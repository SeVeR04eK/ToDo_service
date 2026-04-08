"""Rename title column in tasks table.

Revision ID: 3c24d699c16c
Revises: 31e96281b70c
Create Date: 2026-04-08 21:18:45.010743

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "3c24d699c16c"
down_revision: Union[str, Sequence[str], None] = "31e96281b70c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column("tasks", "name", new_column_name="title")
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column("tasks", "title", new_column_name="name")
