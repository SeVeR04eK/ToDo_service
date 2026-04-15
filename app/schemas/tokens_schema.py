from pydantic import BaseModel, Field
from typing import Annotated


class TokensBase(BaseModel):
    refresh_token: Annotated[str, Field(title = "Refresh Token")]
    access_token: Annotated[str, Field(title = "Refresh Token")]
    token_type: Annotated[str, Field(title = "Token Type")]

class TokensResponse(TokensBase):
    pass