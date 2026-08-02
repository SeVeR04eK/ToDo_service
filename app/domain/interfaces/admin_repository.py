from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities import User, Role
from app.domain.value_objects import UserPermissionData


class AdminRepository(ABC):

    @abstractmethod
    async def get_users(self, limit: Optional[int], offset: Optional[int]) -> List[User]: ...

    @abstractmethod
    async def user_perm(self, user: User, user_permission: UserPermissionData) -> User: ...

    @abstractmethod
    async def create_role(self, name: str) -> Role: ...

    @abstractmethod
    async def get_roles(self) -> List[Role]: ...

    @abstractmethod
    async def get_role_id_by_name(self, name: str) -> int | None: ...
