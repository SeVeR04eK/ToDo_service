"""Base cache class with common Redis operations."""

import structlog
from typing import Optional, Any
from abc import ABC

from app.infrastructure.redis.client import get_redis_client
from app.infrastructure.redis.serializers import to_json, from_json
from app.domain.exceptions.redis import SerializationError

logger = structlog.get_logger(__name__)


class BaseRedisCache(ABC):
    """Base class for Redis cache implementations with common functionality."""

    def __init__(self):
        """Initialize cache with Redis client."""
        self._client = get_redis_client()

    async def _get(self, key: str) -> Optional[Any]:
        """Get value from Redis by key."""
        try:
            cached_data = await self._client.get(key)
            if cached_data is not None:
                logger.info("cache_hit", cache_key=key)
                return from_json(cached_data)
            logger.info("cache_miss", cache_key=key)
            return None
        except SerializationError as e:
            logger.error("cache_serialization_error", cache_key=key, error=str(e))
            return None
        except Exception as e:
            logger.error("cache_get_error", cache_key=key, error=str(e))
            return None

    async def _set(self, key: str, value: Any, ttl: int) -> bool:
        """Set value in Redis with TTL."""
        try:
            json_data = to_json(value)
            await self._client.set(key, json_data, ex=ttl)
            logger.info("cache_set", cache_key=key, ttl=ttl)
            return True
        except SerializationError as e:
            logger.error("cache_serialization_error", cache_key=key, error=str(e))
            return False
        except Exception as e:
            logger.error("cache_set_error", cache_key=key, error=str(e))
            return False

    async def _delete(self, key: str) -> bool:
        """Delete value from Redis by key."""
        try:
            await self._client.delete(key)
            logger.debug("cache_delete", cache_key=key)
            return True
        except Exception as e:
            logger.error("cache_delete_error", cache_key=key, error=str(e))
            return False

    async def _delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern. Returns number of keys deleted."""
        try:
            keys = await self._client.keys(pattern)
            if keys:
                await self._client.delete(*keys)
                logger.debug("cache_delete_pattern", pattern=pattern, keys_deleted=len(keys))
                return len(keys)
            return 0
        except Exception as e:
            logger.error("cache_delete_pattern_error", pattern=pattern, error=str(e))
            return 0
