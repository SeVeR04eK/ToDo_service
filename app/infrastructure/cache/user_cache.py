"""Redis implementation of user cache."""

import structlog
from typing import Optional

from app.application.interfaces import UserCache
from app.domain.entities import User
from app.infrastructure.cache.base_cache import BaseRedisCache
from app.infrastructure.redis.serializers import serialize_user, deserialize_user

logger = structlog.get_logger(__name__)


class RedisUserCache(UserCache, BaseRedisCache):
    """Redis implementation of user cache with proper serialization."""

    def _get_key(self, user_id: int) -> str:
        """Generate cache key for user."""
        return f"user:me:{user_id}"

    async def get_user(self, user_id: int) -> Optional[User]:
        """Get user from cache by user ID."""
        key = self._get_key(user_id)
        logger.info("cache_get_attempt", cache_key=key, user_id=user_id)
        data = await self._get(key)
        if data is not None:
            try:
                user = deserialize_user(data)
                logger.info("cache_deserialize_success", cache_key=key, user_id=user_id)
                return user
            except Exception as e:
                logger.error("cache_deserialize_error", cache_key=key, user_id=user_id, error=str(e))
                return None
        logger.info("cache_get_returned_none", cache_key=key, user_id=user_id)
        return None

    async def set_user(self, user_id: int, user: User, ttl: int) -> None:
        """Set user in cache with TTL."""
        key = self._get_key(user_id)
        logger.info("cache_set_attempt", cache_key=key, user_id=user_id, ttl=ttl)
        data = serialize_user(user)
        success = await self._set(key, data, ttl)
        logger.info("cache_set_result", cache_key=key, user_id=user_id, success=success)

    async def delete_user(self, user_id: int) -> None:
        """Delete user from cache."""
        key = self._get_key(user_id)
        logger.info("cache_delete_attempt", cache_key=key, user_id=user_id)
        await self._delete(key)
