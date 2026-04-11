from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean, ForeignKey

from app.models import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False, server_default="1")
    role: Mapped["Role"] = relationship(back_populates="users")

    tasks: Mapped[list["Task"]] = relationship(back_populates="user")