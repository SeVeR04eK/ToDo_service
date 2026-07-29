from abc import ABC, abstractmethod
from datetime import datetime

from app.domain.entities import RefreshToken


class RefreshTokenRepository(ABC):

    @abstractmethod
    async def create_refresh_token(
        self,
        user_id: int,
        token: str,
        expires: datetime,
    ) -> None: ...

    @abstractmethod
    async def delete_refresh_token_by_user_id(
        self,
        user_id: int,
    ) -> None: ...

    @abstractmethod
    async def delete_refresh_token(
        self,
        token: RefreshToken,
    ) -> None: ...

    @abstractmethod
    async def get_token_expires(
        self,
        refresh_token: str,
    ) -> RefreshToken | None: ...

    @abstractmethod
    async def delete_expired_tokens(
        self,
    ) -> None: ...