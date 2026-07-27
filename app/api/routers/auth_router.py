from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from app.api.dependencies import db
from app.schemas import TokensResponse, RefreshTokenGet
from app.services import AuthService
from app.core.exceptions import InvalidTokenError, UserNotFoundError, AuthenticationError

# Authentication router for login and token refresh
auth_router = APIRouter(prefix = "/auth", tags = ["auth"])

@auth_router.post("/authentication", status_code=status.HTTP_200_OK, response_model = TokensResponse, summary="User authentication", response_description="Returns access and refresh JWT tokens for authenticated user")
async def authentication(
        form_data: Annotated[
            OAuth2PasswordRequestForm,
            Depends()
        ],
        session: db
) -> TokensResponse:
    """**Authenticate** user with username/password and return JWT tokens."""

    try:
        service = AuthService(session=session)
        return TokensResponse.model_validate(await service.authentication_service(form_data.username, form_data.password))
    except AuthenticationError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

@auth_router.post("/refresh", status_code=status.HTTP_200_OK, response_model = TokensResponse, summary="Access token refresh", response_description="Returns new access and refresh tokens (refresh token rotation enabled)")
async def refresh(refresh_token_data: RefreshTokenGet, session: db) -> TokensResponse:
    """Refresh access token using a valid refresh token (_Refresh token rotation is enabled._)."""

    try:
        service = AuthService(session=session)
        return TokensResponse.model_validate(await service.refresh_service(refresh_token_data.refresh_token))
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")