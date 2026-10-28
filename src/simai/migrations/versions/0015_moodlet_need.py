"""moodlet.need (need-based moodlets)

Revision ID: 0015
Revises: 5200_04
Create Date: 2026-10-28

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0015"
down_revision: str | None = "5200_04"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Niente batch: SQLite supporta ADD COLUMN nativamente.
    # Nullable: i moodlet non-need (ATE_WELL, SOCIALIZED, LONELY,
    # BECAME_*) hanno need=NULL.
    op.add_column(
        "moodlets",
        sa.Column("need", sa.String(16), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("moodlets", "need")
