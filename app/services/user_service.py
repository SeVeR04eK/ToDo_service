from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import User
from app.schemas import UserCreate, UserRead
from app.core.security import bcrypt_context


class UserService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user_service(self, user: UserCreate) -> UserRead:

        user = User(
            username=user.username,
            hashed_password=bcrypt_context.hash(user.password),
        )

        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        return UserRead.model_validate(user)

    async def get_user_service(self, user_id: int) -> UserRead:

        result = await self.session.execute(
            select(User.id, User.username, User.role_id, User.is_active).where(User.id == user_id))
        row = result.mappings().one()
        return UserRead.model_validate(dict(row))