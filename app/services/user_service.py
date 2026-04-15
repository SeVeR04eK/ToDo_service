from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.schemas import UserCreate, UserRead
from app.repository import UserRepository


class UserService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user_service(self, user: UserCreate) -> UserRead:

        repository = UserRepository(session=self.session)
        new_user = await repository.create_user(user)

        return UserRead(
            id=new_user.id,
            username=new_user.username,
            is_active=new_user.is_active,
            role=new_user.role_id
        )


    @staticmethod
    async def get_user_service(user: User) -> UserRead:

        return UserRead(
            id=user.id,
            username=user.username,
            is_active=user.is_active,
            role=user.role.name
        )