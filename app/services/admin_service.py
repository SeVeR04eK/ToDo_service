from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from typing import Optional

from app.repository import AdminRepository, UserRepository
from app.schemas import UserRead


class AdminService:

    def __init__(self, session: AsyncSession):
        self.admin_repository = AdminRepository(session)
        self.user_repository = UserRepository(session)

    async def get_users_service(self, username: Optional[str], limit: Optional[int]) -> list[UserRead] | UserRead:

        if username is None:
            users = await self.admin_repository.get_users(limit=limit)

            return [UserRead.model_validate(user) for user in users]

        user = await self.user_repository.get_user_by_username(username=username)

        return UserRead.model_validate(user)

    async def get_user_service(self, user_id: int) -> UserRead:

        user = await self.user_repository.get_user_by_id(user_id=user_id)

        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        return UserRead.model_validate(user)

    async def ban_user_service(self, user_id: int, is_active: bool) -> UserRead:

        user = await self.user_repository.get_user_by_id(user_id=user_id)

        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        user_updated = await self.admin_repository.ban_user(user=user, is_active=is_active)

        return UserRead.model_validate(user_updated)

    async def delete_user_service(self, user_id: int) -> None:

        user = await self.user_repository.get_user_by_id(user_id=user_id)

        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        await self.user_repository.delete_user(user=user)

