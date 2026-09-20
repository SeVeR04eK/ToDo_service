from __future__ import annotations

import json

import aio_pika
import structlog
from aio_pika import ExchangeType

from app.core.config import settings
from app.infrastructure.services.email_service import EmailService


logger = structlog.get_logger(__name__)


class RabbitMQConsumer:

    def __init__(self, email_service: EmailService):
        self.email_service = email_service

        self._connection: aio_pika.abc.AbstractConnection | None = None
        self._channel: aio_pika.abc.AbstractChannel | None = None

        self._main_exchange: aio_pika.abc.AbstractExchange | None = None
        self._dlx_exchange: aio_pika.abc.AbstractExchange | None = None

        self._main_queue: aio_pika.abc.AbstractQueue | None = None
        self._retry_queue: aio_pika.abc.AbstractQueue | None = None
        self._dlq: aio_pika.abc.AbstractQueue | None = None

    async def connect(self) -> None:
        """Connect to RabbitMQ and declare exchanges and queues."""

        logger.info(
            "Connecting RabbitMQ consumer",
            url=settings.rabbitmq_url,
        )

        self._connection = await aio_pika.connect_robust(
            settings.rabbitmq_url
        )

        self._channel = await self._connection.channel()

        # Limit the number of unacknowledged messages
        # processed by this consumer at the same time.
        await self._channel.set_qos(prefetch_count=10)

        self._dlx_exchange = await self._channel.declare_exchange(
            settings.rabbitmq_dlx,
            ExchangeType.DIRECT,
            durable=True,
        )

        self._dlq = await self._channel.declare_queue(
            f"{settings.rabbitmq_welcome_email_queue}_dlq",
            durable=True,
        )

        await self._dlq.bind(
            self._dlx_exchange,
            settings.rabbitmq_welcome_email_routing_key,
        )

        self._main_exchange = await self._channel.declare_exchange(
            settings.rabbitmq_exchange,
            ExchangeType.DIRECT,
            durable=True,
        )

        # RETRY QUEUE
        # The retry queue does not have a consumer.
        # Message arrives here and waits for TTL.
        # When TTL expires RabbitMQ dead-letters the message
        # back to the main exchange

        self._retry_queue = await self._channel.declare_queue(
            settings.rabbitmq_retry_queue,
            durable=True,
            arguments={
                "x-message-ttl": settings.rabbitmq_retry_ttl_ms,
                "x-dead-letter-exchange": settings.rabbitmq_exchange,
                "x-dead-letter-routing-key": (
                    settings.rabbitmq_welcome_email_routing_key
                ),
            },
        )

        # MAIN QUEUE
        # Messages that are permanently rejected are sent to DLX.

        self._main_queue = await self._channel.declare_queue(
            settings.rabbitmq_welcome_email_queue,
            durable=True,
            arguments={
                "x-dead-letter-exchange": settings.rabbitmq_dlx,
                "x-dead-letter-routing-key": (
                    settings.rabbitmq_welcome_email_routing_key
                ),
            },
        )

        await self._main_queue.bind(
            self._main_exchange,
            settings.rabbitmq_welcome_email_routing_key,
        )

        logger.info(
            "RabbitMQ consumer connected",
            main_queue=settings.rabbitmq_welcome_email_queue,
            retry_queue=settings.rabbitmq_retry_queue,
            dlq=f"{settings.rabbitmq_welcome_email_queue}_dlq",
        )

    async def start_consuming(self) -> None:
        """Start consuming messages from the main queue."""

        if self._main_queue is None:
            raise RuntimeError(
                "RabbitMQ consumer is not connected. "
                "Call connect() first."
            )

        logger.info(
            "Starting RabbitMQ consumer",
            queue=settings.rabbitmq_welcome_email_queue,
        )

        async with self._main_queue.iterator() as queue_iter:
            async for message in queue_iter:
                await self._process_message(message)

    async def _process_message(
        self,
        message: aio_pika.abc.AbstractIncomingMessage,
    ) -> None:
        """Process one message."""

        try:

            body = message.body.decode("utf-8")
            data = json.loads(body)

            username = data.get("username")
            email = data.get("email")
            message_type = data.get("type")

            if message_type != "welcome_email":
                logger.warning(
                    "Unknown message type",
                    message_type=message_type,
                )

                # Unknown message is not retryable.
                # Send directly to DLQ.
                await message.reject(requeue=False)
                return

            if not username or not email:
                logger.warning(
                    "Invalid welcome email message",
                    username=username,
                    email=email,
                )

                # Invalid message is not retryable.
                await message.reject(requeue=False)
                return

            headers = message.headers or {}

            retry_count = headers.get(
                "x-retry-count",
                0,
            )

            try:
                retry_count = int(retry_count)
            except (TypeError, ValueError):
                retry_count = 0

            logger.info(
                "Processing welcome email message",
                username=username,
                email=email,
                retry_count=retry_count,
            )

            success = await self.email_service.send_welcome_email(
                username,
                email,
            )

            if success:
                await message.ack()

                logger.info(
                    "Welcome email sent successfully",
                    username=username,
                    email=email,
                    retry_count=retry_count,
                )

                return

            if retry_count < settings.rabbitmq_max_retries:
                next_retry_count = retry_count + 1

                logger.warning(
                    "Welcome email failed, scheduling retry",
                    username=username,
                    email=email,
                    retry_count=retry_count,
                    next_retry_count=next_retry_count,
                    max_retries=settings.rabbitmq_max_retries,
                )

                # Publish a new message to retry queue.
                # We ACK the original message ONLY after the retry
                # message has been successfully published.

                await self._publish_to_retry(
                    message=message,
                    retry_count=next_retry_count,
                )

                await message.ack()

                logger.info(
                    "Message moved to retry queue",
                    username=username,
                    email=email,
                    retry_count=next_retry_count,
                )

                return

            logger.error(
                "Maximum retry count exceeded, sending message to DLQ",
                username=username,
                email=email,
                retry_count=retry_count,
                max_retries=settings.rabbitmq_max_retries,
            )

            await message.reject(requeue=False)


        except json.JSONDecodeError as exc:
            logger.error(
                "Invalid JSON message, sending to DLQ",
                error=str(exc),
            )

            await message.reject(requeue=False)


        except Exception as exc:
            logger.exception(
                "Unexpected error processing RabbitMQ message",
                error=str(exc),
            )

            # Do not requeue unexpected errors.
            # Send the message to DLQ.
            await message.reject(requeue=False)

    async def _publish_to_retry(
        self,
        message: aio_pika.abc.AbstractIncomingMessage,
        retry_count: int,
    ) -> None:
        """Publish a failed message to the retry queue."""

        if self._channel is None:
            raise RuntimeError(
                "RabbitMQ channel is not initialized."
            )

        # Preserve existing headers.
        headers = dict(message.headers or {})

        # Increment our own retry counter.
        headers["x-retry-count"] = retry_count

        retry_message = aio_pika.Message(
            body=message.body,
            headers=headers,
            content_type=message.content_type,
            content_encoding=message.content_encoding,
            correlation_id=message.correlation_id,
            message_id=message.message_id,
            timestamp=message.timestamp,
            type=message.type,
            app_id=message.app_id,
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )

        # Use RabbitMQ's default exchange.
        # The default exchange routes directly to a queue whose
        # name equals the routing key.
        # Therefore:
        #   routing_key = retry_queue_name
        # sends the message directly to retry_queue.

        await self._channel.default_exchange.publish(
            retry_message,
            routing_key=settings.rabbitmq_retry_queue,
        )

        logger.debug(
            "Message published to retry queue",
            retry_queue=settings.rabbitmq_retry_queue,
            retry_count=retry_count,
        )

    async def close(self) -> None:
        """Close RabbitMQ connection."""

        if self._connection is not None:
            if not self._connection.is_closed:
                await self._connection.close()

                logger.info(
                    "RabbitMQ consumer connection closed"
                )

            self._connection = None
            self._channel = None
            self._main_exchange = None
            self._dlx_exchange = None
            self._main_queue = None
            self._retry_queue = None
            self._dlq = None