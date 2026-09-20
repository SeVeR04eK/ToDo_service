from __future__ import annotations

import json
import structlog
import aio_pika
from aio_pika import ExchangeType

from app.core.config import settings
from app.infrastructure.services.email_service import EmailService

logger = structlog.get_logger(__name__)


class RabbitMQConsumer:
    """RabbitMQ consumer for processing welcome email messages with retry logic."""

    def __init__(self, email_service: EmailService):
        self.email_service = email_service
        self._connection: aio_pika.abc.AbstractConnection | None = None
        self._channel: aio_pika.abc.AbstractChannel | None = None
        self._dlx_queue: aio_pika.abc.AbstractQueue | None = None

    async def connect(self) -> None:
        """Establish connection to RabbitMQ and setup queues."""
        logger.info("Connecting RabbitMQ consumer", url=settings.rabbitmq_url)
        
        self._connection = await aio_pika.connect_robust(settings.rabbitmq_url)
        self._channel = await self._connection.channel()
        
        # Set prefetch count to limit unacknowledged messages
        await self._channel.set_qos(prefetch_count=10)
        
        # Declare DLX exchange
        dlx_exchange = await self._channel.declare_exchange(
            settings.rabbitmq_dlx,
            ExchangeType.DIRECT,
            durable=True
        )
        
        # Declare DLQ (Dead Letter Queue)
        self._dlx_queue = await self._channel.declare_queue(
            f"{settings.rabbitmq_welcome_email_queue}_dlq",
            durable=True
        )
        await self._dlx_queue.bind(dlx_exchange, settings.rabbitmq_welcome_email_routing_key)
        
        # Declare main exchange
        main_exchange = await self._channel.declare_exchange(
            settings.rabbitmq_exchange,
            ExchangeType.DIRECT,
            durable=True
        )
        
        # Declare retry queue with TTL
        retry_queue = await self._channel.declare_queue(
            settings.rabbitmq_retry_queue,
            durable=True,
            arguments={
                'x-dead-letter-exchange': settings.rabbitmq_exchange,
                'x-dead-letter-routing-key': settings.rabbitmq_welcome_email_routing_key,
                'x-message-ttl': settings.rabbitmq_retry_ttl_ms
            }
        )
        await retry_queue.bind(main_exchange, settings.rabbitmq_retry_routing_key)
        
        # Declare main queue
        main_queue = await self._channel.declare_queue(
            settings.rabbitmq_welcome_email_queue,
            durable=True,
            arguments={
                'x-dead-letter-exchange': settings.rabbitmq_dlx,
                'x-dead-letter-routing-key': settings.rabbitmq_welcome_email_routing_key
            }
        )
        await main_queue.bind(main_exchange, settings.rabbitmq_welcome_email_routing_key)
        
        logger.info("RabbitMQ consumer connected and queues declared")

    async def start_consuming(self) -> None:
        """Start consuming messages from the welcome email queue."""
        if self._channel is None:
            logger.error("RabbitMQ channel not initialized")
            return
        
        main_queue = await self._channel.get_queue(settings.rabbitmq_welcome_email_queue)
        
        async with main_queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    await self._process_message(message)

    async def _process_message(self, message: aio_pika.abc.AbstractMessage) -> None:
        """Process a single message with retry logic."""
        try:
            body = message.body.decode()
            data = json.loads(body)
            
            username = data.get("username")
            email = data.get("email")
            message_type = data.get("type")
            
            if message_type != "welcome_email":
                logger.warning("Unknown message type", message_type=message_type)
                await message.ack()
                return
            
            retry_count = message.headers.get("x-retry-count", 0) if message.headers else 0
            
            logger.info(
                "Processing welcome email message",
                username=username,
                email=email,
                retry_count=retry_count
            )
            
            # Send email
            success = await self.email_service.send_welcome_email(username, email)
            
            if success:
                logger.info(
                    "Welcome email sent successfully, ACKing message",
                    username=username,
                    email=email
                )
                await message.ack()
            else:
                # Email failed, check retry count
                if retry_count < settings.rabbitmq_max_retries:
                    logger.warning(
                        "Email send failed, retrying",
                        username=username,
                        email=email,
                        retry_count=retry_count,
                        max_retries=settings.rabbitmq_max_retries
                    )
                    # Reject without requeue - message goes to DLX then retry queue
                    await message.reject(requeue=False)
                else:
                    logger.error(
                        "Max retries exceeded, sending to DLQ",
                        username=username,
                        email=email,
                        retry_count=retry_count
                    )
                    # Reject without requeue - message goes to DLQ
                    await message.reject(requeue=False)
                    
        except json.JSONDecodeError as e:
            logger.error("Failed to decode message", error=str(e))
            # Send to DLQ immediately for malformed messages
            await message.reject(requeue=False)
            
        except Exception as e:
            logger.error("Unexpected error processing message", error=str(e))
            # Send to DLQ for unexpected errors
            await message.reject(requeue=False)

    async def close(self) -> None:
        """Close RabbitMQ connection."""
        if self._connection and not self._connection.is_closed:
            await self._connection.close()
            logger.info("RabbitMQ consumer connection closed")
