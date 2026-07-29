from dataclasses import dataclass


@dataclass(slots=True)
class Role:
    """Domain model for Role."""
    id: int
    name: str