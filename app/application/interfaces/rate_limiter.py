from abc import ABC, abstractmethod
from typing import Optional


class RateLimiter(ABC):
    """Abstract rate limiter interface for rate limiting operations."""

    @abstractmethod
    async def is_allowed(
        self,
        key: str,
        limit: int,
        window: int,
    ) -> bool:
        """Check if a request is allowed based on rate limit.

        Args:
            key: Unique identifier for the rate limit bucket (e.g., user_id, IP)
            limit: Maximum number of requests allowed within the window
            window: Time window in seconds

        Returns:
            True if the request is allowed, False if the limit is exceeded
        """
        ...

    @abstractmethod
    async def get_retry_after(
        self,
        key: str,
        window: int,
    ) -> Optional[int]:
        """Get the number of seconds until the next request is allowed.

        Args:
            key: Unique identifier for the rate limit bucket
            window: Time window in seconds

        Returns:
            Number of seconds until retry, or None if not applicable
        """
        ...
