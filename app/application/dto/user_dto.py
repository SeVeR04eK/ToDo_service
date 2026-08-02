from dataclasses import dataclass


@dataclass
class CreateUserDTO:
    username: str
    password: str
    password_confirm: str

@dataclass
class UpdateUserDTO:
    username: str | None = None
    password: str | None = None
    password_confirm: str | None = None