from dataclasses import dataclass


@dataclass
class TaskPaginationData:
    limit: int | None = None
    offset: int | None = None
    from_newest: bool = False