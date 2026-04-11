from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.core.security import oauth2_bearer, decode_access_token


db = Annotated[AsyncSession, Depends(get_session)]

async def get_current_user(access_token: Annotated[str, Depends(oauth2_bearer)]) -> dict:

        payload = decode_access_token(access_token)

        return {
            "username": payload["sub"],
            "id": payload["id"],
            "role": payload["role"]
        }
