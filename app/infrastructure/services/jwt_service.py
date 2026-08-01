from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.core import settings
from app.domain.interfaces import TokenService
from app.core.exceptions import InvalidAccessTokenError, InvalidRefreshTokenError


class JWTService(TokenService):

    def create_access_token(
        self,
        username: str,
        user_id: int,
        role: str,
        delta: timedelta | None = None
    ) -> str:

        if delta is None:
            delta = settings.access_token_expire_minutes

        expires = datetime.now(timezone.utc) + delta

        payload = {
            "sub": username,
            "id": user_id,
            "role": role,
            "exp": int(expires.timestamp()),
        }

        return jwt.encode(
            payload,
            settings.secret_key.get_secret_value(),
            algorithm=settings.algorithm,
        )

    async def create_refresh_token(
        self,
        username: str,
        user_id: int,
        delta: timedelta | None = None
    ) -> tuple[str, datetime]:

        if delta is None:
            delta = settings.refresh_token_expire_days

        expires = datetime.now(timezone.utc) + delta

        payload = {
            "sub": username,
            "id": user_id,
            "exp": int(expires.timestamp()),
        }

        token = jwt.encode(
            payload,
            settings.secret_key.get_secret_value(),
            algorithm=settings.algorithm,
        )

        return token, expires

    def decode_access_token(
        self,
        access_token: str,
    ) -> dict:

        try:
            payload = jwt.decode(
                access_token,
                settings.secret_key.get_secret_value(),
                algorithms=[settings.algorithm],
            )

            if payload.get("sub") is None or payload.get("id") is None:
                raise InvalidAccessTokenError()

            return payload

        except JWTError:
            raise InvalidAccessTokenError()

    def decode_refresh_token(
        self,
        refresh_token: str,
    ) -> dict:

        try:
            payload = jwt.decode(
                refresh_token,
                settings.secret_key.get_secret_value(),
                algorithms=[settings.algorithm],
            )

            if payload.get("sub") is None or payload.get("id") is None:
                raise InvalidRefreshTokenError()

            return payload

        except JWTError:
            raise InvalidRefreshTokenError()