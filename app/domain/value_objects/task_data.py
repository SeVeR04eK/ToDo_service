from dataclasses import dataclass

from app.domain.enums import TaskStatus


@dataclass
class UpdateTaskData:
    title: str | None = None
    content: str | None = None
    status: TaskStatus | None = None