"""Redis client configuration and initialization.

This module provides a shared Redis client with fail-fast configuration
for graceful handling of Redis unavailability.
"""

import redis.asyncio as redis
from redis.asyncio.retry import Retry
from redis.backoff import NoBackoff

from app.core.config import settings

_client: redis.Redis | None = None


def get_redis_client() -> redis.Redis:
    """Get or create the Redis client (lazy initialization).
    
    The client is configured with short timeouts and fail-fast behavior
    to prevent application hanging when Redis is unavailable.
    
    Returns:
        Redis: Configured Redis client instance.
    """
    global _client
    if _client is None:
        _client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            decode_responses=settings.redis_decode_responses,
            socket_timeout=settings.redis_socket_timeout,  # Short timeout for quick fail when Redis is down
            socket_connect_timeout=settings.redis_socket_connect_timeout,  # Short connection timeout
            retry=Retry(
                NoBackoff(),
                retries=0,
            ),

            health_check_interval=0,
        )
    return _client
