"""lifecycle: age_days, death_cause, pregnancy

Revision ID: 5200_04
Revises: 0014
Create Date: 2026-10-27

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "5200_04"
down_revision: str | None = "0014"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "characters",
        sa.Column("age_days", sa.Integer, nullable=False, server_default="0"),
    )
    op.add_column(
        "characters",
        sa.Column("death_cause", sa.String(16), nullable=True),
    )
    op.create_table(
        "pregnancy",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "character_id",
            sa.Integer,
            sa.ForeignKey("characters.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "partner_id",
            sa.Integer,
            sa.ForeignKey("characters.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("conceived_at_tick", sa.Integer, nullable=False),
        sa.Column("due_at_tick", sa.Integer, nullable=False),
    )
    op.create_index("ix_pregnancy_character", "pregnancy", ["character_id"])


def downgrade() -> None:
    op.drop_index("ix_pregnancy_character", table_name="pregnancy")
    op.drop_table("pregnancy")
    op.drop_column("characters", "death_cause")
    op.drop_column("characters", "age_days")
