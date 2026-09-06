import os
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient, ASGITransport
from faker import Faker
from sqlalchemy import select

# Set environment variable to disable logging setup during tests
os.environ["PYTEST_RUNNING"] = "true"

from app.main import app
from app.infrastructure.models import Base
from app.infrastructure.models import User as UserORM
from app.infrastructure.models.roles_model import Role as RoleORM
from app.infrastructure.models import Task as TaskORM
from app.infrastructure.services.jwt_service import JWTService
from app.infrastructure.security.bcrypt_password_hasher import BcryptPasswordHasher
from app.infrastructure.security.sha256_token_hasher import SHA256TokenHasher
from app.domain.enums import TaskStatus
from app.infrastructure.database import get_session
from app.presentation.api.dependencies.repositories_dep import (
    get_user_repository,
    get_task_repository,
    get_refresh_token_repository,
    get_admin_repository
)

from app.presentation.api.dependencies.uow import get_unit_of_work
from app.presentation.api.dependencies.token_hasher_dep import get_token_hasher
from app.presentation.api.dependencies.cache_dep import (
    get_user_cache,
    get_task_cache,
    get_role_cache
)
from app.presentation.api.dependencies.rate_limit_dep import get_rate_limiter
from app.infrastructure.redis.rate_limit import RedisSlidingWindowLog, RedisSlidingWindowCounter
from app.infrastructure.repositories import (
    SQLAlchemyUserRepository,
    SQLAlchemyTaskRepository,
    SQLAlchemyRefreshTokenRepository,
    SQLAlchemyAdminRepository,
)
from app.infrastructure.unit_of_work import SQLAlchemyUnitOfWork
from app.application.interfaces import UserCache, TaskCache, RoleCache, RateLimiter

# Test database URL (SQLite for testing)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    expire_on_commit=False,
    class_=AsyncSession
)

fake = Faker()
password_hasher = BcryptPasswordHasher()
token_hasher = SHA256TokenHasher()


@pytest.fixture
async def mock_user_cache():
    """Mock UserCache for testing."""
    from unittest.mock import AsyncMock
    cache = AsyncMock(spec=UserCache)
    cache.get_user.return_value = None
    return cache


@pytest.fixture
async def mock_task_cache():
    """Mock TaskCache for testing."""
    from unittest.mock import AsyncMock
    cache = AsyncMock(spec=TaskCache)
    cache.get_task.return_value = None
    cache.get_task_list.return_value = None
    return cache


@pytest.fixture
async def mock_role_cache():
    """Mock RoleCache for testing."""
    from unittest.mock import AsyncMock
    cache = AsyncMock(spec=RoleCache)
    cache.get_roles.return_value = None
    return cache


@pytest.fixture
async def mock_rate_limiter():
    """Mock RateLimiter for testing."""
    from unittest.mock import AsyncMock
    limiter = AsyncMock(spec=RateLimiter)
    limiter.is_allowed.return_value = True
    limiter.get_retry_after.return_value = None
    return limiter


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test."""
    async with test_engine.connect() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    async with test_engine.connect() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession, mock_user_cache, mock_task_cache, mock_role_cache, mock_rate_limiter) -> AsyncGenerator:
    """Create a test client with database session override."""
    from unittest.mock import patch

    async def override_get_session():
        yield db_session

    async def override_get_user_repository():
        yield SQLAlchemyUserRepository(db_session, password_hasher)

    async def override_get_task_repository():
        yield SQLAlchemyTaskRepository(db_session)

    async def override_get_refresh_token_repository():
        yield SQLAlchemyRefreshTokenRepository(db_session)

    async def override_get_admin_repository():
        yield SQLAlchemyAdminRepository(db_session)

    async def override_get_unit_of_work():
        yield SQLAlchemyUnitOfWork(db_session, password_hasher)

    async def override_get_token_hasher():
        yield token_hasher

    async def override_get_user_cache():
        yield mock_user_cache

    async def override_get_task_cache():
        yield mock_task_cache

    async def override_get_role_cache():
        yield mock_role_cache

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_user_repository] = override_get_user_repository
    app.dependency_overrides[get_task_repository] = override_get_task_repository
    app.dependency_overrides[get_refresh_token_repository] = override_get_refresh_token_repository
    app.dependency_overrides[get_admin_repository] = override_get_admin_repository
    app.dependency_overrides[get_unit_of_work] = override_get_unit_of_work
    app.dependency_overrides[get_token_hasher] = override_get_token_hasher
    app.dependency_overrides[get_user_cache] = override_get_user_cache
    app.dependency_overrides[get_task_cache] = override_get_task_cache
    app.dependency_overrides[get_role_cache] = override_get_role_cache

    # Patch the Redis rate limiter classes
    with patch.object(RedisSlidingWindowLog, '__init__', return_value=None):
        with patch.object(RedisSlidingWindowLog, 'is_allowed', mock_rate_limiter.is_allowed):
            with patch.object(RedisSlidingWindowLog, 'get_retry_after', mock_rate_limiter.get_retry_after):
                with patch.object(RedisSlidingWindowCounter, '__init__', return_value=None):
                    with patch.object(RedisSlidingWindowCounter, 'is_allowed', mock_rate_limiter.is_allowed):
                        with patch.object(RedisSlidingWindowCounter, 'get_retry_after', mock_rate_limiter.get_retry_after):
                            async with AsyncClient(
                                    transport=ASGITransport(app=app),
                                    base_url="http://test"
                            ) as ac:
                                yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def faker() -> Faker:
    """Provide a Faker instance for generating test data."""
    return fake


@pytest.fixture
async def test_role(db_session: AsyncSession) -> RoleORM:
    """Create a test role."""
    role = RoleORM(name="user")
    db_session.add(role)
    await db_session.commit()
    await db_session.refresh(role)
    return role


@pytest.fixture
async def test_admin_role(db_session: AsyncSession) -> RoleORM:
    """Create a test admin role."""
    role = RoleORM(name="admin")
    db_session.add(role)
    await db_session.commit()
    await db_session.refresh(role)
    return role


@pytest.fixture
async def test_user(db_session: AsyncSession, test_role: RoleORM) -> UserORM:
    """Create a test user."""
    user = UserORM(
        username=fake.user_name(),
        hashed_password=password_hasher.hash("TestPassword123!"),
        is_active=True,
        role_id=test_role.id
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user, ["role"])
    return user


@pytest.fixture
async def test_admin_user(db_session: AsyncSession, test_admin_role: RoleORM) -> UserORM:
    """Create a test admin user."""
    user = UserORM(
        username=fake.user_name(),
        hashed_password=password_hasher.hash("AdminPassword123!"),
        is_active=True,
        role_id=test_admin_role.id
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user, ["role"])
    return user


@pytest.fixture
async def test_task(db_session: AsyncSession, test_user: UserORM) -> TaskORM:
    """Create a test task."""
    task = TaskORM(
        title=fake.sentence(nb_words=5),
        content=fake.paragraph(nb_sentences=3),
        status=TaskStatus.todo,
        user_id=test_user.id
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)
    return task


@pytest.fixture
async def multiple_tasks(db_session: AsyncSession, test_user: UserORM) -> list[TaskORM]:
    """Create multiple test tasks."""
    tasks = []
    statuses = [TaskStatus.todo, TaskStatus.in_progress, TaskStatus.done]

    for i in range(10):
        task = TaskORM(
            title=fake.sentence(nb_words=5),
            content=fake.paragraph(nb_sentences=3),
            status=statuses[i % 3],
            user_id=test_user.id
        )
        db_session.add(task)
        tasks.append(task)

    await db_session.commit()
    for task in tasks:
        await db_session.refresh(task)

    return tasks


@pytest.fixture
def task_create_data(faker: Faker) -> dict:
    """Provide valid task creation data."""
    return {
        "title": faker.sentence(nb_words=5),
        "content": faker.paragraph(nb_sentences=3),
        "status": TaskStatus.todo
    }


@pytest.fixture
def task_update_data(faker: Faker) -> dict:
    """Provide valid task update data."""
    return {
        "title": faker.sentence(nb_words=5),
        "content": faker.paragraph(nb_sentences=3),
        "status": TaskStatus.in_progress
    }


@pytest.fixture
async def auth_headers(test_user: UserORM, db_session: AsyncSession) -> dict:
    """Provide authentication headers for a test user."""

    # Get role name from database
    result = await db_session.execute(select(RoleORM.name).where(RoleORM.id == test_user.role_id))
    role_name = result.scalar_one_or_none() or "user"

    token_service = JWTService()
    access_token = token_service.create_access_token(
        username=test_user.username,
        user_id=test_user.id,
        role=role_name
    )
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
async def admin_auth_headers(test_admin_user: UserORM, db_session: AsyncSession) -> dict:
    """Provide authentication headers for a test admin user."""

    # Get role name from database
    result = await db_session.execute(select(RoleORM.name).where(RoleORM.id == test_admin_user.role_id))
    role_name = result.scalar_one_or_none() or "admin"

    token_service = JWTService()
    access_token = token_service.create_access_token(
        username=test_admin_user.username,
        user_id=test_admin_user.id,
        role=role_name
    )
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
async def authenticated_client(client: AsyncClient, auth_headers: dict) -> AsyncClient:
    """Provide a test client with authentication headers."""
    client.headers.update(auth_headers)
    return client


@pytest.fixture
async def authenticated_admin_client(client: AsyncClient, admin_auth_headers: dict) -> AsyncClient:
    """Provide a test client with admin authentication headers."""
    client.headers.update(admin_auth_headers)
    return client
