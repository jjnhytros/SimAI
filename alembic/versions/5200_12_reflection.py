"""reflection_entry table

Revision ID: 5200_12
Revises: 5200_11
Create Date: 2026-09-21

"""
from typing import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "5200_12"
down_revision: str | None = "5200_11"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "reflection_entry",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer, "sqlite"), autoincrement=True, nullable=False),
        sa.Column("character_id", sa.BigInteger().with_variant(sa.Integer, "sqlite"), nullable=False),
        sa.Column("kind", sa.String(length=16), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("at_total_seconds", sa.BigInteger(), nullable=False),
        sa.Column("sentiment", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("metadata_json", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["character_id"], ["character.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_reflection_entry_character_id", "reflection_entry", ["character_id"])
    op.create_index("ix_reflection_entry_kind", "reflection_entry", ["kind"])
    op.create_index("ix_reflection_entry_at_total_seconds", "reflection_entry", ["at_total_seconds"])


def downgrade() -> None:
    op.drop_index("ix_reflection_entry_at_total_seconds", table_name="reflection_entry")
    op.drop_index("ix_reflection_entry_kind", table_name="reflection_entry")
    op.drop_index("ix_reflection_entry_character_id", table_name="reflection_entry")
    op.drop_table("reflection_entry")