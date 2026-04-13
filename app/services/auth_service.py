from fastapi import status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from app.repository import RefreshTokenRepository, UserRepository
from app.core.security import authenticate_user, create_access_token, create_refresh_token, decode_refresh_token
from app.schemas import TokensResponse


class AuthService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def authentication_service(self, form_data: OAuth2PasswordRequestForm) -> TokensResponse:

        user = await authenticate_user(form_data.username, form_data.password, self.session)

        repository = RefreshTokenRepository(session=self.session)
        await repository.delete_refresh_token(user.id)

        access_token = create_access_token(
            username = user.username,
            user_id = user.id,
            role = user.role.name
        )
        refresh_token = await create_refresh_token(
            username = user.username,
            user_id = user.id,
            session = self.session
        )

        return TokensResponse(refresh_token = refresh_token, access_token = access_token, token_type = "bearer")

    async def refresh_service(self, refresh_token: str) -> TokensResponse:

        refresh_repository = RefreshTokenRepository(session=self.session)
        db_token = await refresh_repository.get_token_expires(refresh_token)

        if db_token is None or db_token.expires_at < datetime.now(timezone.utc):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid refresh token")

        payload = decode_refresh_token(refresh_token)
        username = payload["sub"]
        user_id = payload["id"]

        await refresh_repository.delete_refresh_token(user_id)

        user_repository = UserRepository(session=self.session)
        user_role = await user_repository.get_user_role(user_id)

        if user_role is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")

        new_refresh = await create_refresh_token(
            username=username,
            user_id=user_id,
            session=self.session
        )
        new_access = create_access_token(
            username=username,
            user_id=user_id,
            role=user_role
        )

        return TokensResponse(refresh_token = new_refresh, access_token = new_access, token_type = "bearer")