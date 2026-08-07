import structlog
from app.application.dto import CreateUserDTO, UpdateUserDTO
from app.domain.value_objects import UserUpdateData
from app.domain.interfaces import UserRepository
from app.domain.exceptions import UsernameAlreadyExistsError, UserNotFoundError
from app.domain.entities import User

logger = structlog.get_logger(__name__)


class UserService:

    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def create_user_service(self, user: CreateUserDTO) -> User:

        logger.info(
            "Creating user",
            username=user.username,
        )
        
        # Check if username already exists
        existing_user = await self.repository.get_user_by_username(username=user.username)
        if existing_user is not None:
            logger.warning(
                "Username already exists",
                username=user.username,
            )
            raise UsernameAlreadyExistsError()

        created_user = await self.repository.create_user(username=user.username, password=user.password)
        
        logger.info(
            "User created",
            user_id=created_user.id,
            username=created_user.username,
        )
        
        return created_user


    async def get_user_service(self, user_id: int) -> User:

        user = await self.repository.get_user_by_id(user_id=user_id)
        if user is None:
            logger.warning(
                "User not found",
                user_id=user_id,
            )
            raise UserNotFoundError()

        return user

    async def update_user_service(self, user_id: int, user_update: UpdateUserDTO) -> User:

        logger.info(
            "Updating user",
            user_id=user_id,
        )

        user = await self.repository.get_user_by_id(user_id=user_id)
        if user is None:
            logger.warning(
                "User not found for update",
                user_id=user_id,
            )
            raise UserNotFoundError()

        # Check if username already exists
        if user_update.username != user.username and user_update.username is not None:
            existing_user = await self.repository.get_user_by_username(username=user_update.username)
            if existing_user is not None:
                logger.warning(
                    "Username already exists during update",
                    username=user_update.username,
                )
                raise UsernameAlreadyExistsError()

        # Validate password confirmation if password is being updated
        if user_update.password is not None and user_update.password != user_update.password_confirm:
            logger.warning(
                "Password confirmation mismatch during user update",
                user_id=user_id,
            )
            raise ValueError("Passwords do not match")

        user_update_data = UserUpdateData(
            username=user_update.username,
            password=user_update.password,
            password_confirm=user_update.password_confirm
        )

        updated_user = await self.repository.update_user(user=user, user_update=user_update_data)
        
        logger.info(
            "User updated",
            user_id=updated_user.id,
            username=updated_user.username,
        )
        
        return updated_user

    async def delete_user_service(self, user_id: int) -> None:

        logger.info(
            "Deleting user",
            user_id=user_id,
        )
        
        user = await self.repository.get_user_by_id(user_id=user_id)
        if user is None:
            logger.warning(
                "User not found for deletion",
                user_id=user_id,
            )
            raise UserNotFoundError()

        await self.repository.delete_user(user=user)
        
        logger.info(
            "User deleted",
            user_id=user_id,
        )
