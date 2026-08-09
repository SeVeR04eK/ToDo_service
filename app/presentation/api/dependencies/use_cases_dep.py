from fastapi import Depends

from app.application.use_cases import AuthenticateUserUseCase
from app.presentation.api.dependencies.uow import get_unit_of_work
from app.domain.interfaces import UnitOfWork, PasswordHasher
from app.presentation.api.dependencies.password_hasher_dep import get_password_hasher



def get_auth_user_use_case(
        unit_of_work: UnitOfWork = Depends(get_unit_of_work),
        password_hasher: PasswordHasher = Depends(get_password_hasher)
) -> AuthenticateUserUseCase:
    return AuthenticateUserUseCase(unit_of_work.user_repository, password_hasher)