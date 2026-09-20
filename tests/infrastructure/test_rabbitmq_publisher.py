"""Tests for RabbitMQ publisher."""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from app.infrastructure.messaging.rabbitmq_publisher import RabbitMQPublisher, get_rabbitmq_publisher
from app.core.config import settings


@pytest.mark.unit
class TestRabbitMQPublisher:
    """Test suite for RabbitMQ publisher."""

    def test_publisher_initialization(self):
        """Test that RabbitMQPublisher initializes with URL."""
        url = "amqp://guest:guest@localhost:5672/"
        publisher = RabbitMQPublisher(url=url)
        
        assert publisher._url == url
        assert publisher._connection is None
        assert publisher._channel is None
        assert publisher._exchange is None

    @pytest.mark.asyncio
    async def test_ensure_connected_first_call(self):
        """Test that _ensure_connected establishes connection on first call."""
        url = "amqp://guest:guest@localhost:5672/"
        publisher = RabbitMQPublisher(url=url)
        
        with patch('app.infrastructure.messaging.rabbitmq_publisher.aio_pika.connect_robust') as mock_connect:
            mock_connection = AsyncMock()
            mock_channel = AsyncMock()
            mock_exchange = AsyncMock()
            mock_dlx_exchange = AsyncMock()
            mock_retry_queue = AsyncMock()
            mock_main_queue = AsyncMock()
            
            mock_connection.channel.return_value = mock_channel
            mock_channel.declare_exchange.side_effect = [mock_exchange, mock_dlx_exchange]
            mock_channel.declare_queue.side_effect = [mock_retry_queue, mock_main_queue]
            mock_connect.return_value = mock_connection
            
            await publisher._ensure_connected()
            
            mock_connect.assert_called_once_with(url)
            mock_connection.channel.assert_called_once()
            assert publisher._exchange == mock_exchange

    @pytest.mark.asyncio
    async def test_ensure_connected_idempotent(self):
        """Test that _ensure_connected doesn't reconnect if already connected."""
        url = "amqp://guest:guest@localhost:5672/"
        publisher = RabbitMQPublisher(url=url)
        publisher._exchange = MagicMock()
        
        with patch('app.infrastructure.messaging.rabbitmq_publisher.aio_pika.connect_robust') as mock_connect:
            await publisher._ensure_connected()
            
            # Should not connect since exchange is already set
            mock_connect.assert_not_called()

    @pytest.mark.asyncio
    async def test_publish_welcome_email(self):
        """Test publishing welcome email message."""
        url = "amqp://guest:guest@localhost:5672/"
        publisher = RabbitMQPublisher(url=url)
        
        mock_exchange = AsyncMock()
        publisher._exchange = mock_exchange
        
        await publisher.publish_welcome_email(username="testuser", email="test@example.com")
        
        mock_exchange.publish.assert_called_once()
        call_args = mock_exchange.publish.call_args
        assert call_args[1]['routing_key'] == settings.rabbitmq_welcome_email_routing_key

    @pytest.mark.asyncio
    async def test_publish_welcome_email_without_connection(self):
        """Test that publish skips when exchange is not initialized."""
        url = "amqp://guest:guest@localhost:5672/"
        publisher = RabbitMQPublisher(url=url)
        
        with patch('app.infrastructure.messaging.rabbitmq_publisher.aio_pika.connect_robust') as mock_connect:
            mock_connection = AsyncMock()
            mock_channel = AsyncMock()
            mock_exchange = AsyncMock()
            mock_dlx_exchange = AsyncMock()
            mock_retry_queue = AsyncMock()
            mock_main_queue = AsyncMock()
            
            mock_connection.channel.return_value = mock_channel
            mock_channel.declare_exchange.side_effect = [mock_exchange, mock_dlx_exchange]
            mock_channel.declare_queue.side_effect = [mock_retry_queue, mock_main_queue]
            mock_connect.return_value = mock_connection
            mock_exchange.publish = AsyncMock()
            
            await publisher.publish_welcome_email(username="testuser", email="test@example.com")
            
            # Should connect and then publish
            mock_connect.assert_called_once()
            mock_exchange.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_welcome_email_exchange_none_after_ensure_connected(self):
        """Test that publish logs warning when exchange is None after _ensure_connected."""
        url = "amqp://guest:guest@localhost:5672/"
        publisher = RabbitMQPublisher(url=url)
        
        with patch('app.infrastructure.messaging.rabbitmq_publisher.aio_pika.connect_robust') as mock_connect:
            mock_connection = AsyncMock()
            mock_channel = AsyncMock()
            mock_connect.return_value = mock_connection
            mock_connection.channel.return_value = mock_channel
            # Simulate exchange being None after connection
            mock_channel.declare_exchange.return_value = None
            
            await publisher.publish_welcome_email(username="testuser", email="test@example.com")
            
            # Should connect but not publish
            mock_connect.assert_called_once()
            # Exchange should be None
            assert publisher._exchange is None

    @pytest.mark.asyncio
    async def test_close_connection(self):
        """Test closing RabbitMQ connection."""
        url = "amqp://guest:guest@localhost:5672/"
        publisher = RabbitMQPublisher(url=url)
        
        mock_connection = AsyncMock()
        mock_connection.is_closed = False
        publisher._connection = mock_connection
        
        await publisher.close()
        
        mock_connection.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_connection_when_already_closed(self):
        """Test closing when connection is already closed."""
        url = "amqp://guest:guest@localhost:5672/"
        publisher = RabbitMQPublisher(url=url)
        
        mock_connection = AsyncMock()
        mock_connection.is_closed = True
        publisher._connection = mock_connection
        
        await publisher.close()
        
        mock_connection.close.assert_not_called()

    @pytest.mark.asyncio
    async def test_close_connection_when_none(self):
        """Test closing when connection is None."""
        url = "amqp://guest:guest@localhost:5672/"
        publisher = RabbitMQPublisher(url=url)
        
        await publisher.close()
        
        # Should not raise an error

    def test_get_rabbitmq_publisher_initializes_publisher(self):
        """Test that get_rabbitmq_publisher initializes a new publisher."""
        # Reset the global publisher
        import app.infrastructure.messaging.rabbitmq_publisher as publisher_module
        publisher_module._publisher = None
        
        with patch('app.infrastructure.messaging.rabbitmq_publisher.RabbitMQPublisher') as mock_publisher_class:
            mock_instance = MagicMock()
            mock_publisher_class.return_value = mock_instance
            
            publisher = get_rabbitmq_publisher()
            
            assert publisher == mock_instance
            mock_publisher_class.assert_called_once_with(url=settings.rabbitmq_url)

    def test_get_rabbitmq_publisher_returns_cached_publisher(self):
        """Test that get_rabbitmq_publisher returns cached publisher on subsequent calls."""
        # Reset the global publisher
        import app.infrastructure.messaging.rabbitmq_publisher as publisher_module
        publisher_module._publisher = None
        
        with patch('app.infrastructure.messaging.rabbitmq_publisher.RabbitMQPublisher') as mock_publisher_class:
            mock_instance = MagicMock()
            mock_publisher_class.return_value = mock_instance
            
            # First call
            publisher1 = get_rabbitmq_publisher()
            # Second call
            publisher2 = get_rabbitmq_publisher()
            
            assert publisher1 == publisher2
            # Publisher class should only be called once
            mock_publisher_class.assert_called_once()
