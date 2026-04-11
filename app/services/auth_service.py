from fastapi import status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from app.core.security import authenticate_user, create_access_token, create_refresh_token, decode_refresh_token
from app.models import RefreshToken, User
from app.schemas import TokensResponse


class AuthService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def authentication_service(self, form_data: OAuth2PasswordRequestForm) -> TokensResponse:

        user = await authenticate_user(form_data.username, form_data.password, self.session)

        if user is None:
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "Incorrect username or password"
            )

        delete_request = delete(RefreshToken).where(RefreshToken.user_id == user.id)
        await self.session.execute(delete_request)

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

        request = select(RefreshToken).where(RefreshToken.token == refresh_token)
        result = await self.session.execute(request)
        db_token = result.scalar_one_or_none()

        if db_token is None or db_token.expires_at < datetime.now(timezone.utc):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid refresh token")

        payload = decode_refresh_token(refresh_token)
        username = payload["sub"]
        user_id = payload["id"]

        await self.session.delete(db_token)
        await self.session.commit()

        result = await self.session.execute(select(User)
                                            .options(selectinload(User.role))
                                            .where(User.id == user_id))
        user = result.scalar_one_or_none()

        if user is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")

        user_role = user.role.name

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