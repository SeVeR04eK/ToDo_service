from pydantic import BaseModel, Field
from typing import Annotated

class RefreshTokenBase(BaseModel):
    """Base refresh token schema with common fields."""
    refresh_token: Annotated[str, Field(..., title = "Refresh Token")]

class RefreshTokenGet(RefreshTokenBase):
    """Schema for refresh token response."""
    pass