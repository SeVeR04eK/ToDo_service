from app.domain.exceptions.base import DomainException


class RoleNotFoundError(DomainException):
    """Raised when a role is not found."""
    pass


class RoleAlreadyExistsError(DomainException):
    """Raised when trying to create a role which is already exists."""
    pass