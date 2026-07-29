from pydantic import BaseModel, Field
from typing import Annotated

class RefreshTokenBase(BaseModel):
    """Base refresh token schema with common fields."""
    refresh_token: Annotated[str, Field(..., title = "Refresh Token")]

class RefreshTokenGet(RefreshTokenBase):
    """Schema for refresh token response."""

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "refresh_token": "example.refresh.token"
                }
            ]
        }
    }