from fastapi import Depends, HTTPException

from app.api.deps import get_current_user


def require_role(*allowed_roles: str):
    def wrapper(user = Depends(get_current_user)):
        if user.role.name not in allowed_roles:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return user
    return wrapper