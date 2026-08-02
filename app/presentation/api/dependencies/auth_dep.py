from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.domain.entities import User
from app.domain.interfaces import UserRepository
from app.presentation.api.dependencies.repositories_dep import get_user_repository
from app.presentation.api.dependencies.tokens_dep import get_token_service
from app.domain.interfaces import TokenService
from app.domain.exceptions import UserNotFoundError, PermissionDeniedError


oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/authentication")

async def get_current_user(
    access_token: str = Depends(oauth2_bearer),
    repository: UserRepository = Depends(get_user_repository),
    token_service: TokenService = Depends(get_token_service)
) -> User:
    """Dependency to get the current authenticated user."""
    payload = token_service.decode_access_token(access_token)
    user_id = payload["id"]

    user = await repository.get_user_by_id(user_id)

    if user is None:
        raise UserNotFoundError()

    if not user.is_active:
        raise PermissionDeniedError()

    return user
