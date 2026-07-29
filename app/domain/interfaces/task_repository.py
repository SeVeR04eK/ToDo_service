from abc import ABC, abstractmethod

from app.domain.entities import Task
from app.domain.enums import TaskStatus
from app.schemas import TaskCreate, TaskUpdate, TasksPagination


class TaskRepository(ABC):

    @abstractmethod
    async def create_task(self, task: TaskCreate, user_id: int) -> Task: ...

    @abstractmethod
    async def get_tasks(
        self,
        user_id: int,
        pagination: TasksPagination,
    ) -> list[Task]: ...

    @abstractmethod
    async def get_tasks_by_status(
        self,
        user_id: int,
        task_status: TaskStatus,
        pagination: TasksPagination,
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
        task_update: TaskUpdate,
    ) -> Task: ...

    @abstractmethod
    async def delete_task(
        self,
        task_id: int,
        user_id: int,
    ) -> None: ...