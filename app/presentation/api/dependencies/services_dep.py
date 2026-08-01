from fastapi import Depends

from app.domain.interfaces import (
    UserRepository,
    TaskRepository,
    RefreshTokenRepository,
    AdminRepository,
    TokenService
)
from app.application.services import UserService, TaskService, AuthService, AdminService
from app.presentation.api.dependencies.repositories_dep import (
    get_user_repository,
    get_task_repository,
    get_refresh_token_repository,
    get_admin_repository,
)
from app.presentation.api.dependencies.tokens_dep import get_token_service
from app.presentation.api.dependencies.use_cases_dep import get_auth_user_use_case
from app.application.use_cases import AuthenticateUserUseCase


def get_user_service(
    repository: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(repository)


def get_task_service(
    repository: TaskRepository = Depends(get_task_repository),
) -> TaskService:
    return TaskService(repository)


def get_auth_service(
    user_repository: UserRepository = Depends(get_user_repository),
    refresh_token_repository: RefreshTokenRepository = Depends(get_refresh_token_repository),
    token_service: TokenService = Depends(get_token_service),
    authenticate_user_use_case: AuthenticateUserUseCase = Depends(get_auth_user_use_case),
) -> AuthService:
    return AuthService(user_repository, refresh_token_repository, token_service, authenticate_user_use_case)


def get_admin_service(
    user_repository: UserRepository = Depends(get_user_repository),
    admin_repository: AdminRepository = Depends(get_admin_repository),
    task_repository: TaskRepository = Depends(get_task_repository),
) -> AdminService:
    return AdminService(user_repository, admin_repository, task_repository)