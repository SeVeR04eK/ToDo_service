from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.models import User


class AdminRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_users(self) -> Sequence[User]:

        request = select(User).options(selectinload(User.role))

        return (await self.session.scalars(request)).all()

    async def ban_user(self, user: User, is_active) -> User:

        if is_active == user.is_active:
            return user

        user.is_active = is_active

        await self.session.commit()
        await self.session.refresh(user)

        return user