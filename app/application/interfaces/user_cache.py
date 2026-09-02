from abc import ABC, abstractmethod
from typing import Optional
from app.domain.entities import User


class UserCache(ABC):
    """Abstract cache interface for user-related caching operations."""

    @abstractmethod
    async def get_user(self, user_id: int) -> Optional[User]:
        """Get user from cache by user ID."""
        ...

    @abstractmethod
    async def set_user(self, user_id: int, user: User, ttl: int) -> None:
        """Set user in cache with TTL."""
        ...

    @abstractmethod
    async def delete_user(self, user_id: int) -> None:
        """Delete user from cache."""
        ...
