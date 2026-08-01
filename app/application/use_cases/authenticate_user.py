from app.domain.entities import User
from app.domain.interfaces import UserRepository
from app.core.exceptions import InvalidCredentialsError
from app.domain.interfaces import PasswordHasher



class AuthenticateUserUseCase:

    def __init__(
        self,
        repository: UserRepository,
        password_hasher: PasswordHasher
    ):
        self.repository = repository
        self.password_hasher = password_hasher


    async def execute(
        self,
        username: str,
        password: str
    ) -> User:

        user = await self.repository.get_user_by_username(username)

        if user is None:
            raise InvalidCredentialsError("Incorrect username or password")

        if not self.password_hasher.verify(
            password,
            user.hashed_password
        ):
            raise InvalidCredentialsError("Incorrect username or password")

        return user