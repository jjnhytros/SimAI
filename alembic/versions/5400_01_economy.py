"""economy: jobs, shop items, transactions

Revision ID: 5400_01
Revises: 5200_06
Create Date: 2026-09-20

"""
from typing import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "5400_01"
down_revision: str | None = "5200_06"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. job
    op.create_table(
        "job",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column("character_id", sa.BigInteger().with_variant(sa.Integer, "sqlite"), nullable=False),
        sa.Column("workplace_id", sa.BigInteger().with_variant(sa.Integer, "sqlite"), nullable=True),
        sa.Column("job_type", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=64), nullable=False),
        sa.Column("daily_wage", sa.Integer(), nullable=False),
        sa.Column("since_total_seconds", sa.BigInteger(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("metadata_json", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["character_id"], ["character.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["workplace_id"], ["location.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("character_id", name="uq_job_character"),
    )
    op.create_index("ix_job_character_id", "job", ["character_id"])
    op.create_index("ix_job_workplace_id", "job", ["workplace_id"])
    op.create_index("ix_job_job_type", "job", ["job_type"])
    op.create_index("ix_job_is_active", "job", ["is_active"])
    op.create_index("ix_job_since_total_seconds", "job", ["since_total_seconds"])

    # 2. shop_item
    op.create_table(
        "shop_item",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column("location_id", sa.BigInteger().with_variant(sa.Integer, "sqlite"), nullable=False),
        sa.Column("item_type", sa.String(length=64), nullable=False),
        sa.Column("item_name", sa.String(length=128), nullable=False),
        sa.Column("base_price", sa.Integer(), nullable=False),
        sa.Column("current_price", sa.Integer(), nullable=False),
        sa.Column("stock", sa.Integer(), nullable=False, server_default="-1"),
        sa.Column("metadata_json", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["location_id"], ["location.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("location_id", "item_type", name="uq_shop_item_pair"),
    )
    op.create_index("ix_shop_item_location_id", "shop_item", ["location_id"])
    op.create_index("ix_shop_item_item_type", "shop_item", ["item_type"])

    # 3. transaction
    op.create_table(
        "transaction",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column("character_id", sa.BigInteger().with_variant(sa.Integer, "sqlite"), nullable=False),
        sa.Column("kind", sa.String(length=16), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("counterparty_id", sa.BigInteger().with_variant(sa.Integer, "sqlite"), nullable=True),
        sa.Column("location_id", sa.BigInteger().with_variant(sa.Integer, "sqlite"), nullable=True),
        sa.Column("item_type", sa.String(length=64), nullable=True),
        sa.Column("at_total_seconds", sa.BigInteger(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["character_id"], ["character.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["counterparty_id"], ["character.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["location_id"], ["location.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_transaction_character_id", "transaction", ["character_id"])
    op.create_index("ix_transaction_kind", "transaction", ["kind"])
    op.create_index("ix_transaction_counterparty_id", "transaction", ["counterparty_id"])
    op.create_index("ix_transaction_at_total_seconds", "transaction", ["at_total_seconds"])


def downgrade() -> None:
    op.drop_index("ix_transaction_at_total_seconds", table_name="transaction")
    op.drop_index("ix_transaction_counterparty_id", table_name="transaction")
    op.drop_index("ix_transaction_kind", table_name="transaction")
    op.drop_index("ix_transaction_character_id", table_name="transaction")
    op.drop_table("transaction")

    op.drop_index("ix_shop_item_item_type", table_name="shop_item")
    op.drop_index("ix_shop_item_location_id", table_name="shop_item")
    op.drop_table("shop_item")

    op.drop_index("ix_job_since_total_seconds", table_name="job")
    op.drop_index("ix_job_is_active", table_name="job")
    op.drop_index("ix_job_job_type", table_name="job")
    op.drop_index("ix_job_workplace_id", table_name="job")
    op.drop_index("ix_job_character_id", table_name="job")
    op.drop_table("job")