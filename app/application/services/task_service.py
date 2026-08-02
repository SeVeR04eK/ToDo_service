from typing import List, Optional

from app.domain.enums import TaskStatus
from app.application.dto import CreateTaskDTO, UpdateTaskDTO, TaskPaginationDTO
from app.domain.exceptions import TaskNotFoundError
from app.domain.entities import Task
from app.domain.interfaces import TaskRepository
from app.domain.value_objects import TaskPaginationData, UpdateTaskData

class TaskService:
    """Service layer for task-related business logic."""

    def __init__(self, repository: TaskRepository):
        self.repository = repository

    async def create_task_service(self, task: CreateTaskDTO, user_id: int) -> Task:

        return await self.repository.create_task(
            title=task.title,
            content=task.content,
            status=task.status,
            user_id=user_id
        )

    async def get_tasks_service(
            self,
            user_id: int,
            task_status: Optional[TaskStatus],
            pagination: TaskPaginationDTO
    ) -> List[Task]:
        """Get tasks with optional filtering by status, pagination, and sorting."""


        pagination_data = TaskPaginationData(
            limit=pagination.limit,
            offset=pagination.offset,
            from_newest=pagination.from_newest
        )

        return await self.repository.get_tasks(
            user_id=user_id,
            pagination=pagination_data,
            task_status=task_status
        )

    async def get_task_service(self, task_id: int, user_id: int) -> Task:
        """Get a single task by ID."""

        task = await self.repository.get_task(task_id=task_id, user_id=user_id)
        if task is None:
            raise TaskNotFoundError()

        return task

    async def update_task_service(
            self,
            task_id: int,
            user_id: int,
            task_update: UpdateTaskDTO
    ) -> Task:
        """Update a task."""

        task = await self.repository.get_task(task_id=task_id, user_id=user_id)
        if task is None:
            raise TaskNotFoundError()

        task_update_data = UpdateTaskData(
            title=task_update.title,
            content=task_update.content,
            status=task_update.status,
        )

        return await self.repository.update_task(task=task, task_update=task_update_data)

    async def delete_task_service(self, task_id: int, user_id: int) -> None:
        """Delete a task."""

        task = await self.repository.get_task(task_id=task_id, user_id=user_id)
        if task is None:
            raise TaskNotFoundError()

        await self.repository.delete_task(task_id=task_id, user_id=user_id)
