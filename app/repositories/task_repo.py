from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from sqlalchemy import select, delete

from app.schemas import TaskCreate, TaskUpdate, TasksPagination
from app.domain.enums import TaskStatus
from app.models import Task as TaskORM
from app.domain.entities import Task
from app.domain.mappers import task_from_orm


class TaskRepository:
    """Repository for task-related database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_task(self, task: TaskCreate, user_id: int) -> Task:
        """Create a new task for a user."""

        orm_task = TaskORM(
            title=task.title,
            content=task.content,
            status=task.status,
            user_id=user_id
        )

        self.session.add(orm_task)
        await self.session.commit()
        await self.session.refresh(orm_task)

        return task_from_orm(orm_task)

    async def get_tasks(
            self,
            user_id: int,
            pagination: TasksPagination) -> List[Task]:
        """Get all tasks for a user with optional pagination and sorting."""

        request = select(TaskORM).where(TaskORM.user_id == user_id)

        if pagination.from_newest:
            request = request.order_by(TaskORM.id.desc())
        else:
            request = request.order_by(TaskORM.id.asc())

        if pagination.offset is not None:
            request = request.offset(pagination.offset)

        if pagination.limit is not None:
            request = request.limit(pagination.limit)

        orm_tasks = (await self.session.scalars(request)).all()
        return [task_from_orm(t) for t in orm_tasks]

    async def get_tasks_by_status(
            self,
            user_id: int,
            task_status: TaskStatus,
            pagination: TasksPagination
    ) -> List[Task]:
        """Get tasks for a user filtered by status with optional pagination and sorting."""

        request = select(TaskORM).where(TaskORM.user_id == user_id, TaskORM.status == task_status)

        if pagination.from_newest:
            request = request.order_by(TaskORM.id.desc())
        else:
            request = request.order_by(TaskORM.id.asc())

        if pagination.offset is not None:
            request = request.offset(pagination.offset)

        if pagination.limit is not None:
            request = request.limit(pagination.limit)

        orm_tasks = (await self.session.scalars(request)).all()
        return [task_from_orm(t) for t in orm_tasks]

    async def get_task(self, task_id: int, user_id: int) -> Task | None:
        """Get a single task by ID for a specific user."""

        request = select(TaskORM).where(TaskORM.user_id == user_id, TaskORM.id == task_id)

        orm_task = await self.session.scalar(request)
        return task_from_orm(orm_task) if orm_task else None

    async def update_task(self, task: Task, task_update: TaskUpdate) -> Task:
        """Update an existing task with partial data."""

        # Get the ORM task from the domain task
        request = select(TaskORM).where(TaskORM.id == task.id)
        orm_task = await self.session.scalar(request)
        
        if orm_task is None:
            return task

        # exclude_unset=True only includes fields that were explicitly set
        update_data = task_update.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            # Only set attributes that are not None to avoid NOT NULL constraint violations
            if value is not None:
                setattr(orm_task, key, value)

        await self.session.commit()
        await self.session.refresh(orm_task)

        return task_from_orm(orm_task)

    async def delete_task(self, task_id: int, user_id: int) -> None:
        """Delete a task by ID for a specific user."""

        request = delete(TaskORM).where(TaskORM.user_id == user_id, TaskORM.id == task_id)
        await self.session.execute(request)
        await self.session.commit()