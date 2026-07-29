from dataclasses import dataclass
from typing import Optional
from app.domain.entities import Role

@dataclass(slots=True)
class User:
    """Domain model for User."""
    id: int
    username: str
    hashed_password: str
    is_active: bool
    role_id: int
    role: Optional[Role] = None