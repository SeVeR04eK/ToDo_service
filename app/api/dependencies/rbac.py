from fastapi import Depends, HTTPException, status
from typing import Callable

from app.api.dependencies.auth_dep import get_current_user


def require_role(*allowed_roles: str) -> Callable:
    """Dependency factory to require specific user roles."""
    def wrapper(user = Depends(get_current_user)):
        if user.role.name not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return user
    return wrapper
