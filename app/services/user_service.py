from app.schemas import UserCreate, UserUpdate
from app.domain.interfaces import UserRepository
from app.core.exceptions import UsernameAlreadyExistsError, UserNotFoundError
from app.domain.entities import User


class UserService:

    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def create_user_service(self, user: UserCreate) -> User:

        # Check if username already exists
        existing_user = await self.repository.get_user_by_username(username=user.username)
        if existing_user is not None:
            raise UsernameAlreadyExistsError("Username already taken")

        return await self.repository.create_user(user)


    async def get_user_service(self, user_id: int) -> User:

        user = await self.repository.get_user_by_id(user_id=user_id)
        if user is None:
            raise UserNotFoundError("User not found")

        return user

    async def update_user_service(self, user_id: int, user_update: UserUpdate) -> User:

        user = await self.repository.get_user_by_id(user_id=user_id)
        if user is None:
            raise UserNotFoundError("User not found")
        # Check if username already exists
        if user_update.username != user.username and user_update.username is not None:
            existing_user = await self.repository.get_user_by_username(username=user_update.username)
            if existing_user is not None:
                raise UsernameAlreadyExistsError("Username already taken")

        return await self.repository.update_user(user=user, user_update=user_update)

    async def delete_user_service(self, user_id: int) -> None:

        user = await self.repository.get_user_by_id(user_id=user_id)
        if user is None:
            raise UserNotFoundError("User not found")

        await self.repository.delete_user(user=user)
