"""addiction table

Revision ID: 5200_09
Revises: 5400_02
Create Date: 2026-09-21

"""
from typing import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "5200_09"
down_revision: str | None = "5400_02"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "addiction",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "character_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=False,
        ),
        sa.Column("kind", sa.String(length=32), nullable=False),
        sa.Column(
            "dependence_level", sa.Float(), nullable=False, server_default="0.0"
        ),
        sa.Column("tolerance", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("last_use_total_seconds", sa.BigInteger(), nullable=False),
        sa.Column("started_at_total_seconds", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["character_id"], ["character.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("character_id", "kind", name="uq_addiction_pair"),
    )
    op.create_index("ix_addiction_character_id", "addiction", ["character_id"])
    op.create_index("ix_addiction_kind", "addiction", ["kind"])
    op.create_index(
        "ix_addiction_last_use_total_seconds",
        "addiction",
        ["last_use_total_seconds"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_addiction_last_use_total_seconds", table_name="addiction"
    )
    op.drop_index("ix_addiction_kind", table_name="addiction")
    op.drop_index("ix_addiction_character_id", table_name="addiction")
    op.drop_table("addiction")