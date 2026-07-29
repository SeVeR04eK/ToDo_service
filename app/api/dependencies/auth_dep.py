from fastapi import Depends, HTTPException

from app.security.auth import oauth2_bearer, decode_access_token
from app.domain.entities import User
from app.domain.interfaces import UserRepository
from app.api.dependencies.repositories_dep import get_user_repository

async def get_current_user(
    access_token: str = Depends(oauth2_bearer),
    repository: UserRepository = Depends(get_user_repository)
) -> User:
    """Dependency to get the current authenticated user."""
    payload = decode_access_token(access_token)
    user_id = payload["id"]

    user = await repository.get_user_by_id(user_id)

    if user is None:
        raise HTTPException(401, "User not found")

    if not user.is_active:
        raise HTTPException(403, "Inactive user")

    return user
