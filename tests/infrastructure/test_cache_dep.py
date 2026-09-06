"""Tests for cache dependencies."""
import pytest
from unittest.mock import patch
from app.presentation.api.dependencies.cache_dep import (
    get_user_cache,
    get_task_cache,
    get_role_cache
)
from app.infrastructure.redis.cache import RedisUserCache, RedisTaskCache, RedisRoleCache
from app.application.interfaces import UserCache, TaskCache, RoleCache


@pytest.mark.unit
class TestCacheDependencies:
    """Test suite for cache dependency functions."""

    def test_get_user_cache_returns_correct_type(self):
        """Test that get_user_cache returns RedisUserCache instance."""
        with patch('app.infrastructure.redis.cache.base_cache.get_redis_client'):
            result = get_user_cache()
            assert isinstance(result, RedisUserCache)
            assert isinstance(result, UserCache)

    def test_get_task_cache_returns_correct_type(self):
        """Test that get_task_cache returns RedisTaskCache instance."""
        with patch('app.infrastructure.redis.cache.base_cache.get_redis_client'):
            result = get_task_cache()
            assert isinstance(result, RedisTaskCache)
            assert isinstance(result, TaskCache)

    def test_get_role_cache_returns_correct_type(self):
        """Test that get_role_cache returns RedisRoleCache instance."""
        with patch('app.infrastructure.redis.cache.base_cache.get_redis_client'):
            result = get_role_cache()
            assert isinstance(result, RedisRoleCache)
            assert isinstance(result, RoleCache)
