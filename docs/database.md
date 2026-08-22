# Database Design

The database uses PostgreSQL with SQLAlchemy 2.0. Schema changes are managed through Alembic migrations.

## Users

| Column      | Description            |
| ----------- | ---------------------- |
| `id`        | Primary key            |
| `username`  | Unique username        |
| `password`  | bcrypt password hash   |
| `role_id`   | Foreign key to `roles` |
| `is_active` | Account status         |

## Tasks

| Column    | Description                     |
| --------- | ------------------------------- |
| `id`      | Primary key                     |
| `title`   | Task title                      |
| `content` | Task content                    |
| `status`  | Task status enum                |
| `user_id` | Foreign key to `users`, indexed |

## Refresh Tokens

| Column        | Description                      |
| ------------- | -------------------------------- |
| `id`          | Primary key                      |
| `user_id`     | Token owner, indexed             |
| `token_hash`  | SHA-256 hash, unique and indexed |
| `family_id`   | Token family identifier, indexed |
| `expires_at`  | Expiration timestamp, indexed    |
| `created_at`  | Creation timestamp               |
| `revoked_at`  | Revocation timestamp             |
| `replaced_by` | Replacement token reference      |

## Roles

| Column | Description      |
| ------ | ---------------- |
| `id`   | Primary key      |
| `name` | Unique role name |

Users have a many-to-one relationship with roles.