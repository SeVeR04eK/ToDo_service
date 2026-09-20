from dataclasses import dataclass


@dataclass
class UserUpdateData:
    username: str | None = None
    email: str | None = None
    password: str | None = None
