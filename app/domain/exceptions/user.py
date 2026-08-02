from app.domain.exceptions.base import DomainException


class UserNotFoundError(DomainException):
    """Raised when a user is not found."""
    pass


class UsernameAlreadyExistsError(DomainException):
    """Raised when trying to create a user with an existing username."""
    pass


class PermissionDeniedError(DomainException):
    """Raised when a user lacks permission to perform an action."""
    pass