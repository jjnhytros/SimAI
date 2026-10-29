"""skills

Revision ID: 5200_08
Revises: 0015
Create Date: 2026-10-29

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "5200_08"
down_revision: str | None = "0015"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "skills",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "character_id",
            sa.Integer,
            sa.ForeignKey("characters.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("kind", sa.String(16), nullable=False),
        sa.Column(
            "level",
            sa.Float,
            nullable=False,
            server_default="0.0",
        ),
        sa.UniqueConstraint(
            "character_id",
            "kind",
            name="uq_skills_character_kind",
        ),
        sa.CheckConstraint(
            "level >= 0.0 AND level <= 100.0",
            name="ck_skills_level",
        ),
    )
    op.create_index("ix_skills_character", "skills", ["character_id"])


def downgrade() -> None:
    op.drop_index("ix_skills_character", table_name="skills")
    op.drop_table("skills")
