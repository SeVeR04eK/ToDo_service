from pydantic import BaseModel, Field
from typing import Annotated, Optional

class Task(BaseModel):
    title: str
    content: str

class TaskCreate(BaseModel):
    title: Annotated[str, Field(..., min_length=1, max_length=80, title="Title")]
    content: Annotated[str, Field(..., min_length=1, title="Content")]
    category_id: Annotated[Optional[int], Field(default=1, title="Category ID", ge=1)]

class TaskRead(BaseModel):
    id: Annotated[int, Field(title="ID")]
    title: Annotated[str, Field(title="Title")]
    content: Annotated[str, Field(title="Content")]
    category: Annotated[str, Field(title="Category")]
    user_id: Annotated[int, Field( title="User ID")]