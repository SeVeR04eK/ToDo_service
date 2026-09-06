"""Sliding Window Counter rate limiter implementation using Redis.

This implementation uses the sliding window counter algorithm with
previous and current time windows to calculate approximate request counts.
"""

import time
import math
import structlog
from typing import Optional

from app.application.interfaces import RateLimiter
from app.infrastructure.redis.client import get_redis_client

logger = structlog.get_logger(__name__)


# Lua script for atomic sliding window counter check and update
# This script calculates the weighted count from previous and current windows
SLIDING_WINDOW_COUNTER_SCRIPT = """
local key = KEYS[1]
local limit = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local now = tonumber(ARGV[3])
local current_window = math.floor(now / window)
local previous_window = current_window - 1

-- Get counts for current and previous windows
local current_count = tonumber(redis.call('HGET', key, current_window) or 0)
local previous_count = tonumber(redis.call('HGET', key, previous_window) or 0)

-- Calculate the weighted count for the sliding window
local elapsed_in_current = now % window
local weight = elapsed_in_current / window
local weighted_count = previous_count * (1 - weight) + current_count

-- Check if limit is exceeded
if weighted_count >= limit then
    return {0, weighted_count, current_count}
end

-- Increment the current window count
local new_count = current_count + 1
redis.call('HSET', key, current_window, new_count)
redis.call('EXPIRE', key, window * 2)

-- Return success and new weighted count
local new_weighted_count = previous_count * (1 - weight) + new_count
return {1, new_weighted_count, new_count}
"""


class RedisSlidingWindowCounter(RateLimiter):
    """Sliding Window Counter rate limiter using Redis Hash.

    This implementation uses a counter-based approach with weighted
    calculation from previous and current time windows, providing
    approximate but efficient rate limiting.
    """

    def __init__(self):
        """Initialize the rate limiter with Redis client."""
        self._client = get_redis_client()
        self._script = None

    async def _get_script(self):
        """Lazy load and register the Lua script."""
        if self._script is None:
            self._script = self._client.register_script(SLIDING_WINDOW_COUNTER_SCRIPT)
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

            result = await script(
                keys=[key],
                args=[limit, window, now],
            )

            allowed = bool(result[0])
            weighted_count = result[1]
            current_count = result[2]

            logger.debug(
                "rate_limit_check",
                key=key,
                limit=limit,
                window=window,
                allowed=allowed,
                weighted_count=weighted_count,
                current_count=current_count,
                algorithm="sliding_window_counter"
            )

            return allowed

        except Exception as e:
            logger.error(
                "rate_limit_error",
                key=key,
                error=str(e),
                algorithm="sliding_window_counter"
            )
            # Fail-open for non-critical endpoints, fail-closed for auth will be handled at dependency level
            raise

    async def get_retry_after(
        self,
        key: str,
        window: int,
    ) -> Optional[int]:
        """Get the number of seconds until the next request is allowed.

        For sliding window counter, we estimate based on the current window
        and the weighted count.

        Args:
            key: Unique identifier for the rate limit bucket
            window: Time window in seconds

        Returns:
            Number of seconds until retry, or None if not applicable
        """
        try:
            now = time.time()
            current_window = math.floor(now / window)
            elapsed_in_current = now % window

            # Get current window count
            current_count = await self._client.hget(key, current_window)
            if current_count is None:
                return None
            current_count = int(current_count)

            # Get previous window count
            previous_window = current_window - 1
            previous_count = await self._client.hget(key, previous_window)
            if previous_count is None:
                previous_count = 0
            else:
                previous_count = int(previous_count)

            # Calculate weighted count
            weight = elapsed_in_current / window
            weighted_count = previous_count * (1 - weight) + current_count

            # If we're not over limit, no retry needed
            # This is a simplified estimation - in practice we'd need the limit to calculate accurately
            if weighted_count < 1:
                return None

            # Estimate retry time based on when the window will roll over
            retry_after = int(window - elapsed_in_current)
            if retry_after <= 0:
                return None

            return retry_after

        except Exception as e:
            logger.error(
                "retry_after_error",
                key=key,
                error=str(e),
                algorithm="sliding_window_counter"
            )
            return None
