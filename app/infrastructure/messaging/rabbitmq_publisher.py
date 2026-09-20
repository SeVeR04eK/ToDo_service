from __future__ import annotations

import json
import structlog
import aio_pika
from aio_pika import ExchangeType, Message

from app.core.config import settings

logger = structlog.get_logger(__name__)

_publisher: RabbitMQPublisher | None = None


class RabbitMQPublisher:
    """RabbitMQ publisher for sending messages."""

    def __init__(self, url: str):
        self._url = url
        self._connection: aio_pika.abc.AbstractConnection | None = None
        self._channel: aio_pika.abc.AbstractChannel | None = None
        self._exchange: aio_pika.abc.AbstractExchange | None = None

    async def _ensure_connected(self) -> None:
        """Ensure connection to RabbitMQ is established (lazy connection)."""
        if self._exchange is not None:
            return
        
        logger.info("Connecting to RabbitMQ", url=self._url)
        
        self._connection = await aio_pika.connect_robust(self._url)
        self._channel = await self._connection.channel()
        
        # Declare exchange
        self._exchange = await self._channel.declare_exchange(
            settings.rabbitmq_exchange,
            ExchangeType.DIRECT,
            durable=True
        )
        
        # Declare DLX exchange
        await self._channel.declare_exchange(
            settings.rabbitmq_dlx,
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
        await retry_queue.bind(self._exchange, settings.rabbitmq_retry_routing_key)
        
        # Declare main queue
        main_queue = await self._channel.declare_queue(
            settings.rabbitmq_welcome_email_queue,
            durable=True,
            arguments={
                'x-dead-letter-exchange': settings.rabbitmq_dlx,
                'x-dead-letter-routing-key': settings.rabbitmq_welcome_email_routing_key
            }
        )
        await main_queue.bind(self._exchange, settings.rabbitmq_welcome_email_routing_key)
        
        logger.info("RabbitMQ connected and queues declared")

    async def publish_welcome_email(self, username: str, email: str) -> None:
        """Publish welcome email message to RabbitMQ."""
        await self._ensure_connected()
        
        if self._exchange is None:
            logger.warning("RabbitMQ exchange not initialized, skipping message publish")
            return
        
        message_body = {
            "username": username,
            "email": email,
            "type": "welcome_email"
        }
        
        message = Message(
            body=json.dumps(message_body).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            content_type="application/json"
        )
        
        await self._exchange.publish(
            message,
            routing_key=settings.rabbitmq_welcome_email_routing_key
        )
        
        logger.info(
            "Welcome email message published",
            username=username,
            email=email
        )

    async def close(self) -> None:
        """Close RabbitMQ connection."""
        if self._connection and not self._connection.is_closed:
            await self._connection.close()
            logger.info("RabbitMQ connection closed")


def get_rabbitmq_publisher() -> RabbitMQPublisher:
    """Get or create the RabbitMQ publisher (lazy initialization).
    
    Returns:
        RabbitMQPublisher: RabbitMQ publisher instance.
    """
    global _publisher
    if _publisher is None:
        _publisher = RabbitMQPublisher(url=settings.rabbitmq_url)
    return _publisher
