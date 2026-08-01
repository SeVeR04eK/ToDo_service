from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from app.presentation.api.schemas import TokensResponse, RefreshTokenGet
from app.application.services import AuthService
from app.core.exceptions import InvalidRefreshTokenError, UserNotFoundError, InvalidCredentialsError
from app.presentation.api.dependencies.services_dep import get_auth_service

# Authentication router for login and token refresh
auth_router = APIRouter(prefix = "/auth", tags = ["auth"])

@auth_router.post("/authentication", status_code=status.HTTP_200_OK, response_model = TokensResponse, summary="User authentication", response_description="Returns access and refresh JWT tokens for authenticated user")
async def authentication(
        form_data: Annotated[
            OAuth2PasswordRequestForm,
            Depends()
        ],
        service: AuthService = Depends(get_auth_service)
) -> TokensResponse:
    """**Authenticate** user with username/password and return JWT tokens."""

    try:
        tokens = await service.authentication_service(form_data.username, form_data.password)
        return TokensResponse(
            refresh_token=tokens.refresh_token,
            access_token=tokens.access_token,
            token_type=tokens.token_type
        )
    except InvalidCredentialsError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

@auth_router.post("/refresh", status_code=status.HTTP_200_OK, response_model = TokensResponse, summary="Access token refresh", response_description="Returns new access and refresh tokens (refresh token rotation enabled)")
async def refresh(refresh_token_data: RefreshTokenGet, service: AuthService = Depends(get_auth_service)) -> TokensResponse:
    """Refresh access token using a valid refresh token (_Refresh token rotation is enabled._)."""

    try:
        tokens = await service.refresh_service(refresh_token_data.refresh_token)
        return TokensResponse(
            refresh_token=tokens.refresh_token,
            access_token=tokens.access_token,
            token_type=tokens.token_type
        )
    except InvalidRefreshTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")