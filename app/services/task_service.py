from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import TaskRead, TaskCreate
from app.repository import TaskRepository

class TaskService:

    def __init__(self, session: AsyncSession):
        self.repository = TaskRepository(session)

    async def create_task_service(self, task: TaskCreate, user_id: int) -> TaskRead:
        new_task = await self.repository.create_task(task=task, user_id=user_id)

        return TaskRead.model_validate(new_task)