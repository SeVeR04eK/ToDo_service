from datetime import datetime, timedelta, timezone
import uuid

from jose import JWTError, jwt

from app.core import settings
from app.domain.interfaces import TokenService
from app.domain.exceptions import InvalidAccessTokenError, InvalidRefreshTokenError


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

        now = datetime.now(timezone.utc)
        expires = now + delta
        iat = int(now.timestamp())

        payload = {
            "sub": username,
            "id": user_id,
            "role": role,
            "exp": int(expires.timestamp()),
            "iat": iat,
            "iss": settings.jwt_issuer,
            "aud": settings.jwt_audience,
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

        now = datetime.now(timezone.utc)
        expires = now + delta
        iat = int(now.timestamp())

        payload = {
            "sub": username,
            "id": user_id,
            "exp": int(expires.timestamp()),
            "iat": iat,
            "jti": str(uuid.uuid4()),
            "iss": settings.jwt_issuer,
            "aud": settings.jwt_audience,
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
                issuer=settings.jwt_issuer,
                audience=settings.jwt_audience,
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
                issuer=settings.jwt_issuer,
                audience=settings.jwt_audience,
            )

            if payload.get("sub") is None or payload.get("id") is None:
                raise InvalidRefreshTokenError()

            return payload

        except JWTError:
            raise InvalidRefreshTokenError()