from fastapi import Depends

from app.domain.interfaces import (
    UserRepository,
    TaskRepository,
    RefreshTokenRepository,
    AdminRepository,
)
from app.services import UserService, TaskService, AuthService, AdminService
from app.api.dependencies.repositories_dep import (
    get_user_repository,
    get_task_repository,
    get_refresh_token_repository,
    get_admin_repository,
)


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
) -> AuthService:
    return AuthService(user_repository, refresh_token_repository)


def get_admin_service(
    user_repository: UserRepository = Depends(get_user_repository),
    admin_repository: AdminRepository = Depends(get_admin_repository),
    task_repository: TaskRepository = Depends(get_task_repository),
) -> AdminService:
    return AdminService(user_repository, admin_repository, task_repository)