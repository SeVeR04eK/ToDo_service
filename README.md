# ToDo Service Backend API (FastAPI + PostgreSQL)

**API Version:** 0.3.0

---

## Overview

ToDo Service is a REST API for task and user management built with FastAPI and PostgreSQL.

The project focuses on backend engineering practices, including application architecture, authentication, authorization, database transactions, testing, observability, and containerization.

The API provides:

- User registration and account management
- JWT-based authentication with access and refresh tokens
- Refresh token rotation, token families, and reuse detection
- Role-Based Access Control (RBAC)
- Task management with filtering and pagination
- Administrative user and task management
- Structured JSON logging with correlation IDs
- Health checks and database connectivity monitoring
- Docker-based development and production-oriented configurations
- Unit, repository, and API/integration tests

### Architecture

The application is divided into four main layers:

- **Domain** — entities, value objects, domain exceptions, and interfaces
- **Application** — use cases, services, and DTOs
- **Infrastructure** — database, repositories, security, and Unit of Work implementation
- **Presentation** — FastAPI routers, schemas, dependencies, middleware, and exception handlers

Dependencies point toward the domain layer. Infrastructure-specific implementations are injected through interfaces and dependencies.

---

## Engineering Highlights

| Area | Implementation |
|---|---|
| Architecture | Clean Architecture, Repository, Unit of Work |
| Authentication | JWT access/refresh tokens, rotation, reuse detection |
| Authorization | Role-Based Access Control (RBAC) |
| Database | PostgreSQL, SQLAlchemy 2.0, Alembic |
| API | FastAPI, OpenAPI, validation, pagination, filtering |
| Observability | Structured JSON logging, correlation IDs, request timing |
| Security | Password hashing, ownership checks, security headers, HSTS |
| Testing | Unit, repository, and API/integration tests |
| Infrastructure | Docker, Docker Compose, multi-stage builds |

---

## Tech Stack

- **Language:** Python 3.12+
- **Framework:** FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy 2.0
- **Migrations:** Alembic
- **Validation & Configuration:** Pydantic v2, Pydantic Settings
- **Authentication:** JWT, OAuth2 Bearer
- **Testing:** Pytest, Pytest-asyncio, HTTPX
- **Logging:** structlog
- **Infrastructure:** Docker, Docker Compose
- **ASGI Server:** Uvicorn, Gunicorn
- **Version Control:** Git

---

## Features

### Authentication & Authorization

- User registration and authentication
- JWT access and refresh tokens
- Refresh token rotation
- SHA-256 hashed refresh tokens
- Token family tracking
- Refresh token reuse detection and family revocation
- Role-Based Access Control (RBAC)
- Session revocation and logout
- OAuth2-compatible Bearer authentication

### User Management

- User registration
- Account information retrieval and updates
- Password change with previous-password verification
- Account deletion
- Active/inactive account handling

### Task Management

- Create, update, retrieve, and delete tasks
- Task status management
- Ownership enforcement
- Filtering
- Pagination

### Administration

- User listing and search
- User blocking and unblocking
- Role management
- Administrative task management
- Pagination and filtering

### Observability

- Health check endpoint
- Database connectivity checks
- Structured JSON logging
- Correlation IDs
- Request duration tracking

### Security

- bcrypt password hashing
- Refresh token hashing
- Ownership checks
- RBAC protection
- Security headers
- Optional HSTS
- CORS configuration
- Request validation

---

## Middleware

The API uses middleware for cross-cutting concerns:

- **Correlation ID** — assigns a unique identifier to each request
- **Request Logging** — records HTTP requests and response duration
- **Security Headers** — adds security-related HTTP headers
- **CORS** — controls allowed cross-origin requests

Middleware is configured in `app/presentation/api/middleware/setup.py` and registered during application startup.

---

## CI

Every push and pull request runs:

- automated tests
- application checks
- Docker build verification

---

## Observability

### Structured Logging

The application uses structured JSON logging with `structlog`.

Logging includes:

- Correlation IDs for request tracing
- HTTP request information
- Request duration
- Configurable log levels

Correlation IDs allow logs belonging to the same HTTP request to be identified across application components.

---

## Project Structure

```text
app/
├── application/       # use cases, services, DTOs
├── core/              # configuration and logging
├── domain/            # entities, interfaces, value objects, exceptions and enums
├── infrastructure/    # models, mappers, background tasks, database, repositories, security, services, UoW
├── migrations/        # versions
├── presentation/      # API, schemas, dependencies, middleware, routers and exception handlers
└── main.py            # application entry point

tests/
├── api/
├── repositories/
├── services/
└── use_cases/
```

### Request flow:

                ┌─────────────────┐
                │   HTTP Request  │
                └────────┬────────┘
                         ↓
                ┌─────────────────┐
                │  FastAPI Router │
                └────────┬────────┘
                         ↓
                ┌─────────────────┐
                │     Use Cases   │
                └────────┬────────┘
                         ↓
                ┌─────────────────┐
                │     Services    │
                └────────┬────────┘
                         ↓
                ┌─────────────────┐
                │   Unit of Work  │
                └────────┬────────┘
                         ↓
                ┌─────────────────┐
                │   Repositories  │
                └────────┬────────┘
                         ↓
                ┌─────────────────┐
                │    PostgreSQL   │
                └─────────────────┘

---

## Unit of Work

The application uses the Unit of Work pattern to define transaction boundaries across repository operations.

Key characteristics:

- Services operate through a shared Unit of Work
- Repositories do not commit transactions independently
- `flush()` and `refresh()` are used for persistence within the transaction
- The Unit of Work controls commit and rollback
- Exceptions trigger automatic rollback
- Refresh token rotation is performed atomically

This keeps transaction management centralized and prevents individual repositories from controlling application-level transactions.

---

## Key Engineering Decisions

### Clean Architecture

The codebase separates domain logic from application, infrastructure, and framework-specific concerns.

### Repository Pattern

Database access is abstracted behind repository interfaces, keeping application logic independent from SQLAlchemy implementations.

### Unit of Work

Transaction boundaries are controlled at the application level, allowing multiple repository operations to be committed atomically.

### Dependency Injection

FastAPI dependencies provide infrastructure implementations to application services and use cases.

### Refresh Token Rotation

Refresh tokens are stored as SHA-256 hashes, rotated after use, grouped into token families, and revoked when reuse is detected.

### Database Migrations

Alembic is used for version-controlled database schema changes.

### Structured Logging

JSON logs with correlation IDs provide request-level traceability across application components.

---

## Database Design

The database is implemented with PostgreSQL and SQLAlchemy 2.0. Schema changes are managed through Alembic migrations.

### Users

| Column | Description |
|---|---|
| `id` | Primary key |
| `username` | Unique username |
| `password` | bcrypt password hash |
| `role_id` | Foreign key to `roles` |
| `is_active` | Account status |

### Tasks

| Column | Description |
|---|---|
| `id` | Primary key |
| `title` | Task title |
| `content` | Task content |
| `status` | Task status enum |
| `user_id` | Foreign key to `users`, indexed |

### Refresh Tokens

| Column | Description |
|---|---|
| `id` | Primary key |
| `user_id` | Token owner, indexed |
| `token_hash` | SHA-256 hash, unique and indexed |
| `family_id` | Token family identifier, indexed |
| `expires_at` | Expiration timestamp, indexed |
| `created_at` | Creation timestamp |
| `revoked_at` | Revocation timestamp |
| `replaced_by` | Replacement token reference |

### Roles

| Column | Description |
|---|---|
| `id` | Primary key |
| `name` | Unique role name |

Users have a many-to-one relationship with roles.

---

## Authentication Flow

1. User authenticates with username and password.
2. The server validates the credentials and issues:
   - short-lived JWT access token
   - long-lived refresh token
3. Only the SHA-256 hash of the refresh token is stored in PostgreSQL.
4. Protected endpoints validate the access token signature and registered claims.
5. When the access token expires, the client sends the refresh token.
6. The server:
   - revokes the previous refresh token
   - issues a new refresh token
   - keeps the same token family
7. Reuse of a revoked refresh token causes the entire token family to be revoked.
8. Logout can revoke the current session or all sessions for the user.

---

## Refresh Token Lifecycle

Refresh tokens are managed as server-side sessions rather than treated as long-lived credentials.

```text
Login
  ↓
Refresh Token Created
  ↓
Stored as SHA-256 Hash
  ↓
Client Uses Refresh Token
  ↓
Old Token Revoked
  ↓
New Token Created
  ↓
Same Token Family
```
If a previously revoked refresh token is reused:
```text
Reused Token
     ↓
Token Family Identified
     ↓
Entire Family Revoked
     ↓
Session Requires Re-authentication
```
This limits the impact of a compromised refresh token and provides server-side session revocation.

---

## API Overview

The application provides a fully documented REST API with authentication, user management, tasks, and admin endpoints.

Interactive documentation:
- Swagger UI: `/docs`
- ReDoc: `/redoc`

### Auth

![Auth](screenshots/auth.png)

**POST /auth/authentication**

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
    "token_type": "bearer",
    "expires_in": 900
}
```

**POST /auth/refresh**

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
    "token_type": "bearer",
    "expires_in": 900
}
```

**Note:** Refresh token rotation is enabled - each refresh returns a new refresh token and invalidates the old one.

### User

![User](screenshots/user.png)

**GET    /user/me**

Request:
```
Authorization: Bearer <access_token>
```

Response:
```
{
    "data": {
        "username": "user",
        "id": 1,
        "is_active": true,
        "role": {
            "name": "user"
        }
    }
}
```

### Tasks

![Tasks](screenshots/tasks.png)

**GET    /tasks/me**

Request:
```
Authorization: Bearer <access_token>
```

Response:
```
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

### Filters

![Tasks_filters](screenshots/tasks_filters.png)

```
GET /tasks/me?task_status=todo
GET /tasks/me?from_newest=true
GET /tasks/me?limit=10&offset=0
```

### **For complete endpoint documentation, see [api.md](docs/api.md)**

---

## Running the Project

The project supports three execution modes:

**Docker DEV** — local development with hot‑reload and bind‑mount
**Docker PROD** — production-oriented container configuration
**Manual Setup** — run without Docker using your own environment

**⚠️ Important**: In `app/core/config.py`, the line `ENVIRONMENT = os.getenv("ENVIRONMENT", "local")` controls which `.env` file is loaded. Change this to:
- `"dev"` to load `.env.dev`
- `"prod"` to load `.env.prod`
- `"local"` to load `.env` (or keep as default)
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

**⚠️ Important**: When running with Docker DEV mode, ensure the `DATABASE_URL` uses `db` as the hostname (not `localhost`), as the database runs in a separate Docker container within the same network.

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

### **For other execution mode look into [running.md](docs/running.md).**

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
- **Development**: Includes development dependencies, hot reload, and source-code bind mounts
- **Production-oriented**: Uses production dependencies, no source-code bind mounts, and Gunicorn with Uvicorn workers

### Entrypoint Script

The `docker-entrypoint.sh` script:
- Runs database migrations (`alembic upgrade head`)
- Runs seed scripts only when `ENVIRONMENT=dev` (roles and admin user)
- Executes the command passed as arguments (`exec "$@"`)
- Uses `set -e` to fail immediately on errors

**Why conditional seed scripts?**
- Seed scripts run automatically in development for convenience
- Seed scripts are NOT run in production to prevent issues with multiple replicas
- They should be run manually in production if needed through deployment scripts

---

## Testing

The project includes a comprehensive test suite covering API, services, repositories, and use cases.

### Running tests
```bash
pytest
pytest --cov=app --cov-report=html
```

### Test structure
```text
tests/
    api/            # API integration tests
    services/       # Unit tests (mocked dependencies)
    repositories/   # DB integration tests
    use_cases/      # Business logic tests
```

### **More detailed information is available in [testing.md](docs/testing.md).**

---

## License
MIT License