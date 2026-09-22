"""aion core: aion_platform, aion_warehouse, aion_listing, aion_order

Revision ID: 6000_05
Revises: 6000_04
Create Date: 2026-09-22

Chunk 5.4a — FASE 5 Economy: fondamenta della piattaforma AION.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "6000_05"
down_revision = "6000_04"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- aion_platform ---
    op.create_table(
        "aion_platform",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column(
            "default_commission_rate",
            sa.Float(),
            nullable=False,
            server_default="0.05",
        ),
        sa.Column(
            "default_fulfillment_mode",
            sa.String(length=16),
            nullable=False,
            server_default="SELLER_DIRECT",
        ),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("code", name="uq_aion_platform_code"),
    )
    op.create_index("ix_aion_platform_code", "aion_platform", ["code"], unique=True)
    op.create_index("ix_aion_platform_is_active", "aion_platform", ["is_active"])

    # --- aion_warehouse ---
    op.create_table(
        "aion_warehouse",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("warehouse_kind", sa.String(length=16), nullable=False, server_default="GLOBAL"),
        sa.Column("depth_meters", sa.Integer(), nullable=False, server_default="-200"),
        sa.Column("underground_x", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("underground_y", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "access_location_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=True,
        ),
        sa.Column("capacity", sa.Integer(), nullable=False, server_default="100000"),
        sa.Column("used_capacity", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("code", name="uq_aion_warehouse_code"),
        sa.ForeignKeyConstraint(
            ["access_location_id"],
            ["location.id"],
            name="fk_aion_warehouse_access",
            ondelete="SET NULL",
        ),
    )
    op.create_index("ix_aion_warehouse_code", "aion_warehouse", ["code"], unique=True)
    op.create_index("ix_aion_warehouse_kind", "aion_warehouse", ["warehouse_kind"])
    op.create_index("ix_aion_warehouse_access", "aion_warehouse", ["access_location_id"])
    op.create_index("ix_aion_warehouse_is_active", "aion_warehouse", ["is_active"])

    # --- aion_listing ---
    op.create_table(
        "aion_listing",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column("seller_type", sa.String(length=16), nullable=False),
        sa.Column("seller_id", sa.Integer(), nullable=False),
        sa.Column("product_type", sa.String(length=16), nullable=False, server_default="GOODS"),
        sa.Column("item_type", sa.String(length=64), nullable=False),
        sa.Column("item_name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.String(length=512), nullable=False, server_default=""),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("quantity_sold", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("unit_price", sa.Integer(), nullable=False),
        sa.Column("condition", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("quality_label", sa.String(length=32), nullable=True),
        sa.Column(
            "fulfillment_mode",
            sa.String(length=16),
            nullable=False,
            server_default="SELLER_DIRECT",
        ),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="ACTIVE"),
        sa.Column("created_at_total_seconds", sa.BigInteger(), nullable=False),
        sa.Column(
            "seller_character_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=True,
        ),
        sa.Column(
            "source_object_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=True,
        ),
        sa.Column(
            "warehouse_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=True,
        ),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["seller_character_id"],
            ["character.id"],
            name="fk_aion_listing_seller_char",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["source_object_id"],
            ["game_object.id"],
            name="fk_aion_listing_source_obj",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["warehouse_id"],
            ["aion_warehouse.id"],
            name="fk_aion_listing_warehouse",
            ondelete="SET NULL",
        ),
    )
    op.create_index("ix_aion_listing_seller_type", "aion_listing", ["seller_type"])
    op.create_index("ix_aion_listing_seller_id", "aion_listing", ["seller_id"])
    op.create_index("ix_aion_listing_product_type", "aion_listing", ["product_type"])
    op.create_index("ix_aion_listing_item_type", "aion_listing", ["item_type"])
    op.create_index("ix_aion_listing_fulfillment", "aion_listing", ["fulfillment_mode"])
    op.create_index("ix_aion_listing_status", "aion_listing", ["status"])
    op.create_index("ix_aion_listing_created_at", "aion_listing", ["created_at_total_seconds"])
    op.create_index("ix_aion_listing_seller_char", "aion_listing", ["seller_character_id"])
    op.create_index("ix_aion_listing_source_obj", "aion_listing", ["source_object_id"])
    op.create_index("ix_aion_listing_warehouse", "aion_listing", ["warehouse_id"])

    # --- aion_order ---
    op.create_table(
        "aion_order",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column(
            "listing_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=False,
        ),
        sa.Column("buyer_type", sa.String(length=16), nullable=False, server_default="CHARACTER"),
        sa.Column("buyer_id", sa.Integer(), nullable=False),
        sa.Column(
            "buyer_character_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=True,
        ),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("unit_price", sa.Integer(), nullable=False),
        sa.Column("total_price", sa.Integer(), nullable=False),
        sa.Column("commission", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("net_to_seller", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("escrowed_amount", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "escrow_entry_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=True,
        ),
        sa.Column(
            "settlement_entry_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=True,
        ),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="PENDING"),
        sa.Column("created_at_total_seconds", sa.BigInteger(), nullable=False),
        sa.Column("delivered_at_total_seconds", sa.BigInteger(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["listing_id"],
            ["aion_listing.id"],
            name="fk_aion_order_listing",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["buyer_character_id"],
            ["character.id"],
            name="fk_aion_order_buyer_char",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["escrow_entry_id"],
            ["journal_entry.id"],
            name="fk_aion_order_escrow_entry",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["settlement_entry_id"],
            ["journal_entry.id"],
            name="fk_aion_order_settlement_entry",
            ondelete="SET NULL",
        ),
    )
    op.create_index("ix_aion_order_listing", "aion_order", ["listing_id"])
    op.create_index("ix_aion_order_buyer_type", "aion_order", ["buyer_type"])
    op.create_index("ix_aion_order_buyer_id", "aion_order", ["buyer_id"])
    op.create_index("ix_aion_order_buyer_char", "aion_order", ["buyer_character_id"])
    op.create_index("ix_aion_order_escrow_entry", "aion_order", ["escrow_entry_id"])
    op.create_index("ix_aion_order_settlement_entry", "aion_order", ["settlement_entry_id"])
    op.create_index("ix_aion_order_status", "aion_order", ["status"])
    op.create_index("ix_aion_order_created_at", "aion_order", ["created_at_total_seconds"])


def downgrade() -> None:
    op.drop_index("ix_aion_order_created_at", table_name="aion_order")
    op.drop_index("ix_aion_order_status", table_name="aion_order")
    op.drop_index("ix_aion_order_settlement_entry", table_name="aion_order")
    op.drop_index("ix_aion_order_escrow_entry", table_name="aion_order")
    op.drop_index("ix_aion_order_buyer_char", table_name="aion_order")
    op.drop_index("ix_aion_order_buyer_id", table_name="aion_order")
    op.drop_index("ix_aion_order_buyer_type", table_name="aion_order")
    op.drop_index("ix_aion_order_listing", table_name="aion_order")
    op.drop_table("aion_order")

    op.drop_index("ix_aion_listing_warehouse", table_name="aion_listing")
    op.drop_index("ix_aion_listing_source_obj", table_name="aion_listing")
    op.drop_index("ix_aion_listing_seller_char", table_name="aion_listing")
    op.drop_index("ix_aion_listing_created_at", table_name="aion_listing")
    op.drop_index("ix_aion_listing_status", table_name="aion_listing")
    op.drop_index("ix_aion_listing_fulfillment", table_name="aion_listing")
    op.drop_index("ix_aion_listing_item_type", table_name="aion_listing")
    op.drop_index("ix_aion_listing_product_type", table_name="aion_listing")
    op.drop_index("ix_aion_listing_seller_id", table_name="aion_listing")
    op.drop_index("ix_aion_listing_seller_type", table_name="aion_listing")
    op.drop_table("aion_listing")

    op.drop_index("ix_aion_warehouse_is_active", table_name="aion_warehouse")
    op.drop_index("ix_aion_warehouse_access", table_name="aion_warehouse")
    op.drop_index("ix_aion_warehouse_kind", table_name="aion_warehouse")
    op.drop_index("ix_aion_warehouse_code", table_name="aion_warehouse")
    op.drop_table("aion_warehouse")

    op.drop_index("ix_aion_platform_is_active", table_name="aion_platform")
    op.drop_index("ix_aion_platform_code", table_name="aion_platform")
    op.drop_table("aion_platform")