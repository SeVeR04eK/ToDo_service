from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict

from app.schemas import UserCreate, UserUpdate
from app.repositories import UserRepository
from app.core.exceptions import UsernameAlreadyExistsError, UserNotFoundError


class UserService:

    def __init__(self, session: AsyncSession):
        self.repository = UserRepository(session)

    async def create_user_service(self, user: UserCreate) -> Dict:

        # Check if username already exists
        existing_user = await self.repository.get_user_by_username(username=user.username)
        if existing_user is not None:
            raise UsernameAlreadyExistsError("Username already taken")

        new_user = await self.repository.create_user(user)

        user = await self.repository.get_user_by_id(user_id=new_user.id)

        return {
            "id": user.id,
            "username": user.username,
            "is_active": user.is_active,
            "role": {"name": user.role.name} if user.role else None  # type: ignore
        }


    async def get_user_service(self, user_id: int) -> Dict:

        user = await self.repository.get_user_by_id(user_id=user_id)
        if user is None:
            raise UserNotFoundError("User not found")

        return {
            "id": user.id,
            "username": user.username,
            "is_active": user.is_active,
            "role": {"name": user.role.name} if user.role else None  # type: ignore
        }

    async def update_user_service(self, user_id: int, user_update: UserUpdate) -> Dict:

        user = await self.repository.get_user_by_id(user_id=user_id)
        if user is None:
            raise UserNotFoundError("User not found")

        updated_user = await self.repository.update_user(user=user, user_update=user_update)

        return {
            "id": updated_user.id,
            "username": updated_user.username,
            "is_active": updated_user.is_active,
            "role": {"name": updated_user.role.name} if updated_user.role else None  # type: ignore
        }

    async def delete_user_service(self, user_id: int) -> None:

        user = await self.repository.get_user_by_id(user_id=user_id)
        if user is None:
            raise UserNotFoundError("User not found")

        await self.repository.delete_user(user=user)
