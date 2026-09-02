"""Redis implementation of role cache."""

from typing import Optional, List

from app.application.interfaces import RoleCache
from app.domain.entities import Role
from app.infrastructure.cache.base_cache import BaseRedisCache
from app.infrastructure.redis.serializers import serialize_roles, deserialize_roles


class RedisRoleCache(RoleCache, BaseRedisCache):
    """Redis implementation of role cache with proper serialization."""

    def _get_key(self) -> str:
        """Generate cache key for roles."""
        return "roles"

    async def get_roles(self) -> Optional[List[Role]]:
        """Get all roles from cache."""
        key = self._get_key()
        data = await self._get(key)
        if data is not None:
            try:
                return deserialize_roles(data)
            except Exception:
                return None
        return None

    async def set_roles(self, roles: List[Role], ttl: int) -> None:
        """Set all roles in cache with TTL."""
        key = self._get_key()
        data = serialize_roles(roles)
        await self._set(key, data, ttl)

    async def delete_roles(self) -> None:
        """Delete all roles from cache."""
        key = self._get_key()
        await self._delete(key)
