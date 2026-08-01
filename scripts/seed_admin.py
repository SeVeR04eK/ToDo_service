import asyncio
from sqlalchemy import select

from app.infrastructure.database import SessionLocal
from app.infrastructure.models import User, Role
from app.infrastructure.security.bcrypt_password_hasher import BcryptPasswordHasher
from app.core import settings


async def seed_admin() -> None:
    async with SessionLocal() as db:

        admin_role = await db.scalar(
            select(Role).where(Role.name == "admin")
        )

        if admin_role is None:
            raise RuntimeError("Role 'admin' does not exist")

        existing_admin = await db.scalar(
            select(User).where(User.username == settings.first_admin_username)
        )

        if existing_admin is not None:
            return

        password_hasher = BcryptPasswordHasher()

        admin = User(
            username=settings.first_admin_username,
            hashed_password=password_hasher.hash(settings.first_admin_password.get_secret_value()),
            role_id=admin_role.id,
            is_active=True,
        )

        db.add(admin)
        await db.commit()


if __name__ == "__main__":
    asyncio.run(seed_admin())
