from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models import User, Role
from app.schemas import UserCreate, UserUpdate
from app.utils import hash_password


class UserRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, user: UserCreate) -> User:

        user = User(
            username=user.username,
            hashed_password=hash_password(user.password),
        )

        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        return user

    async def get_user_by_username(self, username: str) -> User:

        request = (select(User)
                   .options(selectinload(User.role))
                   .where(User.username == username))

        return await self.session.scalar(request)

    async def get_user_by_id(self, user_id: int) -> User:

        request = (select(User)
                   .options(selectinload(User.role))
                   .where(User.id == user_id))

        return await self.session.scalar(request)

    async def get_user_role(self, user_id) -> str:

        request = select(Role.name).join(User.role).where(User.id == user_id)

        return await self.session.scalar(request)

    async def update_task(self, user: User, user_update: UserUpdate) -> User:

        update_data = user_update.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            if key == "password":
                user.hashed_password = hash_password(update_data["password"])
            else:
                setattr(user, key, value)

        await self.session.commit()
        await self.session.refresh(user)

        return user

    async def delete_user(self, user: User) -> None:

        await self.session.delete(user)
        await self.session.commit()