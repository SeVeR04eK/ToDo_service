"""Tests for Redis client."""
import pytest
from unittest.mock import patch, MagicMock
from app.infrastructure.redis.client import get_redis_client
from app.core.config import settings


@pytest.mark.unit
class TestRedisClient:
    """Test suite for Redis client."""

    def test_get_redis_client_initializes_client(self):
        """Test that get_redis_client initializes a new client."""
        # Reset the global client
        import app.infrastructure.redis.client as client_module
        client_module._client = None
        
        with patch('app.infrastructure.redis.client.redis.Redis') as mock_redis:
            mock_instance = MagicMock()
            mock_redis.return_value = mock_instance
            
            client = get_redis_client()
            
            assert client == mock_instance
            mock_redis.assert_called_once()
            # Verify configuration
            call_kwargs = mock_redis.call_args[1]
            assert call_kwargs['host'] == settings.redis_host
            assert call_kwargs['port'] == settings.redis_port
            assert call_kwargs['db'] == settings.redis_db
            assert call_kwargs['decode_responses'] == settings.redis_decode_responses

    def test_get_redis_client_returns_cached_client(self):
        """Test that get_redis_client returns cached client on subsequent calls."""
        # Reset the global client
        import app.infrastructure.redis.client as client_module
        client_module._client = None
        
        with patch('app.infrastructure.redis.client.redis.Redis') as mock_redis:
            mock_instance = MagicMock()
            mock_redis.return_value = mock_instance
            
            # First call
            client1 = get_redis_client()
            # Second call
            client2 = get_redis_client()
            
            assert client1 == client2
            # Redis should only be called once
            mock_redis.assert_called_once()

    def test_get_redis_client_configuration(self):
        """Test that Redis client is configured with fail-fast settings."""
        # Reset the global client
        import app.infrastructure.redis.client as client_module
        client_module._client = None
        
        with patch('app.infrastructure.redis.client.redis.Redis') as mock_redis:
            mock_instance = MagicMock()
            mock_redis.return_value = mock_instance
            
            get_redis_client()
            
            call_kwargs = mock_redis.call_args[1]
            # Verify fail-fast configuration
            assert 'socket_timeout' in call_kwargs
            assert 'socket_connect_timeout' in call_kwargs
            assert 'retry' in call_kwargs
            assert 'health_check_interval' in call_kwargs
            assert call_kwargs['health_check_interval'] == 0
