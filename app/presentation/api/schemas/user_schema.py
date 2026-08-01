from pydantic import BaseModel, Field, model_validator
from typing import Annotated


class UserBase(BaseModel):
    """Base user schema with common fields."""
    username: str

class UserRole(BaseModel):
    """Nested schema for user role information in responses."""
    name: Annotated[str, Field(title="Role Name")]

    model_config = {
        "from_attributes": True
    }

class UserCreate(UserBase):
    """Schema for user registration with password confirmation."""
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

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "user",
                    "password": "user12345",
                    "password_confirm": "user12345"
                }
            ]
        }
    }

    @model_validator(mode="after")
    def passwords_match(self):
        """Validate that password and password confirmation match."""
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")
        return self

class UserUpdate(UserBase):
    """Schema for updating user profile (all fields optional)."""
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
        """Validate that password and password confirmation match."""
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")
        return self

    model_config = {"extra": "ignore"}

class UserRead(UserBase):
    """Schema for user response (includes database-generated fields)."""
    username: Annotated[str, Field(title="Username")]
    id: Annotated[int, Field(title="User ID")]
    is_active: Annotated[bool, Field(title="User Active Status")]
    role: UserRole

    # Enable ORM mode to allow serialization from SQLAlchemy models
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "username": "user",
                    "id": 1,
                    "is_active": True,
                    "role": {
                        "name": "user"
                    }
                }
            ]
        }
    }


