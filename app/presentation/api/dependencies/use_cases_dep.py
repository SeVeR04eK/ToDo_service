from fastapi import Depends

from app.application.use_cases import AuthenticateUserUseCase
from app.presentation.api.dependencies.repositories_dep import get_user_repository
from app.domain.interfaces import UserRepository, PasswordHasher
from app.presentation.api.dependencies.password_hasher_dep import get_password_hasher



def get_auth_user_use_case(
        repository: UserRepository = Depends(get_user_repository),
        password_hasher: PasswordHasher = Depends(get_password_hasher)
) -> AuthenticateUserUseCase:
    return AuthenticateUserUseCase(repository, password_hasher)