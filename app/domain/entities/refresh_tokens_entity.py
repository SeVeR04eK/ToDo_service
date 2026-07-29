from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class RefreshToken:
    """Domain model for RefreshToken."""
    id: int
    user_id: int
    token: str
    expires_at: datetime