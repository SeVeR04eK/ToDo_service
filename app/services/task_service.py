from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.schemas import TaskRead, TaskCreate, TaskUpdate, TaskStatus
from app.repositories import TaskRepository

class TaskService:
    """Service layer for task-related business logic."""

    def __init__(self, session: AsyncSession):
        self.repository = TaskRepository(session)

    async def create_task_service(self, task: TaskCreate, user_id: int) -> TaskRead:
        new_task = await self.repository.create_task(task=task, user_id=user_id)

        return TaskRead.model_validate(new_task)

    async def get_tasks_service(
            self,
            user_id: int,
            task_status: Optional[TaskStatus],
            limit: Optional[int],
            offset: Optional[int],
            from_newest: Optional[bool] = False
    ) -> list[TaskRead]:
        """Get tasks with optional filtering by status, pagination, and sorting."""

        # Route to appropriate repository method based on whether status filter is provided
        if task_status is not None:
            tasks = await self.repository.get_tasks_by_status(
                user_id=user_id,
                task_status=task_status,
                limit=limit,
                from_newest=from_newest,
                offset=offset
            )
        else:
            tasks = await self.repository.get_tasks(
                user_id=user_id,
                limit=limit,
                from_newest=from_newest,
                offset=offset
            )

        return [TaskRead.model_validate(task) for task in tasks]

    async def get_task_service(self, task_id: int, user_id: int) -> TaskRead:
        """Get a single task by ID with user ownership validation."""

        task = await self.repository.get_task(task_id=task_id, user_id=user_id)

        # Raise 404 if task doesn't exist or doesn't belong to the user
        if task is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

        return TaskRead.model_validate(task)

    async def update_task_service(self, task_id: int, task_update: TaskUpdate, user_id: int) -> TaskRead:
        """Update a task with user ownership validation."""

        task = await self.repository.get_task(task_id=task_id, user_id=user_id)

        # Raise 404 if task doesn't exist or doesn't belong to the user
        if task is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

        task_updated = await self.repository.update_task(task=task, task_update=task_update)

        return TaskRead.model_validate(task_updated)

    async def delete_task_service(self, task_id: int, user_id: int) -> None:
        """Delete a task with user ownership validation."""

        task = await self.repository.get_task(task_id=task_id, user_id=user_id)

        # Raise 404 if task doesn't exist or doesn't belong to the user
        if task is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

        await self.repository.delete_task(task_id=task_id, user_id=user_id)
