from dataclasses import dataclass


@dataclass
class TaskPaginationData:
    limit: int = 100
    offset: int | None = None
    from_newest: bool = False