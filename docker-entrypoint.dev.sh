#!/bin/bash

alembic upgrade head
python -m scripts.seed_roles
python -m scripts.seed_admin

exec "$@"
