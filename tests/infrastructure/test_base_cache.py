"""Tests for BaseRedisCache."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.infrastructure.cache.base_cache import BaseRedisCache
from app.domain.exceptions import SerializationError


@pytest.mark.unit
class TestBaseRedisCache:
    """Test suite for BaseRedisCache."""

    @pytest.fixture
    def mock_redis_client(self):
        """Create a mock Redis client."""
        client = AsyncMock()
        return client

    @pytest.fixture
    def cache(self, mock_redis_client):
        """Create a BaseRedisCache instance with mocked client."""
        with patch('app.infrastructure.cache.base_cache.get_redis_client', return_value=mock_redis_client):
            return BaseRedisCache()

    async def test_get_success(self, cache, mock_redis_client):
        """Test successful get operation."""
        mock_redis_client.get.return_value = '{"key": "value"}'
        
        result = await cache._get("test_key")
        
        assert result == {"key": "value"}
        mock_redis_client.get.assert_called_once_with("test_key")

    async def test_get_cache_miss(self, cache, mock_redis_client):
        """Test get operation with cache miss."""
        mock_redis_client.get.return_value = None
        
        result = await cache._get("test_key")
        
        assert result is None
        mock_redis_client.get.assert_called_once_with("test_key")

    async def test_get_serialization_error(self, cache, mock_redis_client):
        """Test get operation with serialization error."""
        mock_redis_client.get.return_value = "invalid json"
        
        with patch('app.infrastructure.cache.base_cache.from_json', side_effect=SerializationError()):
            result = await cache._get("test_key")
            
            assert result is None

    async def test_get_general_exception(self, cache, mock_redis_client):
        """Test get operation with general exception."""
        mock_redis_client.get.side_effect = Exception("Connection error")
        
        result = await cache._get("test_key")
        
        assert result is None

    async def test_set_success(self, cache, mock_redis_client):
        """Test successful set operation."""
        mock_redis_client.set.return_value = True
        
        result = await cache._set("test_key", {"key": "value"}, 60)
        
        assert result is True
        mock_redis_client.set.assert_called_once()

    async def test_set_serialization_error(self, cache, mock_redis_client):
        """Test set operation with serialization error."""
        class Unserializable:
            pass
        
        with patch('app.infrastructure.cache.base_cache.to_json', side_effect=SerializationError()):
            result = await cache._set("test_key", Unserializable(), 60)
            
            assert result is False

    async def test_set_general_exception(self, cache, mock_redis_client):
        """Test set operation with general exception."""
        mock_redis_client.set.side_effect = Exception("Connection error")
        
        result = await cache._set("test_key", {"key": "value"}, 60)
        
        assert result is False

    async def test_delete_success(self, cache, mock_redis_client):
        """Test successful delete operation."""
        mock_redis_client.delete.return_value = 1
        
        result = await cache._delete("test_key")
        
        assert result is True
        mock_redis_client.delete.assert_called_once_with("test_key")

    async def test_delete_exception(self, cache, mock_redis_client):
        """Test delete operation with exception."""
        mock_redis_client.delete.side_effect = Exception("Connection error")
        
        result = await cache._delete("test_key")
        
        assert result is False

    async def test_delete_pattern_with_keys(self, cache, mock_redis_client):
        """Test delete pattern operation with matching keys."""
        mock_redis_client.keys.return_value = ["key1", "key2", "key3"]
        mock_redis_client.delete.return_value = 3
        
        result = await cache._delete_pattern("test:*")
        
        assert result == 3
        mock_redis_client.keys.assert_called_once_with("test:*")
        mock_redis_client.delete.assert_called_once_with("key1", "key2", "key3")

    async def test_delete_pattern_no_keys(self, cache, mock_redis_client):
        """Test delete pattern operation with no matching keys."""
        mock_redis_client.keys.return_value = []
        
        result = await cache._delete_pattern("test:*")
        
        assert result == 0
        mock_redis_client.keys.assert_called_once_with("test:*")
        mock_redis_client.delete.assert_not_called()

    async def test_delete_pattern_exception(self, cache, mock_redis_client):
        """Test delete pattern operation with exception."""
        mock_redis_client.keys.side_effect = Exception("Connection error")
        
        result = await cache._delete_pattern("test:*")
        
        assert result == 0
