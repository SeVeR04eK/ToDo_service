# ToDo Service Backend API (FastAPI + PostgreSQL)

**API Version:** 0.2.0

**Status:** Production-Ready Architecture

---

## Overview

This project implements a fully-featured backend service for managing tasks and users using **Clean Architecture** and **Domain-Driven Design (DDD)** principles. It provides a production-ready foundation with proper separation of concerns, dependency inversion, and testability.

**What is this project?**

The ToDo Service is a comprehensive REST API backend that provides task management functionality with robust user authentication and authorization. It serves as a practical example of modern backend development practices, demonstrating how to build scalable, maintainable, and secure web services using Python and FastAPI with clean architecture patterns.

**Core Functionality:**

- **User Management**: Complete user lifecycle including registration, authentication, profile management, and account deletion
- **Task Management**: Create, read, update, and delete personal tasks with status tracking (todo, in_progress, done)
- **Admin Operations**: Administrative interface for user management, role assignment, and oversight of all user tasks
- **Authentication**: JWT-based authentication with access tokens and refresh token rotation for enhanced security
- **Authorization**: Role-based access control (RBAC) system that distinguishes between regular users and administrators
- **Data Filtering**: Advanced filtering capabilities for tasks (by status, recency) and users (by username, ID) with pagination support

**Architecture Highlights:**

The project implements **Clean Architecture** with strict layer separation:

- **Domain Layer** (`app/domain/`): Core business logic, entities, value objects, and interfaces
- **Application Layer** (`app/application/`): Use cases, DTOs, and application services
- **Infrastructure Layer** (`app/infrastructure/`): External concerns (database, security, repositories)
- **Presentation Layer** (`app/presentation/`): API routers, schemas, and HTTP handling

This separation ensures:
- **Dependency Inversion**: High-level modules don't depend on low-level modules
- **Testability**: Each layer can be tested in isolation with proper mocking
- **Maintainability**: Changes to infrastructure don't affect business logic
- **Scalability**: Easy to add new features without modifying existing code

**Key goals:**

* Build a secure and scalable API following Clean Architecture and DDD principles
* Demonstrate proper backend engineering patterns with production-ready structure
* Provide a learning resource for modern Python web development with best practices
* Implement robust authentication and authorization mechanisms
* Showcase database design and migration management with Alembic
* Provide comprehensive Docker setup for development and production environments

---

## Tech Stack

### Core Framework
* **Python 3.12+**
* **FastAPI** — high-performance async web framework
* **Starlette** — lightweight ASGI framework
* **Uvicorn** — ASGI server (development)
* **Gunicorn** — production ASGI server with Uvicorn workers

### Database
* **PostgreSQL** — relational database
* **SQLAlchemy 2.0** — async ORM with modern Python patterns
* **Alembic** — database migrations
* **asyncpg** — async PostgreSQL driver
* **psycopg2-binary** — sync PostgreSQL driver for migrations

### Data Validation & Configuration
* **Pydantic v2** — data validation & serialization
* **Pydantic Settings** — environment configuration with ENVIRONMENT-based file loading

### Security
* **JWT (python-jose)** — authentication tokens
* **Passlib / bcrypt** — password hashing
* **python-multipart** — form/file uploads

### Testing
* **Pytest** — testing framework
* **Pytest-asyncio** — async test support
* **Httpx** — async HTTP client for API testing
* **Faker** — fake data generator for tests
* **Pytest-cov** — test coverage reporting
* **Aiosqlite** — lightweight async SQLite for unit tests

### Development Tools
* **Black** — code formatting
* **Email Validator** — email validation
* **Docker / Docker Compose** — containerization (DEV + PROD)
* **Git** — version control

---

## Features

### Authentication & Authorization

* User registration & login
* Password hashing (bcrypt)
* JWT-based authentication with short-lived access tokens (15 minutes)
* Refresh token rotation with secure token hashing (SHA-256)
* Token families for session tracking
* Refresh token reuse detection and family revocation
* Atomic refresh operations with Unit of Work pattern
* Role-based access control (RBAC)
* Active/inactive user handling
* Null-safe role checks to prevent authentication bypasses
* OAuth2-compatible Bearer authentication with expires_in field
* Logout endpoints for token revocation (single session and all sessions)

---

### User Management

Features available to regular users:

* Create Account
* Get Account Information 
* Update Account Information 
* Delete Account  

---

### Health Monitoring

* Health check endpoint for service monitoring
* Database connectivity verification
* Service status and version information
* Degraded status reporting for database issues

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
* Weak password validating
* Protected endpoints via dependencies
* Ownership checks (users access only their data)
* Admin overrides
* Proper HTTP status codes (401 / 403)
* Security headers middleware (X-Content-Type-Options, X-Frame-Options, Referrer-Policy, Permissions-Policy)
* Optional HSTS (HTTP Strict Transport Security) for production
* Null-safe authentication checks to prevent privilege escalation

---

### Middleware

The application uses a layered middleware architecture for cross-cutting concerns:

**Middleware Order (applied in reverse order):**

1. **CorrelationIdMiddleware** - First middleware executed
   - Generates unique UUID for each incoming request
   - Binds correlation ID to structlog contextvars for request tracing
   - Automatically includes `request_id` in all logs during the request lifecycle
   - Clears contextvars after request completion

2. **RequestLoggingMiddleware** - Second middleware executed
   - Logs all HTTP requests with structured logging (JSON format)
   - Captures HTTP method, request path, status code, and duration
   - Automatic log level based on request duration:
     - INFO for requests < 1 second
     - WARNING for requests >= 1 second
   - Automatically includes correlation ID from CorrelationIdMiddleware

3. **SecurityHeadersMiddleware** - Third middleware executed
   - Adds security headers to all responses:
     - `X-Content-Type-Options: nosniff` - Prevents MIME type sniffing
     - `X-Frame-Options: DENY` - Prevents clickjacking attacks
     - `Referrer-Policy: strict-origin-when-cross-origin` - Controls referrer information
     - `Permissions-Policy: camera=(), microphone=(), geolocation=()` - Restricts browser features
   - Optionally adds HSTS header when `ENABLE_HSTS=true` (production)

4. **CORSMiddleware** - Last middleware executed (FastAPI built-in)
   - Configured via environment variables:
     - `CORS_ALLOW_ORIGINS` - Allowed origins for cross-origin requests
     - `CORS_ALLOW_METHODS` - Allowed HTTP methods
     - `CORS_ALLOW_HEADERS` - Allowed request headers
     - `CORS_ALLOW_CREDENTIALS` - Allow cookies in CORS requests

**Middleware Configuration:**

All middlewares are configured in `app/presentation/api/middleware/setup.py` and applied to the FastAPI app in `app/main.py`. The order is critical - correlation ID must be first to ensure all logs include the request identifier.

---

### Logging

* Structured logging with JSON format using structlog
* Request/response logging middleware with correlation IDs
* Automatic log level based on request duration (info for <1s, warning for >=1s)
* Configurable log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
* Context-aware logging with request tracking across application layers
- HTTP method
- Request path
- Status code
- Request duration in milliseconds
- Correlation ID for request tracing

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
│   │   ├── config/           # Application configuration and environment settings
│   │   ├── logging/          # Logging setup: formatters, handlers, log configuration
│   ├── domain/               # domain layer
│   │   ├── entities/         # Domain entities
│   │   ├── enums/            # Domain enums
│   │   ├── exceptions/       # Domain exceptions
│   │   ├── interfaces/       # Repository and Unit of Work interfaces
│   │   └── value_objects/    # Value objects
│   ├── infrastructure/       # infrastructure layer
│   │   ├── background_tasks/  # Background tasks
│   │   ├── database/         # Database configuration
│   │   ├── mappers/          # ORM mappers
│   │   ├── models/           # SQLAlchemy ORM models
│   │   ├── repositories/     # Repository implementations
│   │   ├── security/         # Security implementations
│   │   ├── services/         # Infrastructure services
│   │   └── unit_of_work/     # Unit of Work implementation
│   ├── migrations/           # alembic migrations
│   ├── presentation/         # presentation layer
│   │   ├── api/              # API layer
│   │   │   ├── dependencies/ # FastAPI dependencies (including UoW)
│   │   │   ├── middleware/   # Request, logging, security, CORS middlewares
│   │   │   ├── routers/      # FastAPI routers
│   │   │   └── schemas/      # Pydantic schemas
│   │   └── exception_handlers/ # Exception handlers
│   └── main.py               # FastAPI application entry point
├── tests/                    # tests for application
│   ├── api/                  # API integration tests
│   ├── factories.py          # Test data factories
│   ├── repositories/         # Repository layer tests
│   ├── services/             # Service layer tests
│   └── use_cases/            # Use case layer tests
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
├── .env.dev                  # Development environment variables (template)
├── .env.prod                 # Production environment variables (template)
├── requirements.txt          # Production dependencies
└── requirements-dev.txt      # Development dependencies


```

**Principle:**
`route → use case → service → unit_of_work → repository → database`

**Transaction Flow with Unit of Work:**
- Services inject `UnitOfWork` instead of individual repositories
- Repositories use `flush()` and `refresh()` instead of `commit()`
- Services call `unitOfWork.commit()` to persist changes atomically
- Automatic rollback on exceptions via async context manager

---

## Unit of Work Pattern

The application implements the **Unit of Work (UoW)** pattern to manage transactions and ensure data consistency across multiple repository operations.

### Key Benefits

- **Atomic Operations**: Multiple repository operations can be committed together or rolled back as a unit
- **Concurrency Safety**: Refresh token consumption is atomic, preventing race conditions
- **Centralized Transaction Control**: Application layer controls transaction boundaries
- **Testability**: Easier to test transactional behavior with explicit commit/rollback

---

## Configuration Management

The application uses **environment-based configuration** with Pydantic Settings:

- **ENVIRONMENT variable**: Controls which `.env` file is loaded (`.env.dev` or `.env.prod`)
- **Development**: Uses `.env.dev` with debug mode enabled
- **Production**: Uses `.env.prod` with debug mode disabled
- **Validation**: Settings are validated on startup (secret key length, password strength, URL format)

Configuration is managed in `app/core/config.py` with automatic environment file selection based on the `ENVIRONMENT` variable.

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
* user_id (FK, indexed)

---

### Refresh Tokens

* id
* user_id (FK, indexed)
* token_hash (unique, indexed) - SHA-256 hash of the refresh token
* family_id (indexed) - UUID for token family tracking
* expires_at (indexed)
* created_at
* revoked_at (indexed, nullable)
* replaced_by (FK to refresh_tokens.id, nullable)

---

### Roles

* id
* name


---

### User ↔ Role

* many-to-one relationship

---

## Authentication Flow

1. User logs in with username/password
2. Server validates credentials and issues:
   - Short-lived access token (15 minutes) with JWT claims (sub, id, role, exp, iat, iss, aud)
   - Long-lived refresh token (7 days) with secure SHA-256 hash stored in database
   - Token family ID for session tracking
3. Client sends access token in Authorization header for API requests
4. Protected endpoints validate JWT signature, algorithm, expiration, issuer, and audience
5. When access token expires, client uses refresh token to get new tokens:
   - Old refresh token is revoked (token rotation)
   - New refresh token is issued with same family ID
   - If old token is reused, entire family is revoked (security measure)
6. Logout endpoints revoke refresh tokens (single session or all sessions)

---

## API Examples

### Health Check

* #### GET /health

Request:
```
GET /health
```

Response:
```
{
    "status": "healthy",
    "timestamp": "2026-08-15T12:00:00.000000",
    "service": "ToDo Service API",
    "version": "0.2.0",
    "database": {
        "status": "healthy",
        "error": null
    }
}
```

**Note:** Use this endpoint for service monitoring and health checks in production environments.

---

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
    "token_type": "bearer",
    "expires_in": 900
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
    "token_type": "bearer",
    "expires_in": 900
}
```

**Note:** Refresh token rotation is enabled - each refresh returns a new refresh token and invalidates the old one.

* #### POST /auth/logout

Request:
```
{
  "refresh_token": "example.refresh.token"
}
```

Response:
```
204 No Content
```

**Note:** Revokes the current refresh token session.

* #### POST /auth/logout-all

Request:
```
Authorization: Bearer <access_token>
```

Response:
```
204 No Content
```

**Note:** Revokes all refresh token sessions for the authenticated user.

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
    "data": {
        "username": "new_user",
        "id": 1,
        "is_active": true,
        "role": {
            "name": "user"
        }
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
    "data": {
        "id": 1,
        "title": "example title",
        "content": "example content",
        "status": "todo",
        "user_id": 1
    }
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
    "data": {
        "id": {task_id},
        "title": "example title",
        "content": "example content",
        "status": "todo",
        "user_id": 1
    }
}
```

* #### PATCH  /tasks/me/{task_id}

Request:
```
Authorization: Bearer <access_token>

{
  "title": "example new title",
  "content": "example new content",
  "status": "done"
}
```

Response:
```
{
    "data": {
        "id": {task_id},
        "title": "example new title",
        "content": "example new content",
        "status": "done",
        "user_id": 1
    }
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

Response (paginated list):
```
{
    "data": [
        {
            "username": "user",
            "id": 1,
            "is_active": true,
            "role": {
                "name": "user"
            }
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

Response (single user when filtered by username):
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

**Important:** When filtering by `username`, pagination parameters (`limit` and `offset`) are **not allowed** and will result in an `InvalidPaginationParameters` exception. This is because username filtering returns a single user, making pagination meaningless.

* #### GET    /admin/users/{user_id}   

Request:
```
Authorization: Bearer <access_token>
```

Response:
```
{
    "data": {
        "username": "user",
        "id": {user_id},
        "is_active": true,
        "role": {
            "name": "user"
        }
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
    "data": {
        "username": "user",
        "id": {user_id},
        "is_active": false,
        "role": {
            "name": "admin"
        }
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
{
    "data": [
        {
            "id": 1,
            "title": "example title",
            "content": "example content",
            "status": "todo",
            "user_id": {user_id}
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

* #### GET    /admin/users/{user_id}/tasks/{task_id}    

Request:
```
Authorization: Bearer <access_token>
```

Response:
```
{
    "data": {
        "id": {task_id},
        "title": "example title",
        "content": "example content",
        "status": "todo",
        "user_id": {user_id}
    }
}
```

* #### PATCH  /admin/users/{user_id}/tasks/{task_id}  

Request:
```
Authorization: Bearer <access_token>

{
  "title": "example new title",
  "content": "example new content",
  "status": "done"
}
```

Response:
```
{
    "data": {
        "id": {task_id},
        "title": "example new title",
        "content": "example new content",
        "status": "done",
        "user_id": {user_id}
    }
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
{
    "data": [
        {
            "name": "user",
            "id": 1
        },
        {
            "name": "admin",
            "id": 2
        }
    ]
}
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
    "data": {
        "name": "moderator",
        "id": 7
    }
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

### Response Format

All successful API responses follow a consistent wrapped format for better API contract consistency and future extensibility.

**Single Item Response (DataResponse[T]):**
```
{
  "data": {
    "id": 1,
    "username": "john_doe",
    "is_active": true,
    "role": {
      "name": "user"
    }
  }
}
```

**List Response (ListResponse[T]):**
```
{
  "data": [
    {
      "id": 1,
      "name": "admin"
    },
    {
      "id": 2,
      "name": "user"
    }
  ]
}
```

**Paginated Response (PaginatedResponse[T]):**
```
{
  "data": [],
  "meta": {
    "page": 1,
    "page_size": 20,
    "total_items": 157,
    "total_pages": 8,
    "has_next": true,
    "has_previous": false
  }
}
```

---

### Pagination

All list endpoints that support pagination return a consistent paginated response format with `data` and `meta` fields.

**Pagination Parameters:**
- `limit`: Number of items per page (default: 10, max: 100)
- `offset`: Number of items to skip (for pagination navigation)

**Pagination Response Fields:**
- `data`: Array of items for the current page
- `meta.page`: Current page number (1-indexed)
- `meta.page_size`: Number of items per page
- `meta.total_items`: Total number of items matching the query
- `meta.total_pages`: Total number of pages available
- `meta.has_next`: Whether there is a next page
- `meta.has_previous`: Whether there is a previous page

**Note:** Filtering affects only the `data` list and `total_items`/`total_pages` counts.

---

## Running the Project

The project supports three execution modes:

**Docker DEV** — local development with hot‑reload and bind‑mount

**Docker PROD** — production-ready optimized container setup

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

Use `.env.dev` as a template for local development:

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
- Runs seed scripts only when `ENVIRONMENT=dev` (roles and admin user)
- Executes the command passed as arguments (`exec "$@"`)
- Uses `set -e` to fail immediately on errors

**Why conditional seed scripts?**
- Seed scripts run automatically in development for convenience
- Seed scripts are NOT run in production to prevent issues with multiple replicas
- They should be run manually in production if needed through deployment scripts

### Environment Files

- **`.env.dev`**: Development environment variables with debug enabled (template)
- **`.env.prod`**: Production environment variables with debug disabled (template)

### Docker Compose Files

- **`docker-compose.dev.yml`**: Development configuration with volumes and hot reload
- **`docker-compose.prod.yml`**: Production configuration with health checks and restart policies

---
## Test Suite

**tests/** directory contains the comprehensive test suite for the ToDo Service FastAPI application, organized by architectural layers.

### Test Structure

```
tests/
├── conftest.py              # Pytest configuration and shared fixtures
├── factories.py             # Test data factories
├── api/                     # API integration tests (real dependencies)
│   ├── test_admin_router.py
│   ├── test_auth_router.py
│   ├── test_tasks_router.py
│   └── test_user_router.py
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

### Test Strategy

- **Unit Tests** (services, use_cases): Mock dependencies using `AsyncMock(spec=Interface)` for isolated testing
- **Integration Tests** (repositories, API): Use real database sessions with SQLite in-memory
- **Test Coverage**: 97% coverage across all layers
- **185 Tests**: Comprehensive test suite covering success paths, edge cases, and error scenarios
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
- Service layer tests (mocked repositories)
- Use case layer tests (mocked dependencies)
- Test business logic in isolation

#### Integration Tests (`@pytest.mark.integration`)
- API endpoint tests (real dependencies with overrides)
- Repository layer tests (real database)
- Test full request/response cycle
- Test authentication and authorization

#### Markers
- `unit`: Unit tests
- `integration`: Integration tests
- `tasks`: Task-related tests
- `auth`: Authentication-related tests
- `slow`: Slow-running tests
---

## OpenAPI Documentation

The API includes comprehensive OpenAPI documentation with detailed descriptions:

- **Interactive Swagger UI**: Available at `/docs` endpoint
- **ReDoc**: Available at `/redoc` endpoint
- **Schema Documentation**: All endpoints include request/response schemas with field descriptions
- **Authentication**: Bearer token authentication documented in security schemes
- **Error Responses**: Domain exceptions are properly documented with status codes
- **Example Values**: Request/response examples for all endpoints

The documentation is auto-generated from Pydantic schemas and FastAPI route decorators, ensuring it stays in sync with the codebase.

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
* Null-safe authentication checks to prevent security vulnerabilities
* Connection pooling with health checks for database reliability
* Health monitoring endpoint for production observability

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
