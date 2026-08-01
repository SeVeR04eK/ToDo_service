from app.domain.interfaces import PasswordHasher
from app.infrastructure.security.bcrypt_password_hasher import BcryptPasswordHasher


def get_password_hasher() -> PasswordHasher:
    return BcryptPasswordHasher()