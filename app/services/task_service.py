from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Optional

from app.schemas import TaskCreate, TaskUpdate, TaskStatus, TasksPagination
from app.repositories import TaskRepository
from app.core.exceptions import TaskNotFoundError

class TaskService:
    """Service layer for task-related business logic."""

    def __init__(self, session: AsyncSession):
        self.repository = TaskRepository(session)

    async def create_task_service(self, task: TaskCreate, user_id: int) -> Dict:
        new_task = await self.repository.create_task(task=task, user_id=user_id)

        return {
            "id": new_task.id,  # type: ignore
            "title": new_task.title,  # type: ignore
            "content": new_task.content,  # type: ignore
            "status": new_task.status,  # type: ignore
            "user_id": new_task.user_id  # type: ignore
        }

    async def get_tasks_service(
            self,
            user_id: int,
            task_status: Optional[TaskStatus],
            pagination: TasksPagination
    ) -> List[Dict]:
        """Get tasks with optional filtering by status, pagination, and sorting."""

        # Route to appropriate repository method based on whether status filter is provided
        if task_status is not None:
            tasks = await self.repository.get_tasks_by_status(
                user_id=user_id,
                task_status=task_status,
                pagination=pagination
            )
        else:
            tasks = await self.repository.get_tasks(
                user_id=user_id,
                pagination=pagination
            )

        return [
            {
                "id": task.id,  # type: ignore
                "title": task.title,  # type: ignore
                "content": task.content,  # type: ignore
                "status": task.status,  # type: ignore
                "user_id": task.user_id  # type: ignore
            }
            for task in tasks
        ]

    async def get_task_service(self, task_id: int, user_id: int) -> Dict:
        """Get a single task by ID."""

        task = await self.repository.get_task(task_id=task_id, user_id=user_id)
        if task is None:
            raise TaskNotFoundError("Task not found")

        return {
            "id": task.id,  # type: ignore
            "title": task.title,  # type: ignore
            "content": task.content,  # type: ignore
            "status": task.status,  # type: ignore
            "user_id": task.user_id  # type: ignore
        }

    async def update_task_service(self, task_id: int, user_id: int, task_update: TaskUpdate) -> Dict:
        """Update a task."""

        task = await self.repository.get_task(task_id=task_id, user_id=user_id)
        if task is None:
            raise TaskNotFoundError("Task not found")

        task_updated = await self.repository.update_task(task=task, task_update=task_update)

        return {
            "id": task_updated.id,  # type: ignore
            "title": task_updated.title,  # type: ignore
            "content": task_updated.content,  # type: ignore
            "status": task_updated.status,  # type: ignore
            "user_id": task_updated.user_id  # type: ignore
        }

    async def delete_task_service(self, task_id: int, user_id: int) -> None:
        """Delete a task."""

        task = await self.repository.get_task(task_id=task_id, user_id=user_id)
        if task is None:
            raise TaskNotFoundError("Task not found")

        await self.repository.delete_task(task_id=task_id, user_id=user_id)
