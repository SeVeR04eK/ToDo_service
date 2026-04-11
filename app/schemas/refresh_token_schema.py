from pydantic import BaseModel

class RefreshTokenBase(BaseModel):
    refresh_token: str

class RefreshTokenGet(RefreshTokenBase):
    pass