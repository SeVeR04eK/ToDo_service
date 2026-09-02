from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.entities import Task
from app.domain.value_objects import Page


class TaskCache(ABC):
    """Abstract cache interface for task-related caching operations."""

    @abstractmethod
    async def get_task(self, user_id: int, task_id: int) -> Optional[Task]:
        """Get single task from cache."""
        ...

    @abstractmethod
    async def set_task(self, user_id: int, task_id: int, task: Task, ttl: int) -> None:
        """Set single task in cache with TTL."""
        ...

    @abstractmethod
    async def delete_task(self, user_id: int, task_id: int) -> None:
        """Delete single task from cache."""
        ...

    @abstractmethod
    async def get_task_list(self, user_id: int, task_status: Optional[str], limit: int, offset: int, from_newest: bool) -> Optional[Page[Task]]:
        """Get task list from cache."""
        ...

    @abstractmethod
    async def set_task_list(self, user_id: int, task_status: Optional[str], limit: int, offset: int, from_newest: bool, page: Page[Task], ttl: int) -> None:
        """Set task list in cache with TTL."""
        ...

    @abstractmethod
    async def delete_task_list(self, user_id: int) -> None:
        """Delete all task lists for a user from cache."""
        ...
