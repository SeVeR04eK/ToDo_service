from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String

from app.infrastructure.models import Base


class Role(Base):
    """Role model for RBAC (Role-Based Access Control)."""
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    # One-to-many relationship: a role can be assigned to many users
    users: Mapped[list["User"]] = relationship(back_populates="role")