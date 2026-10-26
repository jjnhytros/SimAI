"""shop_item

Revision ID: 0013
Revises: 0012
Create Date: 2026-10-26

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0013"
down_revision: str | None = "0012"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "shop_items",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("location_key", sa.String(32), nullable=False),
        sa.Column("action_kind", sa.String(16), nullable=False),
        sa.Column("price", sa.Float, nullable=False),
        sa.Column(
            "stock",
            sa.Integer,
            nullable=False,
            server_default="-1",
        ),
        sa.UniqueConstraint(
            "location_key",
            "action_kind",
            name="uq_shop_items_location_action",
        ),
    )


def downgrade() -> None:
    op.drop_table("shop_items")
