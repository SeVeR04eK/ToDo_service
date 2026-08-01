from dataclasses import dataclass


@dataclass(slots=True)
class Tokens:
    """DTO for authentication tokens."""
    refresh_token: str
    access_token: str
    token_type: str