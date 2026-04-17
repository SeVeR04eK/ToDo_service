from pydantic import BaseModel, Field
from typing import Annotated, Optional
from enum import Enum

class Task(BaseModel):
    title: str
    content: str
    status: TaskStatus

class TaskStatus(str, Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"

class TaskCreate(BaseModel):
    title: Annotated[str, Field(..., min_length=1, max_length=80, title="Title")]
    content: Annotated[str, Field(..., min_length=1, title="Content")]
    status: Annotated[Optional[TaskStatus], Field(default=TaskStatus.todo, title="Status")]

class TaskUpdate(BaseModel):
    title: Annotated[Optional[str], Field(default=None, min_length=1, max_length=80, title="Title")]
    content: Annotated[Optional[str], Field(default=None, min_length=1, title="Content")]
    status: Annotated[Optional[TaskStatus], Field(default=None, title="Status")]

class TaskRead(BaseModel):
    id: Annotated[int, Field(title="ID")]
    title: Annotated[str, Field(title="Title")]
    content: Annotated[str, Field(title="Content")]
    status: Annotated[TaskStatus, Field(title="Category")]
    user_id: Annotated[int, Field( title="User ID")]

    model_config = {
        "from_attributes": True
    }