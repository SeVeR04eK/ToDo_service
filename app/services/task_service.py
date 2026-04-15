from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.schemas import TaskRead, TaskCreate
from app.repository import TaskRepository

class TaskService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_task_service(self, task: TaskCreate, user_id: int) -> TaskRead:
        repository = TaskRepository(session=self.session)
        new_task = await repository.create_task(task=task, user_id=user_id)

        task_category = await repository.get_task_category(task_id=new_task.id)

        if task_category is None:
            raise HTTPException(status_code=404, detail="Something went wrong.")

        return TaskRead(
            id=new_task.id,
            title=new_task.title,
            content=new_task.content,
            category=task_category,
            user_id=new_task.user_id
        )