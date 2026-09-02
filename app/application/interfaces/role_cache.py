from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.entities import Role


class RoleCache(ABC):
    """Abstract cache interface for role-related caching operations."""

    @abstractmethod
    async def get_roles(self) -> Optional[List[Role]]:
        """Get all roles from cache."""
        ...

    @abstractmethod
    async def set_roles(self, roles: List[Role], ttl: int) -> None:
        """Set all roles in cache with TTL."""
        ...

    @abstractmethod
    async def delete_roles(self) -> None:
        """Delete all roles from cache."""
        ...
