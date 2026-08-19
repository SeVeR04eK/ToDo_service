"""add refresh token hashing and families

Revision ID: cb7197378bc8
Revises: eaf949916456
Create Date: 2026-08-16 22:13:39.453979
"""

from typing import Sequence, Union

import hashlib
import uuid

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import table, column


# revision identifiers, used by Alembic.
revision: str = "cb7197378bc8"
down_revision: Union[str, Sequence[str], None] = "eaf949916456"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns as nullable first because existing rows need
    # to be migrated before we can make them NOT NULL.
    op.add_column(
        "refresh_tokens",
        sa.Column("token_hash", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "refresh_tokens",
        sa.Column("family_id", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "refresh_tokens",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )
    op.add_column(
        "refresh_tokens",
        sa.Column(
            "revoked_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )
    op.add_column(
        "refresh_tokens",
        sa.Column(
            "replaced_by",
            sa.Integer(),
            nullable=True,
        ),
    )

    # Temporary table representation used for data migration.
    refresh_tokens = table(
        "refresh_tokens",
        column("id", sa.Integer),
        column("token", sa.String),
        column("token_hash", sa.String),
        column("family_id", sa.String),
        column("created_at", sa.DateTime(timezone=True)),
    )

    connection = op.get_bind()

    # Migrate existing refresh tokens.
    result = connection.execute(
        sa.select(
            refresh_tokens.c.id,
            refresh_tokens.c.token,
        )
    )

    for row in result:
        token_hash = hashlib.sha256(row.token.encode()).hexdigest()
        family_id = str(uuid.uuid4())

        connection.execute(
            refresh_tokens.update()
            .where(refresh_tokens.c.id == row.id)
            .values(
                token_hash=token_hash,
                family_id=family_id,
                created_at=sa.func.now(),
            )
        )

    # Existing data has now been migrated.
    op.alter_column(
        "refresh_tokens",
        "token_hash",
        nullable=False,
    )
    op.alter_column(
        "refresh_tokens",
        "family_id",
        nullable=False,
    )
    op.alter_column(
        "refresh_tokens",
        "created_at",
        nullable=False,
    )

    # The old plaintext token uniqueness constraint is no longer needed.
    op.drop_constraint(
        op.f("refresh_tokens_token_key"),
        "refresh_tokens",
        type_="unique",
    )

    # Add indexes.
    op.create_index(
        "ix_refresh_tokens_token_hash",
        "refresh_tokens",
        ["token_hash"],
        unique=True,
    )
    op.create_index(
        "ix_refresh_tokens_family_id",
        "refresh_tokens",
        ["family_id"],
        unique=False,
    )
    op.create_index(
        "ix_refresh_tokens_revoked_at",
        "refresh_tokens",
        ["revoked_at"],
        unique=False,
    )

    # Self-referencing relationship for token rotation.
    op.create_foreign_key(
        "fk_refresh_tokens_replaced_by",
        "refresh_tokens",
        "refresh_tokens",
        ["replaced_by"],
        ["id"],
        ondelete="SET NULL",
    )

    # Remove plaintext refresh tokens.
    op.drop_column("refresh_tokens", "token")


def downgrade() -> None:
    # WARNING:
    # Original plaintext refresh tokens cannot be restored from hashes.

    op.add_column(
        "refresh_tokens",
        sa.Column(
            "token",
            sa.VARCHAR(),
            nullable=True,
        ),
    )

    op.drop_constraint(
        "fk_refresh_tokens_replaced_by",
        "refresh_tokens",
        type_="foreignkey",
    )

    op.drop_index(
        "ix_refresh_tokens_token_hash",
        table_name="refresh_tokens",
    )
    op.drop_index(
        "ix_refresh_tokens_family_id",
        table_name="refresh_tokens",
    )
    op.drop_index(
        "ix_refresh_tokens_revoked_at",
        table_name="refresh_tokens",
    )

    op.create_unique_constraint(
        "refresh_tokens_token_key",
        "refresh_tokens",
        ["token"],
    )

    op.drop_column("refresh_tokens", "replaced_by")
    op.drop_column("refresh_tokens", "revoked_at")
    op.drop_column("refresh_tokens", "created_at")
    op.drop_column("refresh_tokens", "family_id")
    op.drop_column("refresh_tokens", "token_hash")
