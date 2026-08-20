from dataclasses import dataclass


@dataclass
class UserUpdateData:
    username: str | None = None
    password: str | None = None
