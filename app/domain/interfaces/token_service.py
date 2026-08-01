from abc import ABC, abstractmethod
from datetime import timedelta, datetime


class TokenService(ABC):

    @abstractmethod
    def create_access_token(
        self,
        username: str,
        user_id: int,
        role: str,
        delta: timedelta | None = None
    ) -> str:
        ...

    @abstractmethod
    async def create_refresh_token(
        self,
        username: str,
        user_id: int,
        delta: timedelta | None = None
    ) -> tuple[str, datetime]:
        ...

    @abstractmethod
    def decode_access_token(
        self,
        access_token: str,
    ) -> dict:
        ...

    @abstractmethod
    def decode_refresh_token(
        self,
        refresh_token: str,
    ) -> dict:
        ...