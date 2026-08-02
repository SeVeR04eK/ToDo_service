from abc import ABC, abstractmethod

from app.domain.entities import User
from app.domain.value_objects import UserUpdateData

class UserRepository(ABC):

    @abstractmethod
    async def create_user(self, username: str, password: str) -> User: ...

    @abstractmethod
    async def get_user_by_username(self, username: str) -> User | None: ...

    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> User | None: ...

    @abstractmethod
    async def get_user_role(self, user_id: int) -> str | None: ...

    @abstractmethod
    async def update_user(self, user: User, user_update: UserUpdateData) -> User: ...

    @abstractmethod
    async def delete_user(self, user: User) -> None: ...