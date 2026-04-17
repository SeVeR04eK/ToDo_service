from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import TaskCreate
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