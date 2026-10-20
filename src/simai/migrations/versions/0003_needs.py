"""needs

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-20

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "needs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "character_id",
            sa.Integer,
            sa.ForeignKey("characters.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("kind", sa.String(16), nullable=False),
        sa.Column(
            "value",
            sa.Float,
            nullable=False,
            server_default="100.0",
        ),
        sa.UniqueConstraint("character_id", "kind", name="uq_needs_character_kind"),
    )


def downgrade() -> None:
    op.drop_table("needs")
