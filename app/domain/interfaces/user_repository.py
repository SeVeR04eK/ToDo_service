from abc import ABC, abstractmethod

from app.domain.entities import User
from app.presentation.api.schemas import UserCreate, UserUpdate


class UserRepository(ABC):

    @abstractmethod
    async def create_user(self, user: UserCreate) -> User: ...

    @abstractmethod
    async def get_user_by_username(self, username: str) -> User | None: ...

    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> User | None: ...

    @abstractmethod
    async def get_user_role(self, user_id: int) -> str | None: ...

    @abstractmethod
    async def update_user(self, user: User, user_update: UserUpdate) -> User: ...

    @abstractmethod
    async def delete_user(self, user: User) -> None: ...