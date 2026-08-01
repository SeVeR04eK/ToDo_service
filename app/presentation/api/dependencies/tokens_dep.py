from app.infrastructure.services.jwt_service import JWTService
from app.domain.interfaces import TokenService


def get_token_service() -> TokenService:
    return JWTService()
