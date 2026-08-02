from dataclasses import dataclass


@dataclass
class TaskPaginationDTO:
    limit: int | None = None
    offset: int | None = None
    from_newest: bool = False