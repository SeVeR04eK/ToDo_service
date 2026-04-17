from sqlalchemy.ext.asyncio import AsyncSession
from typing import Sequence, Optional
from sqlalchemy import select, delete

from app.schemas import TaskCreate, TaskUpdate, TaskStatus
from app.models import Task


class TaskRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_task(self, task: TaskCreate, user_id: int) -> Task:

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
            limit: Optional[int],
            from_newest: Optional[bool] = False) -> Sequence[Task]:

        request = select(Task).where(Task.user_id == user_id)

        if from_newest:
            request = request.order_by(Task.id.desc())

        if limit is not None:
            request = request.limit(limit)

        return (await self.session.scalars(request)).all()

    async def get_tasks_by_status(
            self,
            user_id: int,
            task_status: TaskStatus,
            limit: Optional[int],
            from_newest: Optional[bool] = False
    ) -> Sequence[Task]:

        request = select(Task).where(Task.user_id == user_id, Task.status == task_status)

        if from_newest:
            request = request.order_by(Task.id.desc())

        if limit is not None:
            request = request.limit(limit)

        return (await self.session.scalars(request)).all()

    async def get_task(self, task_id: int, user_id: int) -> Task:

        request = select(Task).where(Task.user_id == user_id, Task.id == task_id)

        return await self.session.scalar(request)

    async def update_task(self, task: Task, task_update: TaskUpdate) -> Task:

        update_data = task_update.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(task, key, value)

        await self.session.commit()
        await self.session.refresh(task)

        return task

    async def delete_task(self, task_id: int, user_id: int) -> None:

        request = delete(Task).where(Task.user_id == user_id, Task.id == task_id)
        await self.session.execute(request)
        await self.session.commit()