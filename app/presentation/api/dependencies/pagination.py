from typing import Optional, Annotated
from fastapi import Query

from app.presentation.api.schemas import TasksPagination

def tasks_pagination(
        limit: Annotated[
            Optional[int],
            Query(title="Limit of tasks", ge=1, le=100)
        ] = None,
        offset: Annotated[
            Optional[int],
            Query(title="Offset for pagination", ge=1, le=10000)
        ] = None,
        from_newest: Annotated[
            Optional[bool],
            Query(title="Sort from newest")
        ] = False
) -> TasksPagination:
    return TasksPagination(limit=limit, offset=offset, from_newest=from_newest)
