#!/bin/bash

alembic upgrade head
python scripts/seed_roles.py
python scripts/seed_admin.py

exec "$@"
