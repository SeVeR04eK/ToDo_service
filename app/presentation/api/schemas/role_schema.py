from pydantic import BaseModel, Field
from typing import Annotated

class RoleBase(BaseModel):
    """Base role schema with common fields."""
    name: str

class RoleRead(RoleBase):
    """Schema for role response (includes database-generated ID)."""
    name: Annotated[str, Field(title="Role Name")]
    id: Annotated[int, Field(title="Role ID")]

    # Enable ORM mode to allow serialization from SQLAlchemy models
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "name": "user",
                    "id": 1
                }
            ]
        }
    }

class RoleCreate(RoleBase):
    """Schema for creating a new role (request validation)."""
    name: Annotated[str, Field(..., title="Role Name")]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "moderator"
                }
            ]
        }
    }
