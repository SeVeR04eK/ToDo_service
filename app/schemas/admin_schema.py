from pydantic import BaseModel

class BlockUser(BaseModel):
    is_active: bool