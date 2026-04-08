from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.schemas import UserCreate, UserRead
from app.core.security import bcrypt_context

async def create_user(user: UserCreate, session: AsyncSession):

    user = User(
        username=user.username,
        hashed_password=bcrypt_context.hash(user.password),
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return UserRead.model_validate(user)