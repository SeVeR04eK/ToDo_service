"""Sliding Window Log rate limiter implementation using Redis Sorted Sets.

This implementation uses Redis Sorted Sets to store request timestamps,
providing exact rate limiting with atomic operations via Lua scripts.
"""

import time
import uuid
import structlog
from typing import Optional

from app.application.interfaces import RateLimiter
from app.infrastructure.redis.client import get_redis_client

logger = structlog.get_logger(__name__)


# Lua script for atomic sliding window log check and update
# This script removes old entries, counts remaining, and adds new entry atomically
SLIDING_WINDOW_LOG_SCRIPT = """
local key = KEYS[1]
local limit = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local now = tonumber(ARGV[3])
local unique_id = ARGV[4]

-- Remove entries older than the window
local old_timestamp = now - window
redis.call('ZREMRANGEBYSCORE', key, 0, old_timestamp)

-- Count remaining entries
local count = redis.call('ZCARD', key)

-- Check if limit is exceeded
if count >= limit then
    return {0, count}
end

-- Add the new request
redis.call('ZADD', key, now, unique_id)
redis.call('EXPIRE', key, window)

-- Return success and new count
return {1, count + 1}
"""


class RedisSlidingWindowLog(RateLimiter):
    """Sliding Window Log rate limiter using Redis Sorted Sets.

    This implementation stores each request timestamp in a Redis Sorted Set,
    allowing for precise rate limiting with exact window boundaries.
    """

    def __init__(self):
        """Initialize the rate limiter with Redis client."""
        self._client = get_redis_client()
        self._script = None

    async def _get_script(self):
        """Lazy load and register the Lua script."""
        if self._script is None:
            self._script = self._client.register_script(SLIDING_WINDOW_LOG_SCRIPT)
        return self._script

    async def is_allowed(
        self,
        key: str,
        limit: int,
        window: int,
    ) -> bool:
        """Check if a request is allowed based on rate limit.

        Args:
            key: Unique identifier for the rate limit bucket
            limit: Maximum number of requests allowed within the window
            window: Time window in seconds

        Returns:
            True if the request is allowed, False if the limit is exceeded
        """
        try:
            script = await self._get_script()
            now = time.time()
            unique_id = str(uuid.uuid4())

            result = await script(
                keys=[key],
                args=[limit, window, now, unique_id],
            )

            allowed = bool(result[0])
            count = result[1]

            logger.debug(
                "rate_limit_check",
                key=key,
                limit=limit,
                window=window,
                allowed=allowed,
                count=count,
                algorithm="sliding_window_log"
            )

            return allowed

        except Exception as e:
            logger.error(
                "rate_limit_error",
                key=key,
                error=str(e),
                algorithm="sliding_window_log"
            )
            # Fail-open for non-critical endpoints, fail-closed for auth will be handled at dependency level
            raise

    async def get_retry_after(
        self,
        key: str,
        window: int,
    ) -> Optional[int]:
        """Get the number of seconds until the next request is allowed.

        For sliding window log, we check the oldest timestamp in the window
        to calculate when it will expire.

        Args:
            key: Unique identifier for the rate limit bucket
            window: Time window in seconds

        Returns:
            Number of seconds until retry, or None if not applicable
        """
        try:
            now = time.time()
            old_timestamp = now - window

            # Get the oldest timestamp in the window
            oldest = await self._client.zrange(key, 0, 0, withscores=True)

            if not oldest:
                return None

            oldest_score = oldest[0][1]
            retry_after = int(oldest_score + window - now)

            if retry_after <= 0:
                return None

            return retry_after

        except Exception as e:
            logger.error(
                "retry_after_error",
                key=key,
                error=str(e),
                algorithm="sliding_window_log"
            )
            return None
