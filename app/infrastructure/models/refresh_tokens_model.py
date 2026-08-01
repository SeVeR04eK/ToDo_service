from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, ForeignKey
from datetime import datetime

from app.infrastructure.models import Base


class RefreshToken(Base):
    """Refresh token model for JWT token rotation and session management."""
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # CASCADE delete ensures tokens are removed when user is deleted
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    token: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)