# ToDo Service Backend API

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python\&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi\&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql\&logoColor=white)](https://www.postgresql.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00)](https://www.sqlalchemy.org/)
[![Alembic](https://img.shields.io/badge/Alembic-Migrations-333333)](https://alembic.sqlalchemy.org/)
[![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?logo=pytest\&logoColor=white)](https://pytest.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker\&logoColor=white)](https://www.docker.com/)
[![Git](https://img.shields.io/badge/Git-F05032?logo=git\&logoColor=white)](https://git-scm.com/)

**API Version:** 0.3.0

---

## Overview

ToDo Service is a REST API for task and user management built with FastAPI and PostgreSQL.

The project focuses on practical backend engineering, including application architecture, authentication and authorization, database transactions, testing, observability, security, and containerization.

The API provides:

* User registration and account management
* JWT-based authentication with access and refresh tokens
* Refresh token rotation, token families, and reuse detection
* Role-Based Access Control (RBAC)
* Task management with filtering and pagination
* Administrative user and task management
* Structured JSON logging with correlation IDs
* Health checks and database connectivity monitoring
* Docker-based development and production-oriented configurations
* Unit, repository, and API/integration tests

---

## Engineering Highlights

| Area           | Implementation                                                             |
| -------------- |----------------------------------------------------------------------------|
| Architecture   | Clean Architecture, Repository Pattern, Dependency Injection, Unit of Work |
| Authentication | JWT access/refresh tokens, rotation, reuse detection                       |
| Authorization  | Role-Based Access Control (RBAC)                                           |
| Database       | PostgreSQL, SQLAlchemy 2.0, Alembic migrations                             |
| API            | FastAPI, OpenAPI, validation, pagination, filtering                        |
| Transactions   | Unit of Work with centralized commit/rollback                              |
| Observability  | Structured JSON logging, correlation IDs, request timing                   |
| Security       | bcrypt, refresh token hashing, ownership checks, security headers, HSTS    |
| Testing        | Unit, repository, and API/integration tests                                |
| Infrastructure | Docker, Docker Compose, multi-stage builds                                 |

---

## Features

### Authentication & Authorization

* User registration and authentication
* JWT access and refresh tokens
* OAuth2-compatible Bearer authentication
* Refresh token rotation
* SHA-256 hashed refresh tokens
* Token family tracking
* Refresh token reuse detection and family revocation
* Session revocation and logout
* Role-Based Access Control (RBAC)

### User Management

* Account information retrieval and updates
* Password change with previous-password verification
* Account deletion
* Active/inactive account handling

### Task Management

* Create, update, retrieve, and delete tasks
* Task status management
* Ownership enforcement
* Filtering
* Pagination

### Administration

* User listing and search
* User blocking and unblocking
* Role management
* Administrative task management
* Pagination and filtering

### Security

* bcrypt password hashing
* Refresh token hashing
* Ownership checks
* RBAC protection
* Security headers
* Optional HSTS
* CORS configuration
* Request validation

### Observability

* Health check endpoint
* Database connectivity checks
* Structured JSON logging
* Correlation IDs
* Request duration tracking

---

## Architecture

The application is divided into four main layers:

* **Domain** — entities, value objects, domain exceptions, and interfaces
* **Application** — use cases, services, and DTOs
* **Infrastructure** — database, repositories, security, and Unit of Work implementation
* **Presentation** — FastAPI routers, schemas, dependencies, middleware, and exception handlers

Dependencies point toward the domain layer, while infrastructure-specific implementations are injected through interfaces and dependencies.

### For more detailed information, see **[docs/architecture.md](docs/architecture.md)**.

---

## Middleware

The API uses middleware for cross-cutting HTTP concerns:

* **Correlation ID** — assigns a unique identifier to each request
* **Request Logging** — records HTTP requests and response duration
* **Security Headers** — adds security-related HTTP headers
* **CORS** — controls allowed cross-origin requests

Middleware is configured in:

```text
app/presentation/api/middleware/setup.py
```

---

## Database Design

The service uses PostgreSQL with SQLAlchemy 2.0, and all schema changes are managed through Alembic migrations.
The data model includes four core entities:

Users — authentication, roles, account status

Tasks — user‑owned tasks with status tracking

Refresh Tokens — hashed tokens with rotation, families, and reuse detection

Roles — simple role definitions for RBAC

### Detailed schema definitions are available in the **[docs/database.md](docs/database.md)**.

---

## Authentication Flow

The system uses short‑lived JWT access tokens and rotating refresh tokens.
Refresh tokens are stored only as SHA‑256 hashes and rotated on every use.
Reuse of a revoked token invalidates the entire token family, and logout supports single‑session or full‑account revocation.

### Detailed information and refresh token lifecycle is available in the **[docs/authentication.md](docs/authentication.md)**.

---

## API

The application provides a REST API with authentication, user management, task management, and administrative endpoints.

Interactive documentation:

* Swagger UI: `/docs`
* ReDoc: `/redoc`

### Authentication

![Auth](screenshots/auth.png)

**POST `/auth/authentication`**

Request:

```text
Content-Type: application/x-www-form-urlencoded

username=user
password=user12345
```

Response:

```json
{
    "refresh_token": "example.refresh.token",
    "access_token": "example.access.token",
    "token_type": "bearer",
    "expires_in": 900
}
```

### Tasks

![Tasks](screenshots/tasks.png)

**GET `/tasks/me`**

Request:

```http
Authorization: Bearer <access_token>
```

Response:

```json
{
    "data": [
        {
            "id": 1,
            "title": "example title",
            "content": "example content",
            "status": "todo",
            "user_id": 1
        }
    ],
    "meta": {
        "page": 1,
        "page_size": 10,
        "total_items": 1,
        "total_pages": 1,
        "has_next": false,
        "has_previous": false
    }
}
```

### Filtering & Pagination

![Task Filters](screenshots/tasks_filters.png)

```http
GET /tasks/me?task_status=todo
GET /tasks/me?from_newest=true
GET /tasks/me?limit=10&offset=0
```

### For complete endpoint documentation, see **[docs/api.md](docs/api.md)**.

---

## Configuration

The application uses environment-based configuration with Pydantic Settings.

The `ENVIRONMENT` variable controls which `.env` file is loaded:

| Environment | File        |
| ----------- | ----------- |
| `local`     | `.env`      |
| `dev`       | `.env.dev`  |
| `prod`      | `.env.prod` |

In `app/core/config.py`, `local` is used as the default environment.

---

## Running the Project

The project supports three execution modes:

* **Docker DEV** — local development with hot reload and bind mounts
* **Docker PROD** — production-oriented container configuration
* **Manual Setup** — run without Docker using your own environment

Detailed instructions for other execution modes are available in **[docs/running.md](docs/running.md)**.

### Docker Development

The development environment uses a multi-stage Docker build with:

* Hot reload
* Source-code bind mounts
* Development dependencies
* Automatic database migrations
* Development seed scripts

### 1. Clone repository

```bash
git clone https://github.com/SeVeR04eK/ToDo_service.git
cd ToDo_service
```

### 2. Generate a secret key

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Configure environment variables

The `.env.dev` file is provided with default values. Replace `SECRET_KEY` with your generated key.

```env
DATABASE_URL=postgresql+asyncpg://user:password@db:5432/todo_service
SECRET_KEY=your_generated_secret_key_here
FIRST_ADMIN_USERNAME=admin
FIRST_ADMIN_PASSWORD=admin123
DEBUG=true
```

When running with Docker Compose, use `db` as the database hostname instead of `localhost`, because PostgreSQL runs in a separate container.

### 4. Start development environment

```bash
docker compose -f docker-compose.dev.yml up --build
```

This will:

* Build the Docker image using the `dev` stage
* Start PostgreSQL
* Start the FastAPI backend with hot reload
* Run database migrations
* Run development seed scripts

### 5. Access the application

* **Swagger UI:** http://127.0.0.1:8000/docs
* **ReDoc:** http://127.0.0.1:8000/redoc
* **Database:** localhost:5432

### 6. Stop the environment

```bash
docker compose -f docker-compose.dev.yml down
```

To remove database volumes:

```bash
docker compose -f docker-compose.dev.yml down -v
```

---

## Testing

The project includes tests for API endpoints, services, repositories, and use cases.

### Running Tests

```bash
pytest
```

With coverage:

```bash
pytest --cov=app --cov-report=html
```

### Test Structure

```text
tests/
├── api/             # API integration tests
├── services/        # Unit tests with mocked dependencies
├── repositories/    # Database integration tests
└── use_cases/      # Business logic tests
```

### CI

Every push and pull request runs:

* Automated tests
* Application checks
* Docker build verification

For more details, see **[docs/testing.md](docs/testing.md)**.

---

## License

MIT License