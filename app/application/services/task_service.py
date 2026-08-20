import structlog
from typing import List, Optional

from app.domain.enums import TaskStatus
from app.application.dto import CreateTaskDTO, UpdateTaskDTO, TaskPaginationDTO
from app.domain.exceptions import TaskNotFoundError
from app.domain.entities import Task
from app.domain.interfaces import UnitOfWork
from app.domain.value_objects import TaskPaginationData, UpdateTaskData, Page

logger = structlog.get_logger(__name__)

class TaskService:
    """Service layer for task-related business logic."""

    def __init__(self, unit_of_work: UnitOfWork):
        self.unit_of_work = unit_of_work

    async def create_task_service(self, task: CreateTaskDTO, user_id: int) -> Task:

        logger.info(
            "Creating task",
            user_id=user_id,
            title=task.title,
        )
        
        async with self.unit_of_work:
            created_task = await self.unit_of_work.task_repository.create_task(
                title=task.title,
                content=task.content,
                status=task.status,
                user_id=user_id
            )
            
            await self.unit_of_work.commit()
        
        logger.info(
            "Task created",
            task_id=created_task.id,
            user_id=user_id,
            title=created_task.title,
        )
        
        return created_task

    async def get_tasks_service(
            self,
            user_id: int,
            task_status: Optional[TaskStatus],
            pagination: TaskPaginationDTO
    ) -> Page[Task]:
        """Get tasks with optional filtering by status, pagination, and sorting."""


        if pagination.limit is None:
            pagination.limit = 100

        pagination_data = TaskPaginationData(
            limit=pagination.limit,
            offset=pagination.offset,
            from_newest=pagination.from_newest
        )

        return await self.unit_of_work.task_repository.get_tasks(
            user_id=user_id,
            pagination=pagination_data,
            task_status=task_status
        )

    async def get_task_service(self, task_id: int, user_id: int) -> Task:
        """Get a single task by ID."""

        task = await self.unit_of_work.task_repository.get_task(task_id=task_id, user_id=user_id)
        if task is None:
            logger.warning(
                "Task not found",
                task_id=task_id,
                user_id=user_id,
            )
            raise TaskNotFoundError()

        return task

    async def update_task_service(
            self,
            task_id: int,
            user_id: int,
            task_update: UpdateTaskDTO
    ) -> Task:
        """Update a task."""

        logger.info(
            "Updating task",
            task_id=task_id,
            user_id=user_id,
        )
        
        async with self.unit_of_work:
            task = await self.unit_of_work.task_repository.get_task(task_id=task_id, user_id=user_id)
            if task is None:
                logger.warning(
                    "Task not found for update",
                    task_id=task_id,
                    user_id=user_id,
                )
                raise TaskNotFoundError()

            task_update_data = UpdateTaskData(
                title=task_update.title,
                content=task_update.content,
                status=task_update.status,
            )

            updated_task = await self.unit_of_work.task_repository.update_task(task=task, task_update=task_update_data)
            
            await self.unit_of_work.commit()
        
        logger.info(
            "Task updated",
            task_id=updated_task.id,
            user_id=user_id,
        )
        
        return updated_task

    async def delete_task_service(self, task_id: int, user_id: int) -> None:
        """Delete a task."""

        logger.info(
            "Deleting task",
            task_id=task_id,
            user_id=user_id,
        )
        
        async with self.unit_of_work:
            task = await self.unit_of_work.task_repository.get_task(task_id=task_id, user_id=user_id)
            if task is None:
                logger.warning(
                    "Task not found for deletion",
                    task_id=task_id,
                    user_id=user_id,
                )
                raise TaskNotFoundError()

            await self.unit_of_work.task_repository.delete_task(task_id=task_id, user_id=user_id)
            
            await self.unit_of_work.commit()
        
        logger.info(
            "Task deleted",
            task_id=task_id,
            user_id=user_id,
        )
