# ToDo Service Backend API (FastAPI + PostgreSQL)

**API Version:** 0.0.1

**Status:** Development Build (not production-ready)

---

## Overview

This project implements a fully-featured backend service for managing tasks and users. It follows layer-based architecture principles, separates concerns, and mimics real-world backend systems.

**What is this project?**

The ToDo Service is a comprehensive REST API backend that provides task management functionality with robust user authentication and authorization. It serves as a practical example of modern backend development practices, demonstrating how to build scalable, maintainable, and secure web services using Python and FastAPI.

**Core Functionality:**

- **User Management**: Complete user lifecycle including registration, authentication, profile management, and account deletion
- **Task Management**: Create, read, update, and delete personal tasks with status tracking (todo, in_progress, done)
- **Admin Operations**: Administrative interface for user management, role assignment, and oversight of all user tasks
- **Authentication**: JWT-based authentication with access tokens and refresh token rotation for enhanced security
- **Authorization**: Role-based access control (RBAC) system that distinguishes between regular users and administrators
- **Data Filtering**: Advanced filtering capabilities for tasks (by status, recency) and users (by username, ID) with pagination support

**Architecture Highlights:**

The project implements a clean three-layer architecture:

- **API Layer** (`app/api/`): FastAPI routers handling HTTP requests and responses
- **Service Layer** (`app/services/`): Business logic and orchestration between repositories
- **Repository Layer** (`app/repositories/`): Data access operations using SQLAlchemy ORM

This separation ensures each layer has a single responsibility, making the codebase testable, maintainable, and scalable.

**Key goals:**

* Build a secure and scalable API following industry best practices
* Demonstrate proper backend engineering patterns and architecture
* Provide a learning resource for modern Python web development
* Implement robust authentication and authorization mechanisms
* Showcase database design and migration management with Alembic

---

## Tech Stack

* **Python 3.9+**
* **FastAPI** — high-performance async web framework
* **Uvicorn** — ASGI server
* **PostgreSQL** — relational database
* **SQLAlchemy (ORM)** — database abstraction
* **Alembic** — database migrations
* **Pydantic v2** — data validation & serialization
* **Pydantic Settings** — environment configuration
* **asyncpg** — async PostgreSQL driver
* **psycopg2-binary** — sync PostgreSQL driver for alembic
* **JWT (JSON Web Tokens)** — authentication
* **Passlib / bcrypt** — password hashing
* **python-multipart** — form/file uploads
* **Black** — code formatting
* **Pytest** — testing framework
* **Pytest-asyncio** — async test support for asyncio/FastAPI
* **Httpx** — async HTTP client for API testing
* **Faker** — fake data generator for tests
* **Pytest-cov** — test coverage reporting
* **Aiosqlite** — lightweight async SQLite database for unit tests
* **Email Validator** — email validation
* **Docker / Docker Compose** — containerization (DEV + PROD)
* **Git** — version control
* **Seed scripts** — automatic creation of roles and initial admin user

---

## Features

### Authentication & Authorization

* User registration & login
* Password hashing (bcrypt)
* JWT-based authentication (access tokens)
* Refresh token rotation
* Role-based access control (RBAC)
* Active/inactive user handling

---

### User Management

Features available to regular users:

* Create Account
* Get Account Information 
* Update Account Information 
* Delete Account  

---

### Admin Management

Functionality available only to administrators.

#### User Operations
* List Users (filtering & pagination)  
* Search Users (`username` or `id`)  
* Block / Unblock Users** — toggle `is_active` status  
* Change User Role (non-admin users only)  
* Delete User (non-admin users only)  

#### User Task Operations
* Get User Tasks — list tasks of a specific user (filtering & pagination)  
* Get User Task
* Update User Task
* Delete User Task  

#### Role Management
* Create Role  
* Get Roles 

---

### Task Management

Functionality for managing personal tasks:

* Create Task 
* Update Task 
* Delete Task 
* Change Task Status (`todo`, `in_progress`, `done`)  
* Get Tasks (filter by status / from newest)  
* Get Task

---

### Security

* Password hashing
* Protected endpoints via dependencies
* Ownership checks (users access only their data)
* Admin overrides
* Proper HTTP status codes (401 / 403)

---

### Architecture

```
ToDo_service/
├── app/                      # main application package
│   ├── application/          # application layer (DTOs, services, use cases)
│   │   ├── dto/              # Data Transfer Objects
│   │   ├── services/         # Business logic services
│   │   └── use_cases/        # Application use cases
│   ├── core/                 # configuration, settings
│   ├── domain/               # domain layer
│   │   ├── entities/         # Domain entities
│   │   ├── enums/            # Domain enums
│   │   ├── exceptions/       # Domain exceptions
│   │   ├── interfaces/       # Repository interfaces
│   │   └── value_objects/    # Value objects
│   ├── infrastructure/       # infrastructure layer
│   │   ├── background_tasks/  # Background tasks
│   │   ├── database/         # Database configuration
│   │   ├── mappers/          # ORM mappers
│   │   ├── models/           # SQLAlchemy ORM models
│   │   ├── repositories/     # Repository implementations
│   │   ├── security/         # Security implementations
│   │   └── services/         # Infrastructure services
│   ├── presentation/          # presentation layer
│   │   ├── api/              # API layer
│   │   │   ├── dependencies/ # FastAPI dependencies
│   │   │   ├── exception_handlers/ # Exception handlers
│   │   │   └── routers/      # FastAPI routers
│   │   └── schemas/         # Pydantic schemas
│   └── main.py               # FastAPI application entry point
├── tests/                    # tests for application
│   ├── api/                  # API integration tests
│   ├── factories.py          # Test data factories
│   ├── repositories/         # Repository layer tests
│   └── services/             # Service layer tests
├── scripts/                  # helper scripts (seed)
├── screenshots/              # screenshots for README.md
├── alembic.ini               # Alembic configuration
├── alembic/                  # Alembic migrations
│   └── versions/             # generated migration files
├── LICENSE                   # project license
├── README.md                 # project documentation
├── .dockerignore             # Docker ignore rules
├── .gitignore                # Git ignore rules
├── Dockerfile                # Multi-stage Dockerfile (dev + prod)
├── docker-compose.dev.yml    # Development environment
├── docker-compose.prod.yml   # Production environment
├── docker-entrypoint.sh      # Common entrypoint script
├── .env.dev                  # Development environment variables
├── .env.prod                 # Production environment variables
├── .env.example              # Template of environment variables
├── requirements.txt          # Production dependencies
└── requirements-dev.txt      # Development dependencies


```

**Principle:**
`route → service → repository → database`

---

## Database Design

### Users

* id
* username (unique)
* password (hashed)
* role_id 
* is_active

---

### Tasks

* id
* title
* content
* status (Enum)
* user_id (FK)

---

### Refresh Tokens

* id
* user_id (FK)
* token
* expires_at

---

### Roles

* id
* name


---

### User ↔ Role

* many-to-one relationship

---

## Authentication Flow

1. User logs in
2. Server validates credentials
3. JWT token is issued
4. Client sends token in headers
5. Protected endpoints validate token

---

## API Examples

### Auth

![Auth](screenshots/auth.png)

* #### POST /auth/authentication

Request:
```
Content-Type: application/x-www-form-urlencoded

username=user
password=user12345
```

Response:
```
{
    "refresh_token": "example.refresh.token",
    "access_token": "example.access.token",
    "token_type": "bearer"
}
```

* #### POST /auth/refresh

Request
```
{
  "refresh_token": "example.refresh.token"
}
```

Response:
```
{
    "refresh_token": "example.new.refresh.token",
    "access_token": "example.new.access.token",
    "token_type": "bearer"
}
```

---

### User

![User](screenshots/user.png)

* #### GET    /user/me

Request:
```
Authorization: Bearer <access_token>
```

Response:
```
{
    "username": "user",
    "id": 1,
    "is_active": true,
    "role": {
        "name": "user"
    }
}
```

* #### POST   /user/me

Request:
```
{
  "username": "user",
  "password": "user12345",
  "password_confirm": "user12345"
}
```

Response:
```
{
  "username": "user",
  "id": 1,
  "is_active": true,
  "role": {
    "name": "user"
  }
}
```

* #### PATCH  /user/me

Request:
```
Authorization: Bearer <access_token>

{
  "username": "new_user",
  "password": "user12345",
  "password_confirm": "user12345"
}
```

Response:
```
{
    "username": "new_user",
    "id": 1,
    "is_active": true,
    "role": {
        "name": "user"
    }
}
```

* #### DELETE /user/me

Request:
```
Authorization: Bearer <access_token>
```


### Tasks

![Tasks](screenshots/tasks.png)

* #### GET    /tasks/me

Request:
```
Authorization: Bearer <access_token>
```

Response:
```
[
    {
        "id": 1,
        "title": "example title",
        "content": "example content",
        "status": "todo",
        "user_id": 1
    }
]
```

* #### POST   /tasks/me

Request:
```
Authorization: Bearer <access_token>

{
  "title": "example title",
  "content": "example content",
  "status": "todo"
}
```

Response:
```
{
    "id": 1,
    "title": "example title",
    "content": "example content",
    "status": "todo",
    "user_id": 1
}
```

* #### GET    /tasks/me/{task_id}

Request:
```
Authorization: Bearer <access_token>
```

Response:
```
{
    "id": {task_id},
    "title": "example title",
    "content": "example content",
    "status": "todo",
    "user_id": 1
}
```

* #### PATCH  /tasks/me/{task_id}

Request:
```
Authorization: Bearer <access_token>

{
  "title": "example new title",
  "content": "example new content ",
  "status": "done"
}
```

Response:
```
{
    "id": {task_id},
    "title": "example new title",
    "content": "example new content ",
    "status": "done",
    "user_id": 1
}
```

* #### DELETE /tasks/me/{task_id}

Request:
```
Authorization: Bearer <access_token>
```

---

### Admin

ONLY for users with admin role

![Admin](screenshots/admin.png)

* #### GET    /admin/users 

Request:
```
Authorization: Bearer <access_token>
```

Response:
```
[
    {
        "username": "user",
        "id": 1,
        "is_active": true,
        "role": {
            "name": "user"
        }
    }
]
```

* #### GET    /admin/users/{user_id}   

Request:
```
Authorization: Bearer <access_token>
```

Response:
```
{
    "username": "user",
    "id": {user_id},
    "is_active": true,
    "role": {
        "name": "user"
    }
}
```

* #### PATCH  /admin/users/{user_id}     

Request:
```
Authorization: Bearer <access_token>

{
  "is_active": false,
  "role": "admin"
}
```

Response:
```
{
    "username": "user",
    "id": {user_id},
    "is_active": false,
    "role": {
        "name": "admin"
    }
}
```

* #### DELETE /admin/users/{user_id}     

Request:
```
Authorization: Bearer <access_token>
```

* #### GET    /admin/users/{user_id}/tasks  


Request:
```
Authorization: Bearer <access_token>
```

Response:
```
[
    {
        "id": 1,
        "title": "example title",
        "content": "example content",
        "status": "todo",
        "user_id": {user_id}
    }
]
```

* #### GET    /admin/users/{user_id}/tasks/{task_id}    

Request:
```
Authorization: Bearer <access_token>
```

Response:
```
{
    "id": {task_id},
    "title": "example title",
    "content": "example content",
    "status": "todo",
    "user_id": {user_id}}
}
```

* #### PATCH  /admin/users/{user_id}/tasks/{task_id}  

Request:
```
Authorization: Bearer <access_token>

{
  "title": "example new title",
  "content": "example new content ",
  "status": "done"
}
```

Response:
```
{
    "id": {task_id},
    "title": "example new title",
    "content": "example new content ",
    "status": "done",
    "user_id": {user_id}
}
```

* #### DELETE /admin/users/{user_id}/tasks/{task_id}

Request:
```
Authorization: Bearer <access_token>
```

* #### GET    /admin/roles         

Request:
```
Authorization: Bearer <access_token>
```

Response:
```
[
    {
        "name": "user",
        "id": 1
    },
    {
        "name": "admin",
        "id": 2
    }
]
```

* #### POST   /admin/roles     

Request:
```
Authorization: Bearer <access_token>

{
  "name": "moderator"
}
```

Response:
```
{
    "name": "moderator",
    "id": 7
}
```


---

### Filters

![Tasks_filters](screenshots/tasks_filters.png)
![Users_filters](screenshots/users_filters.png)
```
GET /tasks/me?task_status=todo
GET /tasks/me?from_newest=true
GET /tasks/me?limit=10&offset=0

GET /admin/users?username=string
GET /admin/users?limit=10&offset=0
```

---

## Running the Project

The project supports three execution modes:

**Docker DEV** — local development with hot‑reload and bind‑mount

**Docker PROD** — production-ready optimized container setup

**Manual Setup** — run without Docker using your own environment

---

## Docker Development Mode (DEV)

### Overview

The development environment uses a multi-stage Docker build with:
- Hot reload enabled for fast development
- Source code mounted as volume
- Development dependencies included
- Automatic database migrations on startup
- Seed scripts for initial data setup

### 1. Clone repository

```
git clone https://github.com/SeVeR04eK/ToDo_service.git
cd ToDo_service
```

---

### 2. Generate secret key

```
python -c "import secrets; print(secrets.token_hex(32))"
```

---

### 3. Setup environment variables

The `.env.dev` file is already provided with default values. Update the `SECRET_KEY` with your generated key:

```bash
# .env.dev
DATABASE_URL=postgresql+asyncpg://user:password@db:5432/todo_service
SECRET_KEY=your_generated_secret_key_here
FIRST_ADMIN_USERNAME=admin
FIRST_ADMIN_PASSWORD=admin123
DEBUG=true
```

---

### 4. Run development environment

```bash
docker compose -f docker-compose.dev.yml up --build
```

This will:
- Build the Docker image using the `dev` stage
- Start PostgreSQL database
- Start the FastAPI backend with hot reload
- Run database migrations automatically
- Run seed scripts (roles and admin user)

---

### 5. Access the application

- **API Documentation**: http://127.0.0.1:8000/docs
- **Database**: localhost:5432

---

### 6. Stop the environment

```bash
docker compose -f docker-compose.dev.yml down
```

To remove volumes (including database data):

```bash
docker compose -f docker-compose.dev.yml down -v
```

---

## Docker Production Mode (PROD)

### Overview

The production environment uses an optimized Docker setup with:
- Multi-stage build for minimal image size
- Production ASGI server (Gunicorn with Uvicorn workers)
- No source code volumes
- Only production dependencies
- Health checks and restart policies
- Network isolation

### 1. Clone repository

```
git clone https://github.com/SeVeR04eK/ToDo_service.git
cd ToDo_service
```

---

### 2. Setup environment variables

Create `.env.prod` with production values:

```bash
# .env.prod
DATABASE_URL=postgresql+asyncpg://user:password@db:5432/todo_service
SECRET_KEY=your_production_secret_key_minimum_32_characters
FIRST_ADMIN_USERNAME=admin
FIRST_ADMIN_PASSWORD=your_secure_admin_password
DEBUG=false
```

**⚠️ Security Notice**: In production, use proper secrets management (HashiCorp Vault, AWS Secrets Manager, etc.) instead of environment files.

---

### 3. Run production environment

```bash
docker compose -f docker-compose.prod.yml up --build -d
```

This will:
- Build the Docker image using the `prod` stage
- Start PostgreSQL with health checks
- Start FastAPI with Gunicorn (4 workers)
- Run database migrations automatically
- Configure restart policies

**Note**: Seed scripts are NOT run in production. Run them manually if needed:

```bash
docker compose -f docker-compose.prod.yml exec backend python -m scripts.seed_roles
docker compose -f docker-compose.prod.yml exec backend python -m scripts.seed_admin
```

---

### 4. Access the application

- **API Documentation**: http://127.0.0.1:8000/docs
- **Database**: localhost:5432

---

### 5. Stop the environment

```bash
docker compose -f docker-compose.prod.yml down
```

To remove volumes:

```bash
docker compose -f docker-compose.prod.yml down -v
```

---

## Manual Setup

### 1. Clone repository

```
git clone https://github.com/SeVeR04eK/ToDo_service.git
cd ToDo_service
```

---

### 2. Create virtual environment

```
python -m venv venv
source venv/bin/activate  # Linux / Mac
venv\Scripts\activate     # Windows
```

---

### 3. Install dependencies

```
pip install -r requirements.txt
```

---

### 4. Generate secret key

```
python -c "import secrets; print(secrets.token_hex(32))"
```

---

### 5. Create database

```
CREATE DATABASE todo_service;   #psql
```

---

### 6. Setup environment variables

Create `.env` file using `.env.example` template:

```
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/todo_service
SECRET_KEY=your_secret_key           
FIRST_ADMIN_USERNAME=admin
FIRST_ADMIN_PASSWORD=admin123
```

---

### 7. Run migrations

```
alembic upgrade head
```

---

### 8. Run seeds

```
python -m scripts.seed_roles
python -m scripts.seed_admin
```

---

### 9. Start server

```
uvicorn app.main:app --reload
```

---

### 10. Open docs

```
http://127.0.0.1:8000/docs
```

---

## Docker Architecture Explanation

### Multi-Stage Build

The Dockerfile uses a multi-stage build pattern:

```
base (common dependencies)
  ├── dev (development stage with hot reload)
  └── prod (production stage with Gunicorn)
```

**Why separate dev and prod?**
- **Development**: Includes dev tools, enables hot reload, mounts source code for fast iteration
- **Production**: Minimal image size, production server, no dev dependencies, optimized for performance

### Entrypoint Script

The `docker-entrypoint.sh` script:
- Runs database migrations (`alembic upgrade head`)
- Executes the command passed as arguments (`exec "$@"`)
- Uses `set -e` to fail immediately on errors

**Why no seed scripts in entrypoint?**
- Seed scripts can cause issues with multiple replicas in production
- They should be run manually or through deployment scripts
- Prevents duplicate data creation during scaling

### Environment Files

- **`.env.dev`**: Development environment variables with debug enabled
- **`.env.prod`**: Production environment variables with debug disabled
- **`.env.example`**: Template showing required variables

### Docker Compose Files

- **`docker-compose.dev.yml`**: Development configuration with volumes and hot reload
- **`docker-compose.prod.yml`**: Production configuration with health checks and restart policies

---
## Test Suite

**tests/** directory contains the comprehensive test suite for the ToDo Service FastAPI application.

### Test Structure

```
tests/
├── conftest.py              # Pytest configuration and shared fixtures
├── factories.py             # Test data factories
├── repositories/           # Repository layer tests
│   ├── test_task_repo.py
│   └── test_user_repo.py
├── services/                # Service layer tests
│   └── test_task_service.py
└── api/                     # API integration tests
    ├── test_tasks_router.py
    └── test_auth_router.py
```
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

### Test Categories

#### Unit Tests (`@pytest.mark.unit`)
- Repository layer tests
- Service layer tests
- Test business logic in isolation

#### Integration Tests (`@pytest.mark.integration`)
- API endpoint tests
- Test full request/response cycle
- Test authentication and authorization

#### Markers
- `unit`: Unit tests
- `integration`: Integration tests
- `tasks`: Task-related tests
- `auth`: Authentication-related tests
- `slow`: Slow-running tests
---

### Fixtures

#### Database Fixtures
- `db_session`: In-memory SQLite database session
- `test_engine`: Test database engine

#### User Fixtures
- `test_role`: Creates a user role
- `test_admin_role`: Creates an admin role
- `test_user`: Creates a test user
- `test_admin_user`: Creates a test admin user

#### Task Fixtures
- `test_task`: Creates a single test task
- `multiple_tasks`: Creates multiple test tasks
- `task_create_data`: Provides valid task creation data
- `task_update_data`: Provides valid task update data

#### Authentication Fixtures
- `auth_headers`: Provides authentication headers for regular user
- `admin_auth_headers`: Provides authentication headers for admin
- `authenticated_client`: Test client with user authentication
- `authenticated_admin_client`: Test client with admin authentication

#### Utility Fixtures
- `faker`: Faker instance for generating test data
- `client`: Async HTTP test client
- `event_loop`: Async event loop for tests
---

### Test Database

Tests use an in-memory SQLite database for fast, isolated testing. The database is:
- Created fresh for each test
- Dropped after each test
- Uses the same schema as the production database
---

### Coverage Goals

Target coverage: 90%+

Run coverage report:
```bash
pytest --cov=app --cov-report=term-missing --cov-report=html
```

View HTML report:
```bash
open htmlcov/index.html
```
---

### Adding New Tests

1. Create test file in appropriate directory (repositories/, services/, or api/)
2. Use appropriate markers (@pytest.mark.unit, @pytest.mark.integration, etc.)
3. Use existing fixtures where possible
4. Follow naming convention: test_<functionality>_<scenario>
5. Test both success and failure cases
---

## Key Engineering Decisions

* Separation of concerns (routes vs services vs repository)
* Dependency injection via FastAPI
* RBAC instead of hardcoded checks
* Alembic migrations instead of manual DB changes
* Explicit error handling (401 vs 403)
* Dockerized architecture for consistent development
* Automatic migrations & seed scripts on container startup
* Test isolation to ensure each test runs independently
* In‑memory database usage for fast test execution
* Fixtures and factories to reduce duplication and improve maintainability

## Why This Project Matters

This project demonstrates:

* Real-world backend architecture
* Secure authentication practices
* Database design skills
* API design and filtering
* Understanding of authorization models
* Ability to containerize applications using Docker
* Knowledge of environment variables and secrets management
* Clear and descriptive test structure
* Comprehensive testing approach covering happy paths, edge cases, and failures

## License

MIT License
