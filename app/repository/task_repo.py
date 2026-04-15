from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from app.schemas import TaskCreate
from app.models import Task, Category


class TaskRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_task(self, task: TaskCreate, user_id: int) -> Task:

        result = await self.session.execute(select(Task.category_id))
        categories = result.scalars().all()


        if task.category_id not in categories:
            raise HTTPException(status_code=404, detail="Category not found.")

        task = Task(
            title=task.title,
            content=task.content,
            category_id=task.category_id,
            user_id=user_id
        )

        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)

        return task

    async def get_task_by_id(self, task_id: int) -> Task:

        request = select(Task).options(selectinload(Task.category.name)).where(Task.id == task_id)
        result = await self.session.execute(request)

        return result.scalar_one_or_none()

    async def get_task_category(self, task_id: int) -> str:

        request = select(Category.name).join(Task.category).where(Task.id == task_id)
        result = await self.session.execute(request)

        return result.scalar_one_or_none()