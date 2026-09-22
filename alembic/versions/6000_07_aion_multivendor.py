"""aion multivendor: seller_company_id, buyer_company_id

Revision ID: 6000_07
Revises: 6000_06
Create Date: 2026-09-22

Chunk 5.4c — FASE 5 Economy: multivendor (Company come seller/buyer).
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "6000_07"
down_revision = "6000_06"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- aion_listing.seller_company_id ---
    with op.batch_alter_table("aion_listing", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "seller_company_id",
                sa.BigInteger().with_variant(sa.Integer, "sqlite"),
                nullable=True,
            )
        )
        batch_op.create_foreign_key(
            "fk_aion_listing_seller_company",
            "company",
            ["seller_company_id"],
            ["id"],
            ondelete="SET NULL",
        )
        batch_op.create_index(
            "ix_aion_listing_seller_company", ["seller_company_id"]
        )

    # --- aion_order.buyer_company_id ---
    with op.batch_alter_table("aion_order", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "buyer_company_id",
                sa.BigInteger().with_variant(sa.Integer, "sqlite"),
                nullable=True,
            )
        )
        batch_op.create_foreign_key(
            "fk_aion_order_buyer_company",
            "company",
            ["buyer_company_id"],
            ["id"],
            ondelete="SET NULL",
        )
        batch_op.create_index(
            "ix_aion_order_buyer_company", ["buyer_company_id"]
        )


def downgrade() -> None:
    with op.batch_alter_table("aion_order", schema=None) as batch_op:
        batch_op.drop_index("ix_aion_order_buyer_company")
        batch_op.drop_constraint("fk_aion_order_buyer_company", type_="foreignkey")
        batch_op.drop_column("buyer_company_id")

    with op.batch_alter_table("aion_listing", schema=None) as batch_op:
        batch_op.drop_index("ix_aion_listing_seller_company")
        batch_op.drop_constraint("fk_aion_listing_seller_company", type_="foreignkey")
        batch_op.drop_column("seller_company_id")