import pytest
import asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient, ASGITransport
from faker import Faker
from sqlalchemy import select

from app.main import app
from app.models import Base
from app.models.users_model import User as UserORM
from app.models.roles_model import Role as RoleORM
from app.models.tasks_model import Task as TaskORM
from app.security import create_access_token
from app.utils import hash_password
from app.domain.enums import TaskStatus

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
async def client(db_session: AsyncSession) -> AsyncGenerator:
    """Create a test client with database session override."""
    from app.db import get_session

    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

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
        hashed_password=hash_password("TestPassword123!"),
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
        hashed_password=hash_password("AdminPassword123!"),
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

    access_token = create_access_token(
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

    access_token = create_access_token(
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
