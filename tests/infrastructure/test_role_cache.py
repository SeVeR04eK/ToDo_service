"""Tests for RedisRoleCache."""
import pytest
from unittest.mock import AsyncMock, patch
from app.infrastructure.redis.cache import RedisRoleCache
from app.domain.entities import Role


@pytest.mark.unit
class TestRedisRoleCache:
    """Test suite for RedisRoleCache."""

    @pytest.fixture
    def mock_redis_client(self):
        """Create a mock Redis client."""
        client = AsyncMock()
        return client

    @pytest.fixture
    def cache(self, mock_redis_client):
        """Create a RedisRoleCache instance with mocked client."""
        with patch('app.infrastructure.redis.cache.base_cache.get_redis_client', return_value=mock_redis_client):
            return RedisRoleCache()

    @pytest.fixture
    def test_roles(self):
        """Create test roles."""
        return [
            Role(id=1, name="user"),
            Role(id=2, name="admin")
        ]

    def test_get_key(self, cache):
        """Test key generation."""
        key = cache._get_key()
        assert key == "roles"

    async def test_get_roles_success(self, cache, mock_redis_client, test_roles):
        """Test successful roles retrieval."""
        mock_redis_client.get.return_value = '[{"id": 1, "name": "user"}, {"id": 2, "name": "admin"}]'
        
        result = await cache.get_roles()
        
        assert result is not None
        assert len(result) == 2
        assert result[0].id == 1
        assert result[0].name == "user"
        assert result[1].id == 2
        assert result[1].name == "admin"
        mock_redis_client.get.assert_called_once()

    async def test_get_roles_not_found(self, cache, mock_redis_client):
        """Test roles retrieval when not found."""
        mock_redis_client.get.return_value = None
        
        result = await cache.get_roles()
        
        assert result is None
        mock_redis_client.get.assert_called_once()

    async def test_get_roles_deserialize_error(self, cache, mock_redis_client):
        """Test roles retrieval with deserialization error."""
        mock_redis_client.get.return_value = "invalid json"
        
        result = await cache.get_roles()
        
        assert result is None

    async def test_set_roles(self, cache, mock_redis_client, test_roles):
        """Test setting roles in cache."""
        mock_redis_client.set.return_value = True
        
        await cache.set_roles(test_roles, 300)
        
        mock_redis_client.set.assert_called_once()

    async def test_delete_roles(self, cache, mock_redis_client):
        """Test deleting roles from cache."""
        mock_redis_client.delete.return_value = 1
        
        await cache.delete_roles()
        
        mock_redis_client.delete.assert_called_once_with("roles")

    async def test_delete_roles_with_error(self, cache, mock_redis_client):
        """Test deleting roles with error."""
        mock_redis_client.delete.side_effect = Exception("Redis error")
        
        # Should not raise exception, just log error
        await cache.delete_roles()
        
        mock_redis_client.delete.assert_called_once()
