"""Test factories for creating test data objects."""
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.models import User
from app.infrastructure.models.roles_model import Role
from app.infrastructure.models import Task
from app.application.dto import CreateTaskDTO, UpdateTaskDTO
from app.domain.enums import TaskStatus
from app.infrastructure.security.bcrypt_password_hasher import BcryptPasswordHasher


fake = Faker()
password_hasher = BcryptPasswordHasher()


class RoleFactory:
    """Factory for creating Role objects."""
    
    @staticmethod
    def create(name: str = "user") -> Role:
        """Create a Role instance."""
        return Role(name=name)
    
    @staticmethod
    async def create_in_db(
        session: AsyncSession,
        name: str = "user"
    ) -> Role:
        """Create and persist a Role in the database."""
        role = RoleFactory.create(name)
        session.add(role)
        await session.commit()
        await session.refresh(role)
        return role


class UserFactory:
    """Factory for creating User objects."""
    
    @staticmethod
    def create(
        username: str | None = None,
        password: str = "TestPassword123!",
        is_active: bool = True,
        role_id: int = 1
    ) -> User:
        """Create a User instance."""
        return User(
            username=username or fake.user_name(),
            hashed_password=password_hasher.hash(password),
            is_active=is_active,
            role_id=role_id
        )
    
    @staticmethod
    async def create_in_db(
        session: AsyncSession,
        username: str | None = None,
        password: str = "TestPassword123!",
        is_active: bool = True,
        role_id: int = 1
    ) -> User:
        """Create and persist a User in the database."""
        user = UserFactory.create(username, password, is_active, role_id)
        session.add(user)
        await session.commit()
        await session.refresh(user, ["role"])
        return user


class TaskFactory:
    """Factory for creating Task objects."""
    
    @staticmethod
    def create(
        title: str | None = None,
        content: str | None = None,
        status: TaskStatus = TaskStatus.todo,
        user_id: int = 1
    ) -> Task:
        """Create a Task instance."""
        return Task(
            title=title or fake.sentence(nb_words=5),
            content=content or fake.paragraph(nb_sentences=3),
            status=status,
            user_id=user_id
        )
    
    @staticmethod
    def create_dto(
        title: str | None = None,
        content: str | None = None,
        status: TaskStatus = TaskStatus.todo
    ) -> CreateTaskDTO:
        """Create a CreateTaskDTO instance."""
        return CreateTaskDTO(
            title=title or fake.sentence(nb_words=5),
            content=content or fake.paragraph(nb_sentences=3),
            status=status
        )
    
    @staticmethod
    def create_update_dto(
        title: str | None = None,
        content: str | None = None,
        status: TaskStatus | None = None
    ) -> UpdateTaskDTO:
        """Create an UpdateTaskDTO instance."""
        return UpdateTaskDTO(
            title=title,
            content=content,
            status=status
        )
    
    @staticmethod
    async def create_in_db(
        session: AsyncSession,
        title: str | None = None,
        content: str | None = None,
        status: TaskStatus = TaskStatus.todo,
        user_id: int = 1
    ) -> Task:
        """Create and persist a Task in the database."""
        task = TaskFactory.create(title, content, status, user_id)
        session.add(task)
        await session.commit()
        await session.refresh(task)
        return task
    
    @staticmethod
    async def create_many_in_db(
        session: AsyncSession,
        count: int,
        user_id: int = 1,
        status: TaskStatus | None = None
    ) -> list[Task]:
        """Create and persist multiple Tasks in the database."""
        tasks = []
        for _ in range(count):
            task_status = status or fake.random_element([TaskStatus.todo, TaskStatus.in_progress, TaskStatus.done])
            task = TaskFactory.create(user_id=user_id, status=task_status)
            session.add(task)
            tasks.append(task)
        
        await session.commit()
        for task in tasks:
            await session.refresh(task)
        
        return tasks
