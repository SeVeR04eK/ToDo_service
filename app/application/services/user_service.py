import structlog
from app.application.dto import CreateUserDTO, UpdateUserDTO
from app.domain.value_objects import UserUpdateData
from app.domain.interfaces import UnitOfWork, PasswordValidator, PasswordHasher
from app.domain.exceptions import (
    UsernameAlreadyExistsError,
    UserNotFoundError,
    WeakPasswordError,
    InvalidCredentialsError
)
from app.domain.entities import User

logger = structlog.get_logger(__name__)


class UserService:

    def __init__(self, unit_of_work: UnitOfWork, password_validator: PasswordValidator, password_hasher: PasswordHasher):
        self.unit_of_work = unit_of_work
        self.password_validator = password_validator
        self.password_hasher = password_hasher

    async def create_user_service(self, user: CreateUserDTO) -> User:

        logger.info(
            "Creating user",
            username=user.username,
        )
        
        # Validate password strength
        is_valid, error_message = self.password_validator.validate(user.password)
        if not is_valid:
            logger.warning(
                "Password validation failed",
                username=user.username,
                reason=error_message
            )
            raise WeakPasswordError()
        
        async with self.unit_of_work:
            # Check if username already exists
            existing_user = await self.unit_of_work.user_repository.get_user_by_username(username=user.username)
            if existing_user is not None:
                logger.warning(
                    "Username already exists",
                    username=user.username,
                )
                raise UsernameAlreadyExistsError()

            created_user = await self.unit_of_work.user_repository.create_user(username=user.username, password=user.password)
            
            await self.unit_of_work.commit()
        
        logger.info(
            "User created",
            user_id=created_user.id,
            username=created_user.username,
        )
        
        return created_user


    async def get_user_service(self, user_id: int) -> User:

        user = await self.unit_of_work.user_repository.get_user_by_id(user_id=user_id)
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

        async with self.unit_of_work:
            user = await self.unit_of_work.user_repository.get_user_by_id(user_id=user_id)
            if user is None:
                logger.warning(
                    "User not found for update",
                    user_id=user_id,
                )
                raise UserNotFoundError()

            # Verify previous password if password is being updated
            if user_update.password is not None:
                if not user_update.previous_password:
                    raise InvalidCredentialsError()

                is_verified = self.password_hasher.verify(user_update.previous_password, user.hashed_password)
                if not is_verified:
                    logger.warning(
                        "Previous password verification failed during user update",
                        user_id=user_id,
                    )
                    raise InvalidCredentialsError()

                # Validate password strength
                is_valid, error_message = self.password_validator.validate(user_update.password)
                if not is_valid:
                    logger.warning(
                        "Password validation failed during update",
                        user_id=user_id,
                        reason=error_message
                    )
                    raise WeakPasswordError()

            # Check if username already exists
            if user_update.username and user_update.username != user.username:
                existing_user = await self.unit_of_work.user_repository.get_user_by_username(username=user_update.username)
                if existing_user is not None:
                    logger.warning(
                        "Username already exists during update",
                        username=user_update.username,
                    )
                    raise UsernameAlreadyExistsError()

            user_update_data = UserUpdateData(
                username=user_update.username,
                password=user_update.password
            )

            updated_user = await self.unit_of_work.user_repository.update_user(user=user, user_update=user_update_data)
            
            await self.unit_of_work.commit()
        
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
        
        async with self.unit_of_work:
            user = await self.unit_of_work.user_repository.get_user_by_id(user_id=user_id)
            if user is None:
                logger.warning(
                    "User not found for deletion",
                    user_id=user_id,
                )
                raise UserNotFoundError()

            await self.unit_of_work.user_repository.delete_user(user=user)
            
            await self.unit_of_work.commit()
        
        logger.info(
            "User deleted",
            user_id=user_id,
        )
