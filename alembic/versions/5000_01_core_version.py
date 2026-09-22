"""core version table

Revision ID: 5000_01
Revises:
Create Date: 2026-09-20

"""
from typing import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5000_01"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "core_version",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column("version", sa.String(length=32), nullable=False),
        sa.Column("git_sha", sa.String(length=40), nullable=True),
        sa.Column(
            "applied_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_core_version_version",
        "core_version",
        ["version"],
        unique=False,
    )

    op.execute(
        sa.text("INSERT INTO core_version (version, git_sha) VALUES (:v, NULL)").bindparams(
            v="0.1.0.dev0"
        )
    )


def downgrade() -> None:
    op.drop_index("ix_core_version_version", table_name="core_version")
    op.drop_table("core_version")