from pydantic import BaseModel, Field, model_validator
from typing import Annotated

from app.schemas.role_schema import RoleRead

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
    password_confirm: Annotated[
        str,
        Field(
            ...,
            min_length=8,
            max_length=128,
            title="User Password Confirm"
        )
    ]

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")
        return self

class UserUpdate(UserBase):
    username: Annotated[
        str,
        Field(default=None, min_length=1, title="Username")
    ]
    password: Annotated[
        str,
        Field(
            default=None,
            min_length=8,
            max_length=128,
            title="User Password"
        )
    ]
    password_confirm: Annotated[
        str,
        Field(
            default=None,
            min_length=8,
            max_length=128,
            title="User Password Confirm"
        )
    ]
    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")
        return self

class UserRead(UserBase):
    username: Annotated[str, Field(title="Username")]
    id: Annotated[int, Field(title="User ID")]
    is_active: Annotated[bool, Field(title="User Active Status")]
    role: RoleRead

    model_config = {
        "from_attributes": True
    }


