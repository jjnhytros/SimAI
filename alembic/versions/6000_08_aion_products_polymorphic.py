"""aion products polymorphic: listing.lot_id, listing.vehicle_id

Revision ID: 6000_08
Revises: 6000_07
Create Date: 2026-09-22

Chunk 5.4d — FASE 5 Economy: prodotti polimorfici su AION.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "6000_08"
down_revision = "6000_07"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("aion_listing", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "lot_id",
                sa.BigInteger().with_variant(sa.Integer, "sqlite"),
                nullable=True,
            )
        )
        batch_op.add_column(
            sa.Column(
                "vehicle_id",
                sa.BigInteger().with_variant(sa.Integer, "sqlite"),
                nullable=True,
            )
        )
        batch_op.create_foreign_key(
            "fk_aion_listing_lot",
            "lot",
            ["lot_id"],
            ["id"],
            ondelete="SET NULL",
        )
        batch_op.create_foreign_key(
            "fk_aion_listing_vehicle",
            "vehicle",
            ["vehicle_id"],
            ["id"],
            ondelete="SET NULL",
        )
        batch_op.create_index("ix_aion_listing_lot", ["lot_id"])
        batch_op.create_index("ix_aion_listing_vehicle", ["vehicle_id"])


def downgrade() -> None:
    with op.batch_alter_table("aion_listing", schema=None) as batch_op:
        batch_op.drop_index("ix_aion_listing_vehicle")
        batch_op.drop_index("ix_aion_listing_lot")
        batch_op.drop_constraint("fk_aion_listing_vehicle", type_="foreignkey")
        batch_op.drop_constraint("fk_aion_listing_lot", type_="foreignkey")
        batch_op.drop_column("vehicle_id")
        batch_op.drop_column("lot_id")