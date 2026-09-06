from fastapi import Request
from fastapi.responses import JSONResponse
from typing import Type, Tuple, Dict
import structlog

from app.domain.exceptions import *
from app.domain.exceptions.base import DomainException

logger = structlog.get_logger(__name__)


ERROR_MAP: Dict[Type[DomainException], Tuple[int, str, str]] = {
    UserNotFoundError: (404, "USER_NOT_FOUND", "User not found"),
    UsernameAlreadyExistsError: (409, "USERNAME_ALREADY_EXISTS", "Username already exists"),
    PermissionDeniedError: (403, "NOT_ENOUGH_PERMISSIONS", "Not enough permissions"),
    RoleNotFoundError: (404, "ROLE_NOT_FOUND", "Role not found"),
    RoleAlreadyExistsError: (409, "ROLE_ALREADY_EXISTS", "Role already exists"),
    TaskNotFoundError: (404, "TASK_NOT_FOUND", "Task not found"),
    InvalidCredentialsError: (401, "INVALID_CREDENTIALS", "Invalid credentials"),
    InvalidAccessTokenError: (401, "INVALID_ACCESS_TOKEN", "Invalid access token"),
    InvalidRefreshTokenError: (401, "INVALID_REFRESH_TOKEN", "Invalid refresh token"),
    InvalidPaginationParameters: (400, "INVALID_PAGINATION_PARAMETERS", "Pagination parameters are not allowed when filtering by username"),
    WeakPasswordError: (400, "WEAK_PASSWORD", "Password is too weak"),
    PasswordNotMatchError: (400, "PASSWORD_NOT_MATCH", "Password does not match"),
    SerializationError: (400, "SERIALIZATION_ERROR", "Failed to serialize or deserialize data"),
    RateLimitExceededError: (429, "RATE_LIMIT_EXCEEDED", "Rate limit exceeded"),
}


async def domain_exception_handler(_request: Request, exc: DomainException):
    status_code, code, message = ERROR_MAP.get(type(exc), (400, "Domain error"))

    logger.warning(
        "Domain exception occurred",
        exception_type=type(exc).__name__,
        status_code=status_code,
        code=code,
        message=message
    )

    headers = {}
    # Add Retry-After header for rate limit exceeded
    if isinstance(exc, RateLimitExceededError) and hasattr(exc, 'retry_after'):
        headers["Retry-After"] = str(exc.retry_after if exc.retry_after else 60)

    return JSONResponse(
        status_code=status_code,
        content={
            "code": code,
            "message": message,
        },
        headers=headers if headers else None
    )
