from fastapi import Depends

from app.domain.interfaces import PasswordValidator
from app.infrastructure.security.password_validator import CommonPasswordValidator


def get_password_validator() -> PasswordValidator:
    """Get password validator instance."""
    return CommonPasswordValidator(min_length=8)
