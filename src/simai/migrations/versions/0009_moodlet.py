"""moodlet + low_intimacy_streak

Revision ID: 0009
Revises: 0008
Create Date: 2026-10-20

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0009"
down_revision: str | None = "0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("characters") as batch:
        batch.add_column(
            sa.Column(
                "low_intimacy_streak",
                sa.Integer,
                nullable=False,
                server_default="0",
            )
        )
    op.create_table(
        "moodlets",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "character_id",
            sa.Integer,
            sa.ForeignKey("characters.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("kind", sa.String(16), nullable=False),
        sa.Column("started_at_tick", sa.Integer, nullable=False),
        sa.Column("expires_at_tick", sa.Integer, nullable=False),
    )
    op.create_index(
        "ix_moodlets_character",
        "moodlets",
        ["character_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_moodlets_character", table_name="moodlets")
    op.drop_table("moodlets")
    with op.batch_alter_table("characters") as batch:
        batch.drop_column("low_intimacy_streak")
