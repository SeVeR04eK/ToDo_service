from fastapi import Request
from fastapi.responses import JSONResponse
from typing import Type, Tuple, Dict

from app.domain.exceptions import *
from app.domain.exceptions.base import DomainException


ERROR_MAP: Dict[Type[DomainException], Tuple[int, str]] = {
    UserNotFoundError: (404, "User not found"),
    UsernameAlreadyExistsError: (409, "Username already exists"),
    PermissionDeniedError: (403, "Not enough permissions"),
    RoleNotFoundError: (404, "Role not found"),
    RoleAlreadyExistsError: (409, "Role already exists"),
    TaskNotFoundError: (404, "Task not found"),
    InvalidCredentialsError: (401, "Invalid credentials"),
    InvalidAccessTokenError: (401, "Invalid access token"),
    InvalidRefreshTokenError: (401, "Invalid refresh token"),
}


async def domain_exception_handler(_request: Request, exc: DomainException):
    status_code, detail = ERROR_MAP.get(type(exc), (400, "Domain error"))

    return JSONResponse(
        status_code=status_code,
        content={"detail": detail},
    )
