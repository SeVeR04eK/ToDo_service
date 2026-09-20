"""Tests for RabbitMQ consumer."""
import pytest
import json
from unittest.mock import patch, MagicMock, AsyncMock
from app.infrastructure.messaging.rabbitmq_consumer import RabbitMQConsumer
from app.infrastructure.services.email_service import EmailService
from app.core.config import settings


@pytest.mark.unit
class TestRabbitMQConsumer:
    """Test suite for RabbitMQ consumer."""

    def test_consumer_initialization(self):
        """Test that RabbitMQConsumer initializes with email service."""
        email_service = MagicMock(spec=EmailService)
        consumer = RabbitMQConsumer(email_service=email_service)
        
        assert consumer.email_service == email_service
        assert consumer._connection is None
        assert consumer._channel is None
        assert consumer._dlx_queue is None

    @pytest.mark.asyncio
    async def test_connect(self):
        """Test that connect establishes connection and sets up queues."""
        email_service = MagicMock(spec=EmailService)
        consumer = RabbitMQConsumer(email_service=email_service)
        
        with patch('app.infrastructure.messaging.rabbitmq_consumer.aio_pika.connect_robust') as mock_connect:
            mock_connection = AsyncMock()
            mock_channel = AsyncMock()
            mock_dlx_exchange = AsyncMock()
            mock_main_exchange = AsyncMock()
            mock_dlx_queue = AsyncMock()
            mock_retry_queue = AsyncMock()
            mock_main_queue = AsyncMock()
            
            mock_connect.return_value = mock_connection
            mock_connection.channel.return_value = mock_channel
            mock_channel.declare_exchange.side_effect = [mock_dlx_exchange, mock_main_exchange]
            mock_channel.declare_queue.side_effect = [mock_dlx_queue, mock_retry_queue, mock_main_queue]
            
            await consumer.connect()
            
            mock_connect.assert_called_once_with(settings.rabbitmq_url)
            mock_connection.channel.assert_called_once()
            mock_channel.set_qos.assert_called_once_with(prefetch_count=10)
            assert consumer._connection == mock_connection
            assert consumer._channel == mock_channel

    @pytest.mark.asyncio
    async def test_start_consuming_without_channel(self):
        """Test that start_consuming returns early when channel is not initialized."""
        email_service = MagicMock(spec=EmailService)
        consumer = RabbitMQConsumer(email_service=email_service)
        
        await consumer.start_consuming()
        
        # Should not raise an error, just return

    @pytest.mark.asyncio
    async def test_process_message_success(self):
        """Test processing a message successfully."""
        email_service = MagicMock(spec=EmailService)
        email_service.send_welcome_email = AsyncMock(return_value=True)
        consumer = RabbitMQConsumer(email_service=email_service)
        
        mock_message = AsyncMock()
        mock_message.body = json.dumps({
            "username": "testuser",
            "email": "test@example.com",
            "type": "welcome_email"
        }).encode()
        mock_message.headers = None
        mock_message.ack = AsyncMock()
        
        await consumer._process_message(mock_message)
        
        email_service.send_welcome_email.assert_called_once_with("testuser", "test@example.com")
        mock_message.ack.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_message_with_retry_count(self):
        """Test processing a message with retry count in headers."""
        email_service = MagicMock(spec=EmailService)
        email_service.send_welcome_email = AsyncMock(return_value=True)
        consumer = RabbitMQConsumer(email_service=email_service)
        
        mock_message = AsyncMock()
        mock_message.body = json.dumps({
            "username": "testuser",
            "email": "test@example.com",
            "type": "welcome_email"
        }).encode()
        mock_message.headers = {"x-retry-count": 2}
        mock_message.ack = AsyncMock()
        
        await consumer._process_message(mock_message)
        
        email_service.send_welcome_email.assert_called_once_with("testuser", "test@example.com")
        mock_message.ack.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_message_unknown_type(self):
        """Test processing a message with unknown type."""
        email_service = MagicMock(spec=EmailService)
        consumer = RabbitMQConsumer(email_service=email_service)
        
        mock_message = AsyncMock()
        mock_message.body = json.dumps({
            "username": "testuser",
            "email": "test@example.com",
            "type": "unknown_type"
        }).encode()
        mock_message.ack = AsyncMock()
        
        await consumer._process_message(mock_message)
        
        email_service.send_welcome_email.assert_not_called()
        mock_message.ack.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_message_email_failure_with_retry(self):
        """Test processing a message when email fails but retries available."""
        email_service = MagicMock(spec=EmailService)
        email_service.send_welcome_email = AsyncMock(return_value=False)
        consumer = RabbitMQConsumer(email_service=email_service)
        
        mock_message = AsyncMock()
        mock_message.body = json.dumps({
            "username": "testuser",
            "email": "test@example.com",
            "type": "welcome_email"
        }).encode()
        mock_message.headers = {"x-retry-count": 1}
        mock_message.reject = AsyncMock()
        
        await consumer._process_message(mock_message)
        
        email_service.send_welcome_email.assert_called_once()
        mock_message.reject.assert_called_once_with(requeue=False)

    @pytest.mark.asyncio
    async def test_process_message_email_failure_max_retries_exceeded(self):
        """Test processing a message when email fails and max retries exceeded."""
        email_service = MagicMock(spec=EmailService)
        email_service.send_welcome_email = AsyncMock(return_value=False)
        consumer = RabbitMQConsumer(email_service=email_service)
        
        mock_message = AsyncMock()
        mock_message.body = json.dumps({
            "username": "testuser",
            "email": "test@example.com",
            "type": "welcome_email"
        }).encode()
        mock_message.headers = {"x-retry-count": 3}
        mock_message.reject = AsyncMock()
        
        await consumer._process_message(mock_message)
        
        email_service.send_welcome_email.assert_called_once()
        mock_message.reject.assert_called_once_with(requeue=False)

    @pytest.mark.asyncio
    async def test_process_message_json_decode_error(self):
        """Test processing a message with invalid JSON."""
        email_service = MagicMock(spec=EmailService)
        consumer = RabbitMQConsumer(email_service=email_service)
        
        mock_message = AsyncMock()
        mock_message.body = b"invalid json"
        mock_message.reject = AsyncMock()
        
        await consumer._process_message(mock_message)
        
        email_service.send_welcome_email.assert_not_called()
        mock_message.reject.assert_called_once_with(requeue=False)

    @pytest.mark.asyncio
    async def test_process_message_unexpected_error(self):
        """Test processing a message when an unexpected error occurs."""
        email_service = MagicMock(spec=EmailService)
        email_service.send_welcome_email = AsyncMock(side_effect=Exception("Unexpected error"))
        consumer = RabbitMQConsumer(email_service=email_service)
        
        mock_message = AsyncMock()
        mock_message.body = json.dumps({
            "username": "testuser",
            "email": "test@example.com",
            "type": "welcome_email"
        }).encode()
        mock_message.reject = AsyncMock()
        
        await consumer._process_message(mock_message)
        
        mock_message.reject.assert_called_once_with(requeue=False)

    @pytest.mark.asyncio
    async def test_close_connection(self):
        """Test closing RabbitMQ connection."""
        email_service = MagicMock(spec=EmailService)
        consumer = RabbitMQConsumer(email_service=email_service)
        
        mock_connection = AsyncMock()
        mock_connection.is_closed = False
        consumer._connection = mock_connection
        
        await consumer.close()
        
        mock_connection.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_connection_when_already_closed(self):
        """Test closing when connection is already closed."""
        email_service = MagicMock(spec=EmailService)
        consumer = RabbitMQConsumer(email_service=email_service)
        
        mock_connection = AsyncMock()
        mock_connection.is_closed = True
        consumer._connection = mock_connection
        
        await consumer.close()
        
        mock_connection.close.assert_not_called()

    @pytest.mark.asyncio
    async def test_close_connection_when_none(self):
        """Test closing when connection is None."""
        email_service = MagicMock(spec=EmailService)
        consumer = RabbitMQConsumer(email_service=email_service)
        
        await consumer.close()
        
        # Should not raise an error
