from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import TaskRead, TaskCreate, TaskUpdate
from app.repository import TaskRepository

class TaskService:

    def __init__(self, session: AsyncSession):
        self.repository = TaskRepository(session)

    async def create_task_service(self, task: TaskCreate, user_id: int) -> TaskRead:
        new_task = await self.repository.create_task(task=task, user_id=user_id)

        return TaskRead.model_validate(new_task)

    async def get_tasks_service(self, user_id: int) -> list[TaskRead]:

        tasks = await self.repository.get_tasks(user_id=user_id)

        return [TaskRead.model_validate(task) for task in tasks]

    async def get_task_service(self, task_id: int, user_id: int) -> TaskRead:

        task = await self.repository.get_task(task_id=task_id, user_id=user_id)

        if task is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

        return TaskRead.model_validate(task)

    async def update_task_service(self, task_id: int, task_update: TaskUpdate, user_id: int) -> TaskRead:

        task = await self.repository.get_task(task_id=task_id, user_id=user_id)

        if task is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

        task_updated = await self.repository.update_task(task=task, task_update=task_update)

        return TaskRead.model_validate(task_updated)

    async def delete_task_service(self, task_id: int, user_id: int) -> None:

        task = await self.repository.get_task(task_id=task_id, user_id=user_id)

        if task is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

        await self.repository.delete_task(task_id=task_id, user_id=user_id)
