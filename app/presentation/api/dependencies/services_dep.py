from fastapi import Depends

from app.domain.interfaces import (
    UnitOfWork,
    TokenService,
    TokenHasher,
    PasswordValidator,
    PasswordHasher
)
from app.application.interfaces import UserCache, TaskCache, RoleCache
from app.application.services import UserService, TaskService, AuthService, AdminService
from app.presentation.api.dependencies.uow import get_unit_of_work
from app.presentation.api.dependencies.tokens_dep import get_token_service
from app.presentation.api.dependencies.token_hasher_dep import get_token_hasher
from app.presentation.api.dependencies.use_cases_dep import get_auth_user_use_case
from app.presentation.api.dependencies.password_validator_dep import get_password_validator
from app.presentation.api.dependencies.password_hasher_dep import get_password_hasher
from app.presentation.api.dependencies.cache_dep import get_user_cache, get_task_cache, get_role_cache
from app.application.use_cases import AuthenticateUserUseCase


def get_user_service(
    unit_of_work: UnitOfWork = Depends(get_unit_of_work),
    password_validator: PasswordValidator = Depends(get_password_validator),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
    user_cache: UserCache = Depends(get_user_cache),
) -> UserService:
    return UserService(unit_of_work, password_validator, password_hasher, user_cache)


def get_task_service(
    unit_of_work: UnitOfWork = Depends(get_unit_of_work),
    task_cache: TaskCache = Depends(get_task_cache),
) -> TaskService:
    return TaskService(unit_of_work, task_cache)


def get_auth_service(
    unit_of_work: UnitOfWork = Depends(get_unit_of_work),
    token_service: TokenService = Depends(get_token_service),
    authenticate_user_use_case: AuthenticateUserUseCase = Depends(get_auth_user_use_case),
    token_hasher: TokenHasher = Depends(get_token_hasher),
) -> AuthService:
    return AuthService(unit_of_work, token_service, authenticate_user_use_case, token_hasher)


def get_admin_service(
    unit_of_work: UnitOfWork = Depends(get_unit_of_work),
    role_cache: RoleCache = Depends(get_role_cache),
) -> AdminService:
    return AdminService(unit_of_work, role_cache)