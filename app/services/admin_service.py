from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from typing import Optional

from app.repository import AdminRepository, UserRepository
from app.schemas import UserRead, RoleRead, UserPermission, RoleCreate
from app.repository import get_roles


class AdminService:

    def __init__(self, session: AsyncSession):
        self.admin_repository = AdminRepository(session)
        self.user_repository = UserRepository(session)
        self.session = session

    async def get_users_service(
            self,
            username: Optional[str],
            limit: Optional[int],
            offset: Optional[int]
    ) -> list[UserRead] | UserRead:

        if username is None:
            users = await self.admin_repository.get_users(limit=limit, offset=offset)

            return [UserRead.model_validate(user) for user in users]

        if offset is not None:
            return []

        user = await self.user_repository.get_user_by_username(username=username)

        return UserRead.model_validate(user)

    async def get_user_service(self, user_id: int) -> UserRead:

        user = await self.user_repository.get_user_by_id(user_id=user_id)

        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        return UserRead.model_validate(user)

    async def permission_user_service(self, user_id: int, user_permission: UserPermission) -> UserRead:

        user = await self.user_repository.get_user_by_id(user_id=user_id)

        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        if (user_permission.role_id is not None and
                user_permission.role_id not in [role.id for role in await get_roles(session=self.session)]):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")

        if user.role.name == "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

        user_updated = await self.admin_repository.user_perm(user=user, user_permission=user_permission)

        return UserRead.model_validate(user_updated)

    async def delete_user_service(self, user_id: int) -> None:

        user = await self.user_repository.get_user_by_id(user_id=user_id)

        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        if user.role.name == "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

        await self.user_repository.delete_user(user=user)

    async def create_role_service(self, new_role: RoleCreate) -> RoleRead:

        return RoleRead.model_validate(await self.admin_repository.create_role(new_role=new_role))

