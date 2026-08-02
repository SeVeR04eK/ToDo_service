#!/bin/bash
set -e

# Run database migrations
alembic upgrade head

# Run seed scripts only in development environment
if [ "$ENVIRONMENT" = "dev" ]; then
    echo "Running seed scripts for development environment..."
    python -m scripts.seed_roles
    python -m scripts.seed_admin
fi

# Execute the command passed as arguments
exec "$@"
