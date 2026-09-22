"""formative event table

Revision ID: 5200_10
Revises: 5200_09
Create Date: 2026-09-21

"""
from typing import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "5200_10"
down_revision: str | None = "5200_09"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "formative_event",
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
        sa.Column("occurred_at_age", sa.Integer(), nullable=False),
        sa.Column("occurred_at_total_seconds", sa.BigInteger(), nullable=False),
        sa.Column("severity", sa.Float(), nullable=False, server_default="0.5"),
        sa.Column("text", sa.String(length=256), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["character_id"], ["character.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "character_id", "kind", "occurred_at_age", name="uq_formative_event"
        ),
    )
    op.create_index("ix_formative_event_character_id", "formative_event", ["character_id"])
    op.create_index("ix_formative_event_kind", "formative_event", ["kind"])
    op.create_index(
        "ix_formative_event_occurred_at_total_seconds",
        "formative_event",
        ["occurred_at_total_seconds"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_formative_event_occurred_at_total_seconds",
        table_name="formative_event",
    )
    op.drop_index("ix_formative_event_kind", table_name="formative_event")
    op.drop_index("ix_formative_event_character_id", table_name="formative_event")
    op.drop_table("formative_event")