from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from app.presentation.api.schemas import TokensResponse, RefreshTokenGet, DataResponse
from app.application.services import AuthService
from app.presentation.api.dependencies.services_dep import get_auth_service

# Authentication router for login and token refresh
auth_router = APIRouter(prefix = "/auth", tags = ["auth"])

@auth_router.post("/authentication", status_code=status.HTTP_200_OK, response_model = DataResponse[TokensResponse], summary="User authentication", response_description="Returns access and refresh JWT tokens for authenticated user")
async def authentication(
        form_data: Annotated[
            OAuth2PasswordRequestForm,
            Depends()
        ],
        service: AuthService = Depends(get_auth_service)
) -> DataResponse[TokensResponse]:
    """**Authenticate** user with username/password and return JWT tokens."""


    tokens = await service.authentication_service(form_data.username, form_data.password)
    return DataResponse[TokensResponse](
        data=TokensResponse(
            refresh_token=tokens.refresh_token,
            access_token=tokens.access_token,
            token_type=tokens.token_type
        )
    )

@auth_router.post("/refresh", status_code=status.HTTP_200_OK, response_model = DataResponse[TokensResponse], summary="Access token refresh", response_description="Returns new access and refresh tokens (refresh token rotation enabled)")
async def refresh(refresh_token_data: RefreshTokenGet, service: AuthService = Depends(get_auth_service)) -> DataResponse[TokensResponse]:
    """Refresh access token using a valid refresh token (_Refresh token rotation is enabled._)."""


    tokens = await service.refresh_service(refresh_token_data.refresh_token)
    return DataResponse[TokensResponse](
        data=TokensResponse(
            refresh_token=tokens.refresh_token,
            access_token=tokens.access_token,
            token_type=tokens.token_type
        )
    )