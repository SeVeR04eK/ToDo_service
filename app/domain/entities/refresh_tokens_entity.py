from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class RefreshToken:
    """Domain model for RefreshToken."""
    id: int
    user_id: int
    token_hash: str
    family_id: str
    expires_at: datetime
    created_at: datetime
    family_created_at: datetime
    revoked_at: Optional[datetime] = None
    replaced_by: Optional[int] = None