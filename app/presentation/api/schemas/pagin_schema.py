from pydantic import BaseModel, Field
from typing import Annotated, Optional


class PaginationBase(BaseModel):
    """Base schema for JWT tokens."""
    limit: Annotated[
        Optional[int],
        Field(title="Limit of tasks", ge=1, le=100)
    ] = None
    offset: Annotated[
        Optional[int],
        Field(title="Offset for pagination", ge=1, le=10000)
    ] = None

class TasksPagination(PaginationBase):
    from_newest: Annotated[
        Optional[bool],
        Field(title="Sort from newest")] = False
