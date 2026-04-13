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

        return UserRead.model_validate(new_user)

    @staticmethod
    async def get_user_service(user: User) -> UserRead:

        return UserRead.model_validate(user)