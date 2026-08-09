from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.domain.interfaces import PasswordHasher, UnitOfWork
from app.infrastructure.unit_of_work import SQLAlchemyUnitOfWork
from app.infrastructure.database import get_session
from app.presentation.api.dependencies.password_hasher_dep import get_password_hasher


def get_unit_of_work(
    session: AsyncSession = Depends(get_session),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
) -> UnitOfWork:
    return SQLAlchemyUnitOfWork(session, password_hasher)