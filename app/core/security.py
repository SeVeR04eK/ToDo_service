from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import timedelta, datetime, timezone
from jose import jwt, JWTError
from fastapi import HTTPException, status

from app.models import User, RefreshToken
from app.core import settings


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/authentication")


async def authenticate_user(
        username: str,
        password: str,
        session: AsyncSession
) -> User | None:

    request = (select(User)
               .options(selectinload(User.role))
               .where(User.username == username))
    result = await session.execute(request)
    user = result.scalar_one_or_none()

    if user is None:
        return None

    if not bcrypt_context.verify(password, user.hashed_password):
        return None

    return user

def create_access_token(
        username: str,
        user_id, role: str,
        delta: timedelta = settings.access_token_expire_minutes
) -> str:

    payload = {"sub": username, "id": user_id, "role": role}
    expires = datetime.now(timezone.utc) + delta
    payload.update({"exp": int(expires.timestamp())})

    return jwt.encode(payload, settings.secret_key, algorithm = settings.algorithm)

async def create_refresh_token(
        username: str,
        user_id: int,
        session: AsyncSession,
        delta: timedelta = settings.refresh_token_expire_days
) -> str:

    payload = {"sub": username, "id": user_id}
    expires = datetime.now(timezone.utc) + delta
    payload.update({"exp": int(expires.timestamp())})

    token = jwt.encode(payload, settings.secret_key, algorithm = settings.algorithm)

    session.add(RefreshToken(
        user_id = user_id,
        token = token,
        expires_at = expires)
    )
    await session.commit()

    return token

def decode_refresh_token(refresh_token: str) -> dict:

    try:
        payload = jwt.decode(refresh_token, settings.secret_key, algorithms=[settings.algorithm])

        if payload.get("sub") is None or payload.get("id") is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        return payload

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

def decode_access_token(access_token: str) -> dict:

    try:
        payload = jwt.decode(access_token, settings.secret_key, algorithms = [settings.algorithm])

        if payload.get("sub") is None or payload.get("id") is None:
            raise HTTPException(status_code = 401, detail = "Could not validate user")

        return payload

    except JWTError:
        raise HTTPException(status_code = 401, detail="Could not validate user")