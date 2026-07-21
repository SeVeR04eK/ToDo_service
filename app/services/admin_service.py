from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from typing import Optional

from app.repositories import AdminRepository, UserRepository
from app.schemas import UserRead, RoleRead, UserPermission, RoleCreate, OnlyUserPermission


class AdminService:
    """Service layer for admin-specific business logic."""

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
        """Get users - returns list if no username filter, single user if username provided."""

        if username is None:
            users = await self.admin_repository.get_users(limit=limit, offset=offset)

            return [UserRead.model_validate(user) for user in users]

        # Offset not supported when filtering by username
        if offset is not None:
            return []

        user = await self.user_repository.get_user_by_username(username=username)

        return UserRead.model_validate(user)

    async def get_user_service(self, user_id: int) -> UserRead:
        """Get a single user by ID."""

        user = await self.user_repository.get_user_by_id(user_id=user_id)

        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        return UserRead.model_validate(user)

    async def permission_user_service(self, user_id: int, user_permission: UserPermission) -> UserRead:
        """Update user permissions (is_active status and role)."""

        user = await self.user_repository.get_user_by_id(user_id=user_id)

        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        if user.role is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User role not found")

        # Resolve role name to role ID if role is being updated
        if user_permission.role is not None:
            role = await self.admin_repository.get_role_id_by_name(user_permission.role)

            if role is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")

            only_user = OnlyUserPermission(is_active=user_permission.is_active, role_id=role)

        else:
            only_user = OnlyUserPermission(is_active=user_permission.is_active, role_id=None)

        # Prevent admins from modifying other admins' permissions
        if user.role.name == "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

        user_updated = await self.admin_repository.user_perm(user=user, user_permission=only_user)

        return UserRead.model_validate(user_updated)

    async def delete_user_service(self, user_id: int) -> None:
        """Delete a user (prevents deletion of admin users)."""

        user = await self.user_repository.get_user_by_id(user_id=user_id)

        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Prevent deletion of admin users
        if user.role is None or user.role.name == "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

        await self.user_repository.delete_user(user=user)

    async def create_role_service(self, new_role: RoleCreate) -> RoleRead:
        """Create a new role."""

        return RoleRead.model_validate(await self.admin_repository.create_role(new_role=new_role))

