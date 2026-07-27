"""Domain exceptions for the application.

These exceptions are raised by the service layer and caught by the router layer
to convert them into appropriate HTTP responses.
"""


class DomainException(Exception):
    """Base class for all domain exceptions."""
    pass


class AuthenticationError(DomainException):
    """Raised when authentication fails."""
    pass


class InvalidTokenError(DomainException):
    """Raised when a token is invalid or expired."""
    pass


class UserNotFoundError(DomainException):
    """Raised when a user is not found."""
    pass


class UsernameAlreadyExistsError(DomainException):
    """Raised when trying to create a user with an existing username."""
    pass


class RoleNotFoundError(DomainException):
    """Raised when a role is not found."""
    pass


class PermissionDeniedError(DomainException):
    """Raised when a user lacks permission to perform an action."""
    pass


class TaskNotFoundError(DomainException):
    """Raised when a task is not found."""
    pass
