from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey, Enum

from app.models import Base
from app.domain.enums import TaskStatus

class Task(Base):
    """Task model representing user tasks with status tracking."""
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(80), nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, name="task_status"),
        nullable=False,
        server_default=TaskStatus.todo
    )

    # CASCADE delete ensures tasks are removed when user is deleted
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)