from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.infrastructure.models import User as UserORM, Role as RoleORM
from app.domain.entities import User, Role
from app.infrastructure.mappers import user_from_orm, role_from_orm
from app.domain.value_objects import UserPermissionData
from app.domain.interfaces import AdminRepository


class SQLAlchemyAdminRepository(AdminRepository):
    """Repository for admin-specific database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_users(self, limit: Optional[int], offset: Optional[int]) -> List[User]:
        """Get all users with optional pagination and role relationship loaded."""

        # selectinload eagerly loads the role relationship to avoid N+1 queries
        request = select(UserORM).options(selectinload(UserORM.role))

        if offset is not None:
            request = request.offset(offset)

        if limit is not None:
            request = request.limit(limit)

        orm_users = (await self.session.scalars(request)).all()
        return [user_from_orm(u) for u in orm_users]

    async def user_perm(self, user: User, user_permission: UserPermissionData) -> User:
        """Update user permissions (is_active status and role ID)."""

        # Get the ORM user from the domain user
        request = select(UserORM).options(selectinload(UserORM.role)).where(UserORM.id == user.id)
        orm_user = await self.session.scalar(request)

        if orm_user is None:
            return user

        update_data = {
            key: value
            for key, value in vars(user_permission).items()
            if value is not None
        }

        for key, value in update_data.items():
            setattr(orm_user, key, value)

        await self.session.commit()
        await self.session.refresh(
            orm_user,
            ["role"]
        )

        return user_from_orm(orm_user)

    async def create_role(self, name: str) -> Role:
        """Create a new role."""

        orm_role = RoleORM(name=name)

        self.session.add(orm_role)
        await self.session.commit()
        await self.session.refresh(orm_role)

        return role_from_orm(orm_role)

    async def get_roles(self) -> List[Role]:
        """Get all roles."""

        orm_roles = (await self.session.scalars(select(RoleORM))).all()
        return [role_from_orm(r) for r in orm_roles]

    async def get_role_id_by_name(self, name: str) -> int:
        """Get a role ID by its name."""

        request = select(RoleORM.id).where(RoleORM.name == name)

        return await self.session.scalar(request)
