from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.infrastructure.models import User as UserORM, Role as RoleORM
from app.domain.entities import User
from app.infrastructure.mappers import user_from_orm
from app.domain.interfaces import UserRepository, PasswordHasher
from app.domain.value_objects import UserUpdateData


class SQLAlchemyUserRepository(UserRepository):
    """Repository for user-related database operations."""

    def __init__(self, session: AsyncSession, password_hasher: PasswordHasher):
        self.session = session
        self.password_hasher = password_hasher

    async def create_user(self, username: str, password: str) -> User:
        """Create a new user with hashed password."""

        orm_user = UserORM(
            username=username,
            hashed_password=self.password_hasher.hash(password)
        )

        self.session.add(orm_user)
        await self.session.flush()

        await self.session.refresh(
            orm_user,
            ["role"]
        )

        return user_from_orm(orm_user)

    async def get_user_by_username(self, username: str) -> User | None:
        """Get a user by username with role relationship loaded."""

        # selectinload eagerly loads the role relationship to avoid N+1 queries
        request = (select(UserORM)
                   .options(selectinload(UserORM.role))
                   .where(UserORM.username == username))

        orm_user = await self.session.scalar(request)
        return user_from_orm(orm_user) if orm_user is not None else None

    async def get_user_by_id(self, user_id: int) -> User | None:
        """Get a user by ID with role relationship loaded."""

        # selectinload eagerly loads the role relationship to avoid N+1 queries
        request = (select(UserORM)
                   .options(selectinload(UserORM.role))
                   .where(UserORM.id == user_id))

        orm_user = await self.session.scalar(request)
        return user_from_orm(orm_user) if orm_user is not None else None

    async def get_user_role(self, user_id: int) -> str | None:
        """Get the role name for a user by ID."""

        request = select(RoleORM.name).join(UserORM.role).where(UserORM.id == user_id)

        return await self.session.scalar(request)

    async def update_user(self, user: User, user_update: UserUpdateData) -> User:
        """Update an existing user with partial data."""

        # Get the ORM user from the domain user with role relationship loaded
        request = select(UserORM).options(selectinload(UserORM.role)).where(UserORM.id == user.id)
        orm_user = await self.session.scalar(request)
        
        if orm_user is None:
            return user

        update_data = {
            key: value
            for key, value in vars(user_update).items()
            if value is not None
        }

        for key, value in update_data.items():
            # Hash password if it's being updated
            if key == "password":
                orm_user.hashed_password = self.password_hasher.hash(update_data["password"])
            else:
                setattr(orm_user, key, value)

        await self.session.flush()
        await self.session.refresh(
            orm_user,
            ["role"]
        )

        return user_from_orm(orm_user)

    async def delete_user(self, user: User) -> None:
        """Delete a user from the database."""

        # Get the ORM user from the domain user
        request = select(UserORM).where(UserORM.id == user.id)
        orm_user = await self.session.scalar(request)
        
        if orm_user is not None:
            await self.session.delete(orm_user)