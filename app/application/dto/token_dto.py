from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class Tokens:
    """DTO for authentication tokens."""
    refresh_token: str
    access_token: str
    token_type: str
    expires_in: Optional[int] = None