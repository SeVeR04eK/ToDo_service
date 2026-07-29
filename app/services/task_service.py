from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.schemas import TaskCreate, TaskUpdate, TasksPagination
from app.domain.enums import TaskStatus
from app.repositories import TaskRepository
from app.core.exceptions import TaskNotFoundError
from app.domain.entities import Task

class TaskService:
    """Service layer for task-related business logic."""

    def __init__(self, session: AsyncSession):
        self.repository = TaskRepository(session)

    async def create_task_service(self, task: TaskCreate, user_id: int) -> Task:
        return await self.repository.create_task(task=task, user_id=user_id)

    async def get_tasks_service(
            self,
            user_id: int,
            task_status: Optional[TaskStatus],
            pagination: TasksPagination
    ) -> List[Task]:
        """Get tasks with optional filtering by status, pagination, and sorting."""

        # Route to appropriate repository method based on whether status filter is provided
        if task_status is not None:
            return await self.repository.get_tasks_by_status(
                user_id=user_id,
                task_status=task_status,
                pagination=pagination
            )
        else:
            return await self.repository.get_tasks(
                user_id=user_id,
                pagination=pagination
            )

    async def get_task_service(self, task_id: int, user_id: int) -> Task:
        """Get a single task by ID."""

        task = await self.repository.get_task(task_id=task_id, user_id=user_id)
        if task is None:
            raise TaskNotFoundError("Task not found")

        return task

    async def update_task_service(self, task_id: int, user_id: int, task_update: TaskUpdate) -> Task:
        """Update a task."""

        task = await self.repository.get_task(task_id=task_id, user_id=user_id)
        if task is None:
            raise TaskNotFoundError("Task not found")

        return await self.repository.update_task(task=task, task_update=task_update)

    async def delete_task_service(self, task_id: int, user_id: int) -> None:
        """Delete a task."""

        task = await self.repository.get_task(task_id=task_id, user_id=user_id)
        if task is None:
            raise TaskNotFoundError("Task not found")

        await self.repository.delete_task(task_id=task_id, user_id=user_id)
