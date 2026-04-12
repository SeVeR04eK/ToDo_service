from typing import Annotated
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db import get_session
from app.core.security import oauth2_bearer, decode_access_token
from app.models import User


db = Annotated[AsyncSession, Depends(get_session)]

async def get_current_user(
    access_token: str = Depends(oauth2_bearer),
    session: AsyncSession = Depends(get_session)
):
    payload = decode_access_token(access_token)
    user_id = payload["id"]

    result = await session.execute(select(User).options(selectinload(User.role)).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(401, "User not found")

    if not user.is_active:
        raise HTTPException(403, "Inactive user")

    return user
