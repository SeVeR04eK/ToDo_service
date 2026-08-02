from fastapi import Depends
from typing import Callable

from app.presentation.api.dependencies.auth_dep import get_current_user
from app.domain.exceptions import PermissionDeniedError


def require_role(*allowed_roles: str) -> Callable:
    """Dependency factory to require specific user roles."""
    def wrapper(user = Depends(get_current_user)):
        if user.role.name not in allowed_roles:
            raise PermissionDeniedError()
        return user
    return wrapper
