from pydantic import BaseModel, Field
from typing import Annotated, Optional


class TokensBase(BaseModel):
    """Base schema for JWT tokens."""
    refresh_token: Annotated[str, Field(title = "Refresh Token")]
    access_token: Annotated[str, Field(title = "Access Token")]
    token_type: Annotated[str, Field(title = "Token Type")]
    expires_in: Optional[Annotated[int, Field(title = "Expires In (seconds)")]] = None

class TokensResponse(TokensBase):
    """Schema for token response after authentication or refresh."""

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "refresh_token": "example.refresh.token",
                    "access_token": "example.access.token",
                    "token_type": "bearer",
                    "expires_in": 900
                }
            ]
        }
    }