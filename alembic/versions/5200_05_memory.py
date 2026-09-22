"""memory table

Revision ID: 5200_05
Revises: 5200_04
Create Date: 2026-09-20

"""
from typing import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "5200_05"
down_revision: str | None = "5200_04"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "memory",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "owner_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=False,
        ),
        sa.Column("kind", sa.String(length=16), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("tick_total_seconds", sa.BigInteger(), nullable=False),
        sa.Column("saliency", sa.Float(), nullable=False, server_default="0.5"),
        sa.Column("valence", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("participants_json", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("tags_json", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("metadata_json", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["character.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_memory_owner_id", "memory", ["owner_id"])
    op.create_index("ix_memory_kind", "memory", ["kind"])
    op.create_index("ix_memory_tick_total_seconds", "memory", ["tick_total_seconds"])


def downgrade() -> None:
    op.drop_index("ix_memory_tick_total_seconds", table_name="memory")
    op.drop_index("ix_memory_kind", table_name="memory")
    op.drop_index("ix_memory_owner_id", table_name="memory")
    op.drop_table("memory")