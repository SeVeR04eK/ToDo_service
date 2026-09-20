from dataclasses import dataclass


@dataclass
class CreateUserDTO:
    username: str
    email: str
    password: str
    password_confirm: str

@dataclass
class UpdateUserDTO:
    username: str | None = None
    email: str | None = None
    password: str | None = None
    password_confirm: str | None = None
    previous_password: str | None = None