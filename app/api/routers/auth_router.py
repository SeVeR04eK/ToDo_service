from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from app.api.deps import db
from app.schemas import TokensResponse
from app.services import AuthService
from app.schemas import RefreshTokenGet

auth_router = APIRouter(prefix = "/auth", tags = ["auth"])

@auth_router.post("/authentication", response_model = TokensResponse)
async def authentication(
        form_data: Annotated[
            OAuth2PasswordRequestForm,
            Depends()
        ],
        session: db
):

    service = AuthService(session)
    return await service.authentication_service(form_data)

@auth_router.post("/refresh", response_model = TokensResponse)
async def refresh(refresh_token_data: RefreshTokenGet, session: db):

    service = AuthService(session)

    return await service.refresh_service(refresh_token_data.refresh_token)