from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.domain.interfaces import PasswordHasher
from app.presentation.api.dependencies.password_hasher_dep import get_password_hasher

from app.infrastructure.repositories import (
    SQLAlchemyUserRepository,
    SQLAlchemyTaskRepository,
    SQLAlchemyRefreshTokenRepository,
    SQLAlchemyAdminRepository,
)
from app.domain.interfaces import (
    UserRepository,
    TaskRepository,
    RefreshTokenRepository,
    AdminRepository,
)
from app.infrastructure.database import get_session


def get_user_repository(
    session: AsyncSession = Depends(get_session),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
) -> UserRepository:
    return SQLAlchemyUserRepository(session, password_hasher)


def get_task_repository(
    session: AsyncSession = Depends(get_session),
) -> TaskRepository:
    return SQLAlchemyTaskRepository(session)


def get_refresh_token_repository(
    session: AsyncSession = Depends(get_session),
) -> RefreshTokenRepository:
    return SQLAlchemyRefreshTokenRepository(session)

def get_refresh_token_repository_raw(
    session: AsyncSession = Depends(get_session),
) -> RefreshTokenRepository:
    return SQLAlchemyRefreshTokenRepository(session)

def get_admin_repository(
    session: AsyncSession = Depends(get_session),
) -> AdminRepository:
    return SQLAlchemyAdminRepository(session)