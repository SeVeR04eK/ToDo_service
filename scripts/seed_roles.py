import asyncio
from sqlalchemy import select
from app.infrastructure.database import SessionLocal
from app.infrastructure.models import Role


async def seed_roles() -> None:
    async with SessionLocal() as session:
        roles = ("user", "admin")

        for role_name in roles:
            existing_role = await session.scalar(
                select(Role).where(Role.name == role_name)
            )

            if existing_role is None:
                session.add(Role(name=role_name))

        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed_roles())
