"""initial core_version table

Revision ID: 0001
Revises:
Create Date: 2026-10-20

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "core_version",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("schema_version", sa.String(32), nullable=False),
        sa.Column("rules_version", sa.String(32), nullable=False),
        sa.Column(
            "applied_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.execute(
        "INSERT INTO core_version (id, schema_version, rules_version) VALUES (1, '0.1.0', '0.1.0')"
    )


def downgrade() -> None:
    op.drop_table("core_version")
