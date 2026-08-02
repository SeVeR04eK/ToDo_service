from dataclasses import dataclass


@dataclass
class UserPermissionData:
    is_active: bool | None = None
    role_id: int | None = None