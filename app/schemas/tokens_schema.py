from pydantic import BaseModel, Field
from typing import Annotated


class TokensBase(BaseModel):
    """Base schema for JWT tokens."""
    refresh_token: Annotated[str, Field(title = "Refresh Token")]
    access_token: Annotated[str, Field(title = "Access Token")]
    token_type: Annotated[str, Field(title = "Token Type")]

class TokensResponse(TokensBase):
    """Schema for token response after authentication or refresh."""

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "refresh_token": "example.refresh.token",
                    "access_token": "example.access.token",
                    "token_type": "bearer"
                }
            ]
        }
    }