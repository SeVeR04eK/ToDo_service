from pydantic import BaseModel


class TokensBase(BaseModel):
    refresh_token: str
    access_token: str
    token_type: str

class TokensResponse(TokensBase):
    pass