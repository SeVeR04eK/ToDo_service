from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from sqlalchemy import select, delete, func

from app.domain.enums import TaskStatus
from app.domain.value_objects import TaskPaginationData, UpdateTaskData, Page
from app.infrastructure.models import Task as TaskORM
from app.domain.entities import Task
from app.infrastructure.mappers import task_from_orm
from app.domain.interfaces import TaskRepository


class SQLAlchemyTaskRepository(TaskRepository):
    """Repository for task-related database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_task(
            self,
            title: str,
            content: str,
            status: TaskStatus,
            user_id: int) -> Task:
        """Create a new task for a user."""

        orm_task = TaskORM(
            title=title,
            content=content,
            status=status,
            user_id=user_id
        )

        self.session.add(orm_task)
        await self.session.commit()
        await self.session.refresh(orm_task)

        return task_from_orm(orm_task)

    async def get_tasks(
            self,
            user_id: int,
            pagination: TaskPaginationData,
            task_status: TaskStatus | None
    ) -> Page[Task]:
        """Get all tasks for a user with optional pagination and sorting."""

        # Build base query
        base_query = select(TaskORM).where(TaskORM.user_id == user_id)

        if task_status is not None:
            base_query = base_query.where(TaskORM.status == task_status)

        # Count total items
        count_query = select(func.count()).select_from(base_query.subquery())
        total_items = await self.session.scalar(count_query)

        # Apply ordering
        query = base_query.order_by(
            TaskORM.id.desc() if pagination.from_newest else TaskORM.id.asc()
        )

        # Calculate page and page_size from offset/limit
        limit = pagination.limit if pagination.limit is not None else 10
        offset = pagination.offset if pagination.offset is not None else 0
        page = (offset // limit) + 1 if limit > 0 else 1

        # Apply pagination
        query = query.offset(offset).limit(limit)

        orm_tasks = (await self.session.scalars(query)).all()
        tasks = [task_from_orm(task) for task in orm_tasks]

        return Page.create(
            items=tasks,
            page=page,
            page_size=limit,
            total_items=total_items or 0
        )

    async def get_task(self, task_id: int, user_id: int) -> Task | None:
        """Get a single task by ID for a specific user."""

        request = select(TaskORM).where(TaskORM.user_id == user_id, TaskORM.id == task_id)

        orm_task = await self.session.scalar(request)
        return task_from_orm(orm_task) if orm_task else None

    async def update_task(self, task: Task, task_update: UpdateTaskData) -> Task:
        """Update an existing task with partial data."""

        # Get the ORM task from the domain task
        request = select(TaskORM).where(TaskORM.id == task.id)
        orm_task = await self.session.scalar(request)
        
        if orm_task is None:
            return task

        # exclude_unset=True only includes fields that were explicitly set
        update_data = {
            key: value
            for key, value in vars(task_update).items()
            if value is not None
        }

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