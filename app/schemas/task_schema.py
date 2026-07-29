from pydantic import BaseModel, Field
from typing import Annotated, Optional
from app.domain.enums import TaskStatus

class TaskCreate(BaseModel):
    """Schema for creating a new task (request validation)."""
    title: Annotated[str, Field(..., min_length=1, max_length=80, title="Title")]
    content: Annotated[str, Field(..., min_length=1, title="Content")]
    status: Annotated[Optional[TaskStatus], Field(default=TaskStatus.todo, title="Status")]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "example title",
                    "content": "example content",
                    "status": "todo"
                }
            ]
        }
    }

class TaskUpdate(BaseModel):
    """Schema for updating a task (all fields optional for partial updates)."""
    title: Annotated[Optional[str], Field(default=None, min_length=1, max_length=80, title="Title")]
    content: Annotated[Optional[str], Field(default=None, min_length=1, title="Content")]
    status: Annotated[Optional[TaskStatus], Field(default=None, title="Status")]

class TaskRead(BaseModel):
    """Schema for task response (includes database-generated fields)."""
    id: Annotated[int, Field(title="ID")]
    title: Annotated[str, Field(title="Title")]
    content: Annotated[str, Field(title="Content")]
    status: Annotated[TaskStatus, Field(title="Category")]
    user_id: Annotated[int, Field( title="User ID")]

    # Enable ORM mode to allow serialization from SQLAlchemy models
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "title": "example title",
                    "content": "example content",
                    "status": "todo",
                    "user_id": 1
                }
            ]
        }
    }