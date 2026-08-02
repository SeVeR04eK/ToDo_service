from app.domain.exceptions.base import DomainException


class TaskNotFoundError(DomainException):
    """Raised when a task is not found."""
    pass
