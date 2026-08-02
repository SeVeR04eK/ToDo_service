from app.domain.exceptions.base import DomainException


class InvalidCredentialsError(DomainException):
    """Raised when authentication fails."""
    pass


class InvalidAccessTokenError(DomainException):
    """Raised when an access token is invalid or expired."""
    pass


class InvalidRefreshTokenError(DomainException):
    """Raised when a refresh token is invalid or expired."""
    pass