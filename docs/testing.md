# Test Suite

**tests/** directory contains the comprehensive test suite for the ToDo Service FastAPI application, organized by architectural layers.

## Test Structure

```
tests/
├── conftest.py              # Pytest configuration and shared fixtures
├── factories.py             # Test data factories
├── api/                     # API integration tests (real dependencies)
│   ├── test_admin_router.py
│   ├── test_auth_router.py
│   ├── test_tasks_router.py
│   └── test_user_router.py
├── infrastructure/          # Infrastructure layer tests (real dependencies)
│   └── test_password_validator.py
├── repositories/            # Repository layer tests (real database)
│   ├── test_admin_repo.py
│   ├── test_task_repo.py
│   └── test_user_repo.py
├── services/                # Service layer tests (mocked repositories)
│   ├── test_admin_service.py
│   ├── test_auth_service.py
│   ├── test_task_service.py
│   └── test_user_service.py
└── use_cases/               # Use case layer tests (mocked dependencies)
    └── test_authenticate_user.py
```

## Test Strategy

- **Unit Tests** (services, use_cases): Mock dependencies using `AsyncMock(spec=Interface)` for isolated testing
- **API and repository tests**: Use isolated in-memory SQLite database sessions
---

### Running Tests

#### Run all tests:
```bash
pytest
```

#### Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

#### Run specific test file:
```bash
pytest tests/repositories/test_task_repo.py
```

#### Run specific test class:
```bash
pytest tests/repositories/test_task_repo.py::TestTaskRepository
```

#### Run specific test:
```bash
pytest tests/repositories/test_task_repo.py::TestTaskRepository::test_create_task_success
```

#### Run by marker:
```bash
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m tasks         # Task-related tests only
pytest -m auth          # Authentication tests only
```

#### Run with verbose output:
```bash
pytest -v
```
---

## Test Categories

### Unit Tests (`@pytest.mark.unit`)
- Service layer tests (mocked repositories)
- Use case layer tests (mocked dependencies)
- Test business logic in isolation

### Integration Tests (`@pytest.mark.integration`)
- API endpoint tests (real dependencies with overrides)
- Repository layer tests (real database)
- Test full request/response cycle
- Test authentication and authorization

### Markers
- `unit`: Unit tests
- `integration`: Integration tests
- `tasks`: Task-related tests
- `auth`: Authentication-related tests
- `slow`: Slow-running tests
---

## Fixtures

### Database Fixtures
- `db_session`: In-memory SQLite database session
- `test_engine`: Test database engine

### User Fixtures
- `test_role`: Creates a user role
- `test_admin_role`: Creates an admin role
- `test_user`: Creates a test user
- `test_admin_user`: Creates a test admin user

### Task Fixtures
- `test_task`: Creates a single test task
- `multiple_tasks`: Creates multiple test tasks
- `task_create_data`: Provides valid task creation data
- `task_update_data`: Provides valid task update data

### Authentication Fixtures
- `auth_headers`: Provides authentication headers for regular user
- `admin_auth_headers`: Provides authentication headers for admin
- `authenticated_client`: Test client with user authentication
- `authenticated_admin_client`: Test client with admin authentication

### Utility Fixtures
- `faker`: Faker instance for generating test data
- `client`: Async HTTP test client
- `event_loop`: Async event loop for tests
---

## Test Database

API and repository tests use an in-memory SQLite database to keep the test suite fast and isolated.

The test database is:
- Created fresh for the test suite
- Isolated from the development database
- Configured using the application's SQLAlchemy models
---

## Coverage 

Latest coverage: 93%

Run coverage report:
```bash
pytest --cov=app --cov-report=term-missing --cov-report=html
```

View HTML report:
```bash
open htmlcov/index.html
```

---

## Adding New Tests

1. Create test file in appropriate directory (repositories/, services/, or api/)
2. Use appropriate markers (@pytest.mark.unit, @pytest.mark.integration, etc.)
3. Use existing fixtures where possible
4. Follow naming convention: test_<functionality>_<scenario>
5. Test both success and failure cases
---

## Docker Architecture

The Dockerfile uses a multi-stage build:

```text
base
├── dev
└── prod
```

### Development Stage

* Development dependencies
* Hot reload
* Source-code bind mounts

### Production Stage

* Production dependencies
* No source-code bind mounts
* Gunicorn with Uvicorn workers

### Entrypoint

The `docker-entrypoint.sh` script:

* Runs database migrations with `alembic upgrade head`
* Runs seed scripts when `ENVIRONMENT=dev`
* Executes the configured application command with `exec "$@"`
* Uses `set -e` to fail immediately on errors

Seed scripts are not executed in production to avoid automatic data modification when multiple replicas are running. They can be executed manually through deployment procedures when required.
