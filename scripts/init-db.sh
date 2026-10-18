#!/bin/bash
set -e

echo "Running database migrations..."
alembic upgrade head

if [ "$ENVIRONMENT" = "dev" ]; then
    echo "Running seed scripts for development environment..."

    python -m scripts.seed_roles
    python -m scripts.seed_admin
fi

echo "Database initialization completed."