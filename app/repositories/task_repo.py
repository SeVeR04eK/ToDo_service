from sqlalchemy.ext.asyncio import AsyncSession
from typing import Sequence, Optional
from sqlalchemy import select, delete

from app.schemas import TaskCreate, TaskUpdate, TaskStatus, TasksPagination
from app.models import Task


class TaskRepository:
    """Repository for task-related database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_task(self, task: TaskCreate, user_id: int) -> Task:
        """Create a new task for a user."""

        task = Task(
            title=task.title,
            content=task.content,
            status=task.status,
            user_id=user_id
        )

        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)

        return task

    async def get_tasks(
            self,
            user_id: int,
            pagination: TasksPagination) -> Sequence[Task]:
        """Get all tasks for a user with optional pagination and sorting."""

        request = select(Task).where(Task.user_id == user_id)

        if pagination.from_newest:
            request = request.order_by(Task.id.desc())
        else:
            request = request.order_by(Task.id.asc())

        if pagination.offset is not None:
            request = request.offset(pagination.offset)

        if pagination.limit is not None:
            request = request.limit(pagination.limit)

        return (await self.session.scalars(request)).all()

    async def get_tasks_by_status(
            self,
            user_id: int,
            task_status: TaskStatus,
            pagination: TasksPagination
    ) -> Sequence[Task]:
        """Get tasks for a user filtered by status with optional pagination and sorting."""

        request = select(Task).where(Task.user_id == user_id, Task.status == task_status)

        if pagination.from_newest:
            request = request.order_by(Task.id.desc())
        else:
            request = request.order_by(Task.id.asc())

        if pagination.offset is not None:
            request = request.offset(pagination.offset)

        if pagination.limit is not None:
            request = request.limit(pagination.limit)

        return (await self.session.scalars(request)).all()

    async def get_task(self, task_id: int, user_id: int) -> Task | None:
        """Get a single task by ID for a specific user."""

        request = select(Task).where(Task.user_id == user_id, Task.id == task_id)

        return await self.session.scalar(request)

    async def update_task(self, task: Task, task_update: TaskUpdate) -> Task:
        """Update an existing task with partial data."""

        # exclude_unset=True only includes fields that were explicitly set
        update_data = task_update.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            # Only set attributes that are not None to avoid NOT NULL constraint violations
            if value is not None:
                setattr(task, key, value)

        await self.session.commit()
        await self.session.refresh(task)

        return task

    async def delete_task(self, task_id: int, user_id: int) -> None:
        """Delete a task by ID for a specific user."""

        request = delete(Task).where(Task.user_id == user_id, Task.id == task_id)
        await self.session.execute(request)
        await self.session.commit()