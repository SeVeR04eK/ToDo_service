from enum import Enum

class TaskStatus(str, Enum):
    """Enum for task status values."""
    todo = "todo"
    in_progress = "in_progress"
    done = "done"