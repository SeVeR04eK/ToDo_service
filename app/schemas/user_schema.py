from pydantic import BaseModel, Field
from typing import Annotated


class RoleRead(BaseModel):
    name: Annotated[str, Field(title="Role Name")]

    model_config = {
        "from_attributes": True
    }

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    username: Annotated[
        str,
        Field(..., min_length=1, title="Username")
    ]
    password: Annotated[
        str,
        Field(
            ...,
            min_length=8,
            max_length=128,
            title="User Password"
        )
    ]

class UserRead(UserBase):
    username: Annotated[str, Field(title="Username")]
    id: Annotated[int, Field(title="User ID")]
    is_active: Annotated[bool, Field(title="User Active Status")]
    role: RoleRead

    model_config = {
        "from_attributes": True
    }


