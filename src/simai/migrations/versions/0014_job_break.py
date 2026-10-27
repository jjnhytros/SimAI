"""job break_start_tick / break_end_tick

Revision ID: 0014
Revises: 0013
Create Date: 2026-10-27

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0014"
down_revision: str | None = "0013"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("jobs", sa.Column("break_start_tick", sa.Integer, nullable=True))
    op.add_column("jobs", sa.Column("break_end_tick", sa.Integer, nullable=True))


def downgrade() -> None:
    op.drop_column("jobs", "break_end_tick")
    op.drop_column("jobs", "break_start_tick")
