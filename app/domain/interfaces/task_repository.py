from abc import ABC, abstractmethod

from app.domain.entities import Task
from app.domain.enums import TaskStatus
from app.domain.value_objects import TaskPaginationData, UpdateTaskData

class TaskRepository(ABC):

    @abstractmethod
    async def create_task(
            self,
            title: str,
            content: str,
            status: TaskStatus,
            user_id: int
    ) -> Task: ...

    @abstractmethod
    async def get_tasks(
        self,
        user_id: int,
        pagination: TaskPaginationData,
        task_status: TaskStatus
    ) -> list[Task]: ...

    @abstractmethod
    async def get_task(
        self,
        task_id: int,
        user_id: int,
    ) -> Task | None: ...

    @abstractmethod
    async def update_task(
        self,
        task: Task,
        task_update: UpdateTaskData,
    ) -> Task: ...

    @abstractmethod
    async def delete_task(
        self,
        task_id: int,
        user_id: int,
    ) -> None: ...