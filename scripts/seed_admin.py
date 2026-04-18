import asyncio
from sqlalchemy import select
from app.db.database import SessionLocal
from app.models import User, Role
from app.utils import hash_password
from app.core.config import settings


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

        admin = User(
            username=settings.first_admin_username,
            hashed_password=hash_password(settings.first_admin_password),
            role_id=admin_role.id,
            is_active=True,
        )

        db.add(admin)
        await db.commit()


if __name__ == "__main__":
    asyncio.run(seed_admin())
