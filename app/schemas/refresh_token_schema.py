from pydantic import BaseModel, Field
from typing import Annotated

class RefreshTokenBase(BaseModel):
    refresh_token: Annotated[str, Field(..., title = "Refresh Token")]

class RefreshTokenGet(RefreshTokenBase):
    pass