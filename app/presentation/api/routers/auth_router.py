from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from app.presentation.api.schemas import TokensResponse, RefreshTokenGet
from app.application.services import AuthService
from app.presentation.api.dependencies.services_dep import get_auth_service
from app.presentation.api.dependencies.auth_dep import get_current_user
from app.presentation.api.dependencies import rate_limit, rate_limit_auth, extract_login_identifier
from app.domain.entities import User
from app.core.config import settings

# Authentication router for login and token refresh
auth_router = APIRouter(prefix = "/auth", tags = ["auth"])

@auth_router.post("/authentication", status_code=status.HTTP_200_OK, response_model = TokensResponse, summary="User authentication", response_description="Returns access and refresh JWT tokens for authenticated user")
async def authentication(
        form_data: Annotated[
            OAuth2PasswordRequestForm,
            Depends()
        ],
        service: AuthService = Depends(get_auth_service),
        _rate_limit: Annotated[None, Depends(rate_limit(
            key_prefix="login",
            limit=settings.rate_limit_auth_login_limit,
            window=settings.rate_limit_auth_login_window,
            algorithm="sliding_window_log",
            fail_closed=True,
            identifier_extractor=extract_login_identifier
        ))] = None,
) -> TokensResponse:
    """**Authenticate** user with username/password and return JWT tokens."""


    tokens = await service.authentication_service(form_data.username, form_data.password)
    return TokensResponse(
        refresh_token=tokens.refresh_token,
        access_token=tokens.access_token,
        token_type=tokens.token_type,
        expires_in=tokens.expires_in
    )

@auth_router.post("/refresh", status_code=status.HTTP_200_OK, response_model = TokensResponse, summary="Access token refresh", response_description="Returns new access and refresh tokens (refresh token rotation enabled)")
async def refresh(
    refresh_token_data: RefreshTokenGet,
    service: AuthService = Depends(get_auth_service),
    _rate_limit: Annotated[None, Depends(rate_limit(
        key_prefix="refresh",
        limit=settings.rate_limit_auth_refresh_limit,
        window=settings.rate_limit_auth_refresh_window,
        algorithm="sliding_window_counter"
    ))] = None,
) -> TokensResponse:
    """Refresh access token using a valid refresh token (_Refresh token rotation is enabled._)."""


    tokens = await service.refresh_service(refresh_token_data.refresh_token)
    return TokensResponse(
        refresh_token=tokens.refresh_token,
        access_token=tokens.access_token,
        token_type=tokens.token_type,
        expires_in=tokens.expires_in
    )

@auth_router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, summary="Logout", response_description="Revoke the current refresh token")
async def logout(
        refresh_token_data: RefreshTokenGet,
        service: AuthService = Depends(get_auth_service)
) -> None:
    """Logout by revoking the current refresh token."""
    await service.logout_service(refresh_token_data.refresh_token)

@auth_router.post("/logout-all", status_code=status.HTTP_204_NO_CONTENT, summary="Logout all sessions", response_description="Revoke all refresh tokens for the authenticated user")
async def logout_all(
        current_user: User = Depends(get_current_user),
        service: AuthService = Depends(get_auth_service),
        _rate_limit: Annotated[None, Depends(rate_limit_auth(
            key_prefix="logout_all",
            limit=settings.rate_limit_auth_logout_all_limit,
            window=settings.rate_limit_auth_logout_all_window,
            algorithm="sliding_window_counter"
        ))] = None,
) -> None:
    """Logout by revoking all refresh tokens for the authenticated user."""
    await service.logout_all_service(current_user.id)