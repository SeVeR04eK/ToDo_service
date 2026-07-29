from dataclasses import dataclass
from app.domain.enums import TaskStatus


@dataclass(slots=True)
class Task:
    """Domain model for Task."""
    id: int
    title: str
    content: str
    status: TaskStatus
    user_id: int