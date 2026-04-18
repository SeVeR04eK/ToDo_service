from typing import Sequence, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.models import User, Role
from app.schemas import UserPermission, RoleCreate


class AdminRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_users(self, limit: Optional[int], offset: Optional[int]) -> Sequence[User]:

        request = select(User).options(selectinload(User.role))

        if offset is not None:
            request = request.offset(offset)

        if limit is not None:
            request = request.limit(limit)

        return (await self.session.scalars(request)).all()

    async def user_perm(self, user: User, user_permission: UserPermission) -> User:

        user_data = user_permission.model_dump(exclude_unset=True)

        for key, value in user_data.items():
            setattr(user, key, value)

        await self.session.commit()
        await self.session.refresh(user)

        return user

    async def create_role(self, new_role: RoleCreate) -> Role:

        role = Role(name=new_role.name)

        self.session.add(role)
        await self.session.commit()
        await self.session.refresh(role)

        return role