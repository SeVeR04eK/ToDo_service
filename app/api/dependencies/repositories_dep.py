from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.repositories import (
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
from app.db import get_session


def get_user_repository(
    session: AsyncSession = Depends(get_session),
) -> UserRepository:
    return SQLAlchemyUserRepository(session)


def get_task_repository(
    session: AsyncSession = Depends(get_session),
) -> TaskRepository:
    return SQLAlchemyTaskRepository(session)


def get_refresh_token_repository(
    session: AsyncSession = Depends(get_session),
) -> RefreshTokenRepository:
    return SQLAlchemyRefreshTokenRepository(session)


def get_admin_repository(
    session: AsyncSession = Depends(get_session),
) -> AdminRepository:
    return SQLAlchemyAdminRepository(session)