"""relationships

Revision ID: 0005
Revises: 0004
Create Date: 2026-10-20

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "relationships",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "from_character_id",
            sa.Integer,
            sa.ForeignKey("characters.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "to_character_id",
            sa.Integer,
            sa.ForeignKey("characters.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("kind", sa.String(16), nullable=False),
        sa.Column(
            "strength",
            sa.Float,
            nullable=False,
            server_default="50.0",
        ),
        sa.UniqueConstraint(
            "from_character_id",
            "to_character_id",
            "kind",
            name="uq_relationships_from_to_kind",
        ),
        sa.CheckConstraint(
            "from_character_id != to_character_id",
            name="ck_relationships_distinct",
        ),
    )
    op.create_index(
        "ix_relationships_from",
        "relationships",
        ["from_character_id"],
    )
    op.create_index(
        "ix_relationships_to",
        "relationships",
        ["to_character_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_relationships_to", table_name="relationships")
    op.drop_index("ix_relationships_from", table_name="relationships")
    op.drop_table("relationships")
