"""Redis implementation of task cache."""

from typing import Optional

from app.application.interfaces import TaskCache
from app.domain.entities import Task
from app.domain.value_objects import Page
from app.infrastructure.redis.cache.base_cache import BaseRedisCache
from app.infrastructure.redis.serializers import (
    serialize_task,
    deserialize_task,
    serialize_task_list,
    deserialize_task_list
)


class RedisTaskCache(TaskCache, BaseRedisCache):
    """Redis implementation of task cache with proper serialization."""

    @staticmethod
    def _get_task_key(user_id: int, task_id: int) -> str:
        """Generate cache key for single task."""
        return f"task:{user_id}:{task_id}"

    @staticmethod
    def _get_task_list_key(user_id: int, task_status: Optional[str], limit: int, offset: int, from_newest: bool) -> str:
        """Generate cache key for task list."""
        status_part = f"status:{task_status}" if task_status else "status:all"
        return f"tasks:user:{user_id}:{status_part}:limit:{limit}:offset:{offset}:newest:{from_newest}"

    async def get_task(self, user_id: int, task_id: int) -> Optional[Task]:
        """Get single task from cache."""
        key = self._get_task_key(user_id, task_id)
        data = await self._get(key)
        if data is not None:
            try:
                return deserialize_task(data)
            except Exception:
                return None
        return None

    async def set_task(self, user_id: int, task_id: int, task: Task, ttl: int) -> None:
        """Set single task in cache with TTL."""
        key = self._get_task_key(user_id, task_id)
        data = serialize_task(task)
        await self._set(key, data, ttl)

    async def delete_task(self, user_id: int, task_id: int) -> None:
        """Delete single task from cache."""
        key = self._get_task_key(user_id, task_id)
        await self._delete(key)

    async def get_task_list(self, user_id: int, task_status: Optional[str], limit: int, offset: int, from_newest: bool) -> Optional[Page[Task]]:
        """Get task list from cache."""
        key = self._get_task_list_key(user_id, task_status, limit, offset, from_newest)
        data = await self._get(key)
        if data is not None:
            try:
                tasks, page_metadata = deserialize_task_list(data)
                return Page(
                    items=tasks,
                    page=page_metadata["page"],
                    page_size=page_metadata["page_size"],
                    total_items=page_metadata["total_items"],
                    total_pages=page_metadata["total_pages"],
                    has_next=page_metadata["has_next"],
                    has_previous=page_metadata["has_previous"]
                )
            except Exception:
                return None
        return None

    async def set_task_list(self, user_id: int, task_status: Optional[str], limit: int, offset: int, from_newest: bool, page: Page[Task], ttl: int) -> None:
        """Set task list in cache with TTL."""
        key = self._get_task_list_key(user_id, task_status, limit, offset, from_newest)
        page_metadata = {
            "page": page.page,
            "page_size": page.page_size,
            "total_items": page.total_items,
            "total_pages": page.total_pages,
            "has_next": page.has_next,
            "has_previous": page.has_previous
        }
        data = serialize_task_list(page.items, page_metadata)
        await self._set(key, data, ttl)

    async def delete_task_list(self, user_id: int) -> None:
        """Delete all task lists for a user from cache."""
        pattern = f"tasks:user:{user_id}:*"
        await self._delete_pattern(pattern)
