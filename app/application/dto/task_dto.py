from dataclasses import dataclass

from app.domain.enums import TaskStatus


@dataclass
class CreateTaskDTO:
    title: str
    content: str
    status: TaskStatus

@dataclass
class UpdateTaskDTO:
    title: str | None = None
    content: str | None = None
    status: TaskStatus | None = None