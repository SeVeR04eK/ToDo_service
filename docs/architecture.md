# Architecture

The application follows **Clean Architecture** and is divided into four main layers:

* **Domain** — entities, value objects, domain exceptions, and interfaces
* **Application** — use cases, services, DTOs, and application interfaces
* **Infrastructure** — database, repositories, security, Redis, Celery, RabbitMQ, and Unit of Work implementations
* **Presentation** — FastAPI routers, schemas, dependencies, middleware, and exception handlers

Dependencies point inward toward the domain layer. Infrastructure-specific implementations are provided through interfaces and dependency injection, keeping business logic independent from external frameworks and services.

## Project Structure

```text
app/
├── application/       # use cases, services, DTOs, interfaces
├── core/              # configuration and logging
├── domain/            # entities, interfaces, value objects, exceptions and enums
├── infrastructure/    # database, repositories, security, Redis, Celery, RabbitMQ, services and UoW
├── migrations/        # Alembic migration versions
├── presentation/      # API, schemas, dependencies, middleware, routers and exception handlers
└── main.py            # application entry point

tests/
├── api/
├── infrastructure/
├── repositories/
├── services/
└── use_cases/
```

## Request Flow

Synchronous HTTP requests follow the application layer boundaries:

```text
                ┌─────────────────┐
                │   HTTP Request  │
                └────────┬────────┘
                         ↓
                ┌─────────────────┐
                │  FastAPI Router │
                └────────┬────────┘
                         ↓
                ┌─────────────────┐
                │     Use Case    │
                └────────┬────────┘
                         ↓
                ┌─────────────────┐
                │     Service     │
                └────────┬────────┘
                         ↓
                ┌─────────────────┐
                │   Unit of Work  │
                └────────┬────────┘
                         ↓
                ┌─────────────────┐
                │   Repository    │
                └────────┬────────┘
                         ↓
                ┌─────────────────┐
                │   PostgreSQL    │
                └─────────────────┘
```

The FastAPI application handles the HTTP lifecycle, while use cases and services contain application logic. Repositories provide persistence operations through interfaces defined outside the infrastructure layer.

## Background Processing

Background processing is implemented with **Celery** and **RabbitMQ**.

The FastAPI application does not execute long-running background work inside the request lifecycle. Instead, the application publishes a Celery task to RabbitMQ and returns control to the HTTP request flow.

```text
                         ┌─────────────────┐
                         │    FastAPI      │
                         └────────┬────────┘
                                  │
                                  │ publish task
                                  ▼
                         ┌─────────────────┐
                         │ Celery Publisher│
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │    RabbitMQ     │
                         │     Broker      │
                         └────────┬────────┘
                                  │
                                  │ deliver task
                                  ▼
                         ┌─────────────────┐
                         │ Celery Worker   │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │   Celery Task   │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │ External Service│
                         │ / Database      │
                         └─────────────────┘
```

### Celery Integration

Celery is isolated inside the infrastructure layer.

Application services depend on the `MessagePublisher` interface rather than directly depending on Celery:

```text
                    Application Layer
                           │
                           │ MessagePublisher
                           ▼
              ┌─────────────────────────┐
              │ CeleryMessagePublisher  │
              └────────────┬────────────┘
                           │
                           ▼
                    Celery Task
                           │
                           ▼
                       RabbitMQ
                           │
                           ▼
                    Celery Worker
```

This keeps the application layer independent from the Celery framework. The concrete `CeleryMessagePublisher` is an infrastructure implementation injected through the application interfaces.

### Welcome Email Flow

Welcome emails are processed asynchronously after user registration:

```text
User Registration
       │
       ▼
   UserService
       │
       ▼
MessagePublisher
       │
       ▼
CeleryMessagePublisher
       │
       ▼
   RabbitMQ
       │
       ▼
Celery Worker
       │
       ▼
send_welcome_email_task
       │
       ▼
   EmailService
       │
       ▼
    SMTP Server
```

The API request does not wait for the email to be delivered.

The email task supports automatic retries with exponential backoff and jitter for failures that propagate as exceptions.

### Periodic Tasks

Periodic maintenance tasks are scheduled by **Celery Beat**.

```text
                    ┌─────────────────┐
                    │   Celery Beat   │
                    └────────┬────────┘
                             │
                             │ schedule task
                             ▼
                    ┌─────────────────┐
                    │    RabbitMQ     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Celery Worker   │
                    └────────┬────────┘
                             │
                             ▼
                clean_expired_tokens_task
                             │
                             ▼
                       PostgreSQL
```

Celery Beat is responsible only for scheduling. Task execution is performed by Celery workers.

The expired refresh-token cleanup task periodically removes expired tokens from PostgreSQL.

### Task Reliability

Celery tasks use retry and acknowledgement mechanisms to improve reliability:

* Failed email tasks can be retried automatically
* Retry backoff increases the delay between attempts
* Retry jitter prevents synchronized retry attempts
* Late acknowledgements allow tasks to be acknowledged after execution
* Worker failures can result in task redelivery

The system therefore follows an **at-least-once task delivery model**. Tasks should not be assumed to execute exactly once.

## System Architecture

The main application infrastructure can be represented as:

```text
                              ┌─────────────────┐
                              │      Client     │
                              └────────┬────────┘
                                       │ HTTP
                                       ▼
                              ┌─────────────────┐
                              │     FastAPI     │
                              └────────┬────────┘
                                       │
                 ┌─────────────────────┼─────────────────────┐
                 │                     │                     │
                 ▼                     ▼                     ▼
          ┌─────────────┐       ┌─────────────┐       ┌─────────────┐
          │ PostgreSQL  │       │    Redis    │       │  RabbitMQ   │
          │             │       │             │       │   Broker    │
          └─────────────┘       └─────────────┘       └──────┬──────┘
                                                              │
                                                              ▼
                                                       ┌─────────────┐
                                                       │   Celery    │
                                                       │   Worker    │
                                                       └──────┬──────┘
                                                              │
                                                              ▼
                                                       Background Tasks

                              ┌─────────────────┐
                              │   Celery Beat   │
                              └────────┬────────┘
                                       │
                                       ▼
                                    RabbitMQ
```

### Infrastructure Responsibilities

| Component     | Responsibility                 |
| ------------- | ------------------------------ |
| PostgreSQL    | Persistent application data    |
| Redis         | Caching and rate limiting      |
| RabbitMQ      | Celery message broker          |
| Celery Worker | Executes background tasks      |
| Celery Beat   | Schedules periodic tasks       |
| FastAPI       | HTTP API and request lifecycle |

## Unit of Work & Transactions

The application uses the **Unit of Work pattern** to define transaction boundaries across repository operations.

Key characteristics:

* Services operate through a shared Unit of Work
* Repositories do not commit transactions independently
* `flush()` and `refresh()` are used for persistence within the transaction
* The Unit of Work controls commit and rollback
* Exceptions trigger automatic rollback
* Refresh token rotation is performed atomically

This centralizes transaction management and prevents individual repositories from controlling application-level transactions.
