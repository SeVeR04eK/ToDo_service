"""Tests for RedisUserCache."""
import pytest
from unittest.mock import AsyncMock, patch
from app.infrastructure.cache.user_cache import RedisUserCache
from app.domain.entities import User, Role


@pytest.mark.unit
class TestRedisUserCache:
    """Test suite for RedisUserCache."""

    @pytest.fixture
    def mock_redis_client(self):
        """Create a mock Redis client."""
        client = AsyncMock()
        return client

    @pytest.fixture
    def cache(self, mock_redis_client):
        """Create a RedisUserCache instance with mocked client."""
        with patch('app.infrastructure.cache.base_cache.get_redis_client', return_value=mock_redis_client):
            return RedisUserCache()

    @pytest.fixture
    def test_user(self):
        """Create a test user."""
        role = Role(id=1, name="user")
        return User(
            id=1,
            username="testuser",
            hashed_password="hashed123",
            is_active=True,
            role_id=1,
            role=role
        )

    def test_get_key(self, cache):
        """Test key generation."""
        key = cache._get_key(123)
        assert key == "user:me:123"

    async def test_get_user_success(self, cache, mock_redis_client, test_user):
        """Test successful user retrieval."""
        serialized_user = {
            "id": 1,
            "username": "testuser",
            "hashed_password": "hashed123",
            "is_active": True,
            "role_id": 1,
            "role": {"id": 1, "name": "user"}
        }
        mock_redis_client.get.return_value = '{"id": 1, "username": "testuser", "hashed_password": "hashed123", "is_active": true, "role_id": 1, "role": {"id": 1, "name": "user"}}'
        
        result = await cache.get_user(1)
        
        assert result is not None
        assert result.id == 1
        assert result.username == "testuser"
        mock_redis_client.get.assert_called_once()

    async def test_get_user_not_found(self, cache, mock_redis_client):
        """Test user retrieval when not found."""
        mock_redis_client.get.return_value = None
        
        result = await cache.get_user(999)
        
        assert result is None
        mock_redis_client.get.assert_called_once()

    async def test_get_user_deserialize_error(self, cache, mock_redis_client):
        """Test user retrieval with deserialization error."""
        mock_redis_client.get.return_value = "invalid json"
        
        result = await cache.get_user(1)
        
        assert result is None

    async def test_set_user(self, cache, mock_redis_client, test_user):
        """Test setting user in cache."""
        mock_redis_client.set.return_value = True
        
        await cache.set_user(1, test_user, 300)
        
        mock_redis_client.set.assert_called_once()

    async def test_delete_user(self, cache, mock_redis_client):
        """Test deleting user from cache."""
        mock_redis_client.delete.return_value = 1
        
        await cache.delete_user(1)
        
        mock_redis_client.delete.assert_called_once_with("user:me:1")

    async def test_delete_user_with_error(self, cache, mock_redis_client):
        """Test deleting user with error."""
        mock_redis_client.delete.side_effect = Exception("Redis error")
        
        # Should not raise exception, just log error
        await cache.delete_user(1)
        
        mock_redis_client.delete.assert_called_once()
