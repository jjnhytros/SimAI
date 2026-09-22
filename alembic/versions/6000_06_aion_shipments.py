"""aion shipments: aion_shipment, aion_inventory_item

Revision ID: 6000_06
Revises: 6000_05
Create Date: 2026-09-22

Chunk 5.4b — FASE 5 Economy: spedizioni e magazzino AION.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "6000_06"
down_revision = "6000_05"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- aion_shipment ---
    op.create_table(
        "aion_shipment",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column(
            "order_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=False,
        ),
        sa.Column("mode", sa.String(length=16), nullable=False, server_default="SELLER_DIRECT"),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="PENDING"),
        sa.Column(
            "origin_character_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=True,
        ),
        sa.Column(
            "origin_location_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=True,
        ),
        sa.Column(
            "origin_warehouse_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=True,
        ),
        sa.Column(
            "destination_character_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=True,
        ),
        sa.Column(
            "destination_location_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=True,
        ),
        sa.Column("distance_cells", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("duration_ticks", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("shipping_cost", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("started_at_total_seconds", sa.BigInteger(), nullable=False),
        sa.Column("arrives_at_total_seconds", sa.BigInteger(), nullable=False),
        sa.Column("delivered_at_total_seconds", sa.BigInteger(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("order_id", name="uq_aion_shipment_order"),
        sa.ForeignKeyConstraint(
            ["order_id"],
            ["aion_order.id"],
            name="fk_aion_shipment_order",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["origin_character_id"],
            ["character.id"],
            name="fk_aion_shipment_origin_char",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["origin_location_id"],
            ["location.id"],
            name="fk_aion_shipment_origin_loc",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["origin_warehouse_id"],
            ["aion_warehouse.id"],
            name="fk_aion_shipment_origin_wh",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["destination_character_id"],
            ["character.id"],
            name="fk_aion_shipment_dest_char",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["destination_location_id"],
            ["location.id"],
            name="fk_aion_shipment_dest_loc",
            ondelete="SET NULL",
        ),
    )
    op.create_index("ix_aion_shipment_order", "aion_shipment", ["order_id"], unique=True)
    op.create_index("ix_aion_shipment_mode", "aion_shipment", ["mode"])
    op.create_index("ix_aion_shipment_status", "aion_shipment", ["status"])
    op.create_index("ix_aion_shipment_origin_char", "aion_shipment", ["origin_character_id"])
    op.create_index("ix_aion_shipment_origin_loc", "aion_shipment", ["origin_location_id"])
    op.create_index("ix_aion_shipment_origin_wh", "aion_shipment", ["origin_warehouse_id"])
    op.create_index("ix_aion_shipment_dest_char", "aion_shipment", ["destination_character_id"])
    op.create_index("ix_aion_shipment_dest_loc", "aion_shipment", ["destination_location_id"])
    op.create_index("ix_aion_shipment_arrives", "aion_shipment", ["arrives_at_total_seconds"])

    # --- aion_inventory_item ---
    op.create_table(
        "aion_inventory_item",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column(
            "warehouse_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=False,
        ),
        sa.Column(
            "listing_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=True,
        ),
        sa.Column(
            "object_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=True,
        ),
        sa.Column("item_type", sa.String(length=64), nullable=False),
        sa.Column("item_name", sa.String(length=128), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("condition", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("quality_label", sa.String(length=32), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="STORED"),
        sa.Column(
            "reserved_for_order_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=True,
        ),
        sa.Column("stored_at_total_seconds", sa.BigInteger(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["warehouse_id"],
            ["aion_warehouse.id"],
            name="fk_aion_inventory_warehouse",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["listing_id"],
            ["aion_listing.id"],
            name="fk_aion_inventory_listing",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["object_id"],
            ["game_object.id"],
            name="fk_aion_inventory_object",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["reserved_for_order_id"],
            ["aion_order.id"],
            name="fk_aion_inventory_order",
            ondelete="SET NULL",
        ),
    )
    op.create_index("ix_aion_inventory_warehouse", "aion_inventory_item", ["warehouse_id"])
    op.create_index("ix_aion_inventory_listing", "aion_inventory_item", ["listing_id"])
    op.create_index("ix_aion_inventory_object", "aion_inventory_item", ["object_id"])
    op.create_index("ix_aion_inventory_item_type", "aion_inventory_item", ["item_type"])
    op.create_index("ix_aion_inventory_status", "aion_inventory_item", ["status"])
    op.create_index("ix_aion_inventory_order", "aion_inventory_item", ["reserved_for_order_id"])


def downgrade() -> None:
    op.drop_index("ix_aion_inventory_order", table_name="aion_inventory_item")
    op.drop_index("ix_aion_inventory_status", table_name="aion_inventory_item")
    op.drop_index("ix_aion_inventory_item_type", table_name="aion_inventory_item")
    op.drop_index("ix_aion_inventory_object", table_name="aion_inventory_item")
    op.drop_index("ix_aion_inventory_listing", table_name="aion_inventory_item")
    op.drop_index("ix_aion_inventory_warehouse", table_name="aion_inventory_item")
    op.drop_table("aion_inventory_item")

    op.drop_index("ix_aion_shipment_arrives", table_name="aion_shipment")
    op.drop_index("ix_aion_shipment_dest_loc", table_name="aion_shipment")
    op.drop_index("ix_aion_shipment_dest_char", table_name="aion_shipment")
    op.drop_index("ix_aion_shipment_origin_wh", table_name="aion_shipment")
    op.drop_index("ix_aion_shipment_origin_loc", table_name="aion_shipment")
    op.drop_index("ix_aion_shipment_origin_char", table_name="aion_shipment")
    op.drop_index("ix_aion_shipment_status", table_name="aion_shipment")
    op.drop_index("ix_aion_shipment_mode", table_name="aion_shipment")
    op.drop_index("ix_aion_shipment_order", table_name="aion_shipment")
    op.drop_table("aion_shipment")