#!/bin/bash

alembic upgrade head
python -m scripts.seed_roles.py
python -m scripts.seed_admin.py

exec "$@"
