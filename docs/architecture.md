# Architecture

The application is divided into four main layers:

* **Domain** — entities, value objects, domain exceptions, and interfaces
* **Application** — use cases, services, and DTOs
* **Infrastructure** — database, repositories, security, and Unit of Work implementation
* **Presentation** — FastAPI routers, schemas, dependencies, middleware, and exception handlers

Dependencies point toward the domain layer, while infrastructure-specific implementations are injected through interfaces and dependencies.

## Project Structure

```text
app/
├── application/       # use cases, services, DTOs
├── core/              # configuration and logging
├── domain/            # entities, interfaces, value objects, exceptions and enums
├── infrastructure/    # models, mappers, background tasks, database,
│                      # repositories, security, services, UoW
├── migrations/        # migration versions
├── presentation/      # API, schemas, dependencies, middleware,
│                      # routers and exception handlers
└── main.py            # application entry point

tests/
├── api/
├── repositories/
├── services/
└── use_cases/
```

### Request Flow

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
```

---

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
