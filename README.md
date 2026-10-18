# ToDo Service Backend API

> Production-oriented REST API for task and user management,
> built with FastAPI, PostgreSQL, Redis, RabbitMQ, and Celery.

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python\&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi\&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql\&logoColor=white)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/Nginx-009639?logo=nginx&logoColor=white)](https://nginx.org/)
[![Redis](https://img.shields.io/badge/Redis-DC382D?logo=redis\&logoColor=white)](https://redis.io/)
[![RabbitMQ](https://img.shields.io/badge/RabbitMQ-FF6600?logo=rabbitmq&logoColor=white)](https://www.rabbitmq.com/)
[![Celery](https://img.shields.io/badge/Celery-37814A?logo=celery&logoColor=white)](https://docs.celeryq.dev/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00)](https://www.sqlalchemy.org/)
[![Alembic](https://img.shields.io/badge/Alembic-Migrations-333333)](https://alembic.sqlalchemy.org/)
[![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?logo=pytest\&logoColor=white)](https://pytest.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker\&logoColor=white)](https://www.docker.com/)
[![Git](https://img.shields.io/badge/Git-F05032?logo=git\&logoColor=white)](https://git-scm.com/)

**API Version:** 0.6.0

---

## Overview

ToDo Service is a production-oriented REST API for task and user management,
built with FastAPI and a PostgreSQL-based backend, with Redis, RabbitMQ,
Celery, and Nginx for caching, background processing, and infrastructure.

The project demonstrates:

- Clean Architecture and dependency inversion
- JWT authentication with refresh-token rotation and reuse detection
- Redis caching and distributed rate limiting
- Asynchronous background processing with Celery and RabbitMQ
- Periodic task scheduling with Celery Beat
- Reverse proxy, HTTPS termination, and load balancing with Nginx
- Automated testing and structured observability
- Docker-based development and deployment

---

## Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Database Design](#database)
- [Authentication Flow](#authentication-flow)
- [API](#api)
- [Configuration](#configuration)
- [Running the Project](#running-the-project)
- [Testing](#testing)
- [Documentation](#documentation)
- [License](#license)

---

## Engineering Highlights

| Area             | Implementation                                                             |
| ---------------- | -------------------------------------------------------------------------- |
| Architecture     | Clean Architecture, Repository Pattern, Dependency Injection, Unit of Work |
| Authentication   | JWT access/refresh tokens, rotation, reuse detection                       |
| Authorization    | Role-Based Access Control (RBAC)                                           |
| Database         | PostgreSQL, SQLAlchemy 2.0, Alembic migrations                             |
| Caching          | Redis-based application caching                                            |
| Rate Limiting    | Redis sliding window log and counter algorithms                            |
| Async Processing | Celery workers with RabbitMQ as the message broker                         |
| Scheduling       | Celery Beat for periodic task scheduling                                   |
| Reliability      | Automatic retries, exponential backoff, retry jitter, late acknowledgments |
| Transactions     | Unit of Work with centralized commit/rollback                              |
| Observability    | Structured JSON logging, correlation IDs, request timing                   |
| Security         | bcrypt, refresh token hashing, ownership checks, security headers, HSTS    |
| Testing          | Unit, repository, API/integration, and infrastructure tests                |
| Infrastructure   | Docker, Docker Compose, multi-stage builds                                 |
| Reverse Proxy | Nginx, HTTPS termination, reverse proxy, load balancing |

---

## Features

### Authentication & Authorization

- User registration and authentication
- JWT access and refresh tokens
- Refresh token rotation and reuse detection
- Session revocation and logout
- Role-Based Access Control (RBAC)

### User & Task Management

- Account management and password changes
- Account activation and deletion
- Task CRUD with ownership enforcement
- Filtering and pagination

### Administration

- User listing and search
- User blocking and unblocking
- Role management
- Administrative task management

### Security

- bcrypt password hashing
- Hashed refresh tokens
- Security headers and CORS
- Request validation

### Background Processing

- Asynchronous welcome email delivery
- Idempotent email processing
- Automatic retries with backoff and jitter
- Periodic expired-token cleanup with Celery Beat

---


## Architecture

The application is divided into four main layers:

* **Domain** — entities, value objects, domain exceptions, and interfaces
* **Application** — use cases, services, and DTOs
* **Infrastructure** — database, repositories, security, Redis (caching and rate limiting), Celery, RabbitMQ, and Unit of Work implementation
* **Presentation** — FastAPI routers, schemas, dependencies, middleware, and exception handlers

Dependencies point toward the domain layer, while infrastructure-specific implementations are injected through interfaces and dependencies.

### For more detailed information, see **[docs/architecture.md](docs/architecture.md)**.

---

## Database

The service uses PostgreSQL with SQLAlchemy 2.0, and schema changes
are managed through Alembic migrations.

### Detailed schema definitions are available in the **[docs/database.md](docs/database.md)**.

---

## Authentication Flow

The system uses short-lived JWT access tokens and rotating refresh tokens.

Refresh tokens are stored as SHA-256 hashes and rotated on every use.
Reuse of a revoked token invalidates the entire token family.

### Detailed information and refresh token lifecycle is available in the **[docs/authentication.md](docs/authentication.md)**.

---

## API

The service provides REST endpoints for:

- Authentication and session management
- User management
- Task management
- Administrative operations
- Health monitoring

Interactive documentation:

- Swagger UI: `/docs`
- ReDoc: `/redoc`

### API Examples: 
![Authentication](screenshots/auth.png)

![Tasks](screenshots/tasks.png)

![Task Filters](screenshots/tasks_filters.png)

### For complete endpoint documentation, request/response examples, filters, pagination, and response formats, see **[docs/api.md](docs/api.md)**.

---

## Documentation

| Document | Description |
|----------|-------------|
| [Architecture](docs/architecture.md) | Application architecture and design principles |
| [Authentication](docs/authentication.md) | JWT and refresh-token lifecycle |
| [Database](docs/database.md) | Database schema and relationships |
| [API](docs/api.md) | API endpoints and usage |
| [Running](docs/running.md) | Development and deployment instructions |
| [Testing](docs/testing.md) | Testing strategy and test execution |
| [Changelog](docs/changelog.md) | Project history of changes |

---

## Running the Project

The project supports three execution modes:

* **Docker DEV** — local development with hot reload and bind mounts
* **Docker PROD** — production-oriented container configuration
* **Manual Setup** — run the application without Docker

In `app/core/config.py`, `local` is used as the default environment.

### Quick Start

Clone the repository:

```bash
git clone https://github.com/SeVeR04eK/ToDo_service.git
cd ToDo_service
```

Generate a secret key:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Configure `.env.dev` and replace the default `SECRET_KEY` with the generated value.

Start the development environment:

```bash
docker compose -f docker-compose.dev.yml up --build
```

The development environment starts:

- Nginx
- FastAPI
- PostgreSQL
- Redis
- RabbitMQ
- Celery Worker
- Celery Beat

Database migrations and development seed scripts are executed automatically.

### Services

| Service | Address |
|---------|---------|
| API / Swagger UI | `https://localhost/docs` |
| ReDoc | `https://localhost/redoc` |
| RabbitMQ Management UI | `http://127.0.0.1:15672` |

When running with Docker Compose, use the service names `db` and `redis` as hostnames inside the application configuration instead of `localhost`.

### Stopping the Development Environment

```bash
docker compose -f docker-compose.dev.yml down
```

To remove the database volume as well:

```bash
docker compose -f docker-compose.dev.yml down -v
```

### Detailed instructions for Docker PROD, manual installation, environment variables, database setup, migrations, and deployment are available in **[docs/running.md](docs/running.md)**.

---

## Testing

The project includes tests for API endpoints, services, repositories,
use cases, and Celery background tasks.

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
├── infrastructure/  # Infrastructure tests
├── services/        # Unit tests with mocked dependencies
├── repositories/    # Database integration tests
└── use_cases/      # Business logic tests
```

### CI

Every push and pull request runs:

* Automated tests
* Application checks
* Docker build verification

### For more details, see **[docs/testing.md](docs/testing.md)**.

---

## License

MIT License