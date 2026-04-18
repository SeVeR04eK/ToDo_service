from pydantic import BaseModel, Field
from typing import Annotated

class RoleBase(BaseModel):
    name: str

class RoleRead(RoleBase):
    name: Annotated[str, Field(title="Role Name")]
    id: Annotated[int, Field(default=1, title="Role ID")]

    model_config = {
        "from_attributes": True
    }

class RoleCreate(RoleBase):
    name: Annotated[str, Field(..., title="Role Name")]
