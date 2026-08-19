from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from app.domain.entities import RefreshToken


class RefreshTokenRepository(ABC):

    @abstractmethod
    async def create_refresh_token(
        self,
        user_id: int,
        token_hash: str,
        family_id: str,
        expires: datetime,
    ) -> RefreshToken: ...

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
    async def revoke_refresh_token(
        self,
        token_id: int,
        replaced_by: Optional[int] = None,
    ) -> bool:
        """Revoke a refresh token by ID and optionally set the replacement token."""
        ...

    @abstractmethod
    async def get_by_token_hash(
        self,
        token_hash: str,
    ) -> RefreshToken | None: ...

    @abstractmethod
    async def revoke_family_by_id(
        self,
        family_id: str,
    ) -> None:
        """Revoke all tokens in a family by family ID."""
        ...

    @abstractmethod
    async def revoke_token_by_user_id(
        self,
        user_id: int,
    ) -> None:
        """Revoke all active refresh token families for a user."""
        ...

    @abstractmethod
    async def delete_expired_tokens(
        self,
    ) -> None: ...