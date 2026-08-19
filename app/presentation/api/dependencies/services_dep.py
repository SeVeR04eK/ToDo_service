from fastapi import Depends

from app.domain.interfaces import (
    UnitOfWork,
    TokenService,
    TokenHasher,
    PasswordValidator
)
from app.application.services import UserService, TaskService, AuthService, AdminService
from app.presentation.api.dependencies.uow import get_unit_of_work
from app.presentation.api.dependencies.tokens_dep import get_token_service
from app.presentation.api.dependencies.token_hasher_dep import get_token_hasher
from app.presentation.api.dependencies.use_cases_dep import get_auth_user_use_case
from app.presentation.api.dependencies.password_validator_dep import get_password_validator
from app.application.use_cases import AuthenticateUserUseCase


def get_user_service(
    unit_of_work: UnitOfWork = Depends(get_unit_of_work),
    password_validator: PasswordValidator = Depends(get_password_validator),
) -> UserService:
    return UserService(unit_of_work, password_validator)


def get_task_service(
    unit_of_work: UnitOfWork = Depends(get_unit_of_work),
) -> TaskService:
    return TaskService(unit_of_work)


def get_auth_service(
    unit_of_work: UnitOfWork = Depends(get_unit_of_work),
    token_service: TokenService = Depends(get_token_service),
    authenticate_user_use_case: AuthenticateUserUseCase = Depends(get_auth_user_use_case),
    token_hasher: TokenHasher = Depends(get_token_hasher),
) -> AuthService:
    return AuthService(unit_of_work, token_service, authenticate_user_use_case, token_hasher)


def get_admin_service(
    unit_of_work: UnitOfWork = Depends(get_unit_of_work),
) -> AdminService:
    return AdminService(unit_of_work)