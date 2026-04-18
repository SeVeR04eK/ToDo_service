from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Sequence

from app.models import Role


async def get_roles(session: AsyncSession) -> Sequence[Role]:

    return (await session.scalars(select(Role))).all()