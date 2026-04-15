"""Setting default category for tasks

Revision ID: 38569b944b97
Revises: 1a4d63d2d9db
Create Date: 2026-04-15 21:05:41.799759

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "38569b944b97"
down_revision: Union[str, Sequence[str], None] = "1a4d63d2d9db"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "tasks",
        "category_id",
        existing_type=sa.INTEGER(),
        server_default="1",
        existing_nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "tasks",
        "category_id",
        existing_type=sa.INTEGER(),
        server_default=None,
        existing_nullable=False,
    )
