"""districts and lots

Revision ID: 5300_02
Revises: 5200_12
Create Date: 2026-09-21

"""
from typing import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "5300_02"
down_revision: str | None = "5200_12"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "district",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column(
            "type",
            sa.String(length=16),
            nullable=False,
            server_default="MIXED",
        ),
        sa.Column("bounds_x", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("bounds_y", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("bounds_w", sa.Integer(), nullable=False, server_default="50"),
        sa.Column("bounds_h", sa.Integer(), nullable=False, server_default="50"),
        sa.Column("tax_rate", sa.Float(), nullable=False, server_default="0.05"),
        sa.Column(
            "safety_rating", sa.Float(), nullable=False, server_default="0.5"
        ),
        sa.Column(
            "aesthetic_score", sa.Float(), nullable=False, server_default="0.5"
        ),
        sa.Column("metadata_json", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_district_name", "district", ["name"])
    op.create_index("ix_district_type", "district", ["type"])

    op.create_table(
        "lot",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "district_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column(
            "usage",
            sa.String(length=16),
            nullable=False,
            server_default="VACANT",
        ),
        sa.Column("bounds_x", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("bounds_y", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("bounds_w", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("bounds_h", sa.Integer(), nullable=False, server_default="10"),
        sa.Column(
            "base_price", sa.Integer(), nullable=False, server_default="1000"
        ),
        sa.Column(
            "is_developed",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column(
            "location_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=True,
        ),
        sa.Column("metadata_json", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column(
            "current_value", sa.Float(), nullable=False, server_default="0.0"
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["district_id"], ["district.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["location_id"], ["location.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_lot_district_id", "lot", ["district_id"])
    op.create_index("ix_lot_usage", "lot", ["usage"])
    op.create_index("ix_lot_location_id", "lot", ["location_id"])


def downgrade() -> None:
    op.drop_index("ix_lot_location_id", table_name="lot")
    op.drop_index("ix_lot_usage", table_name="lot")
    op.drop_index("ix_lot_district_id", table_name="lot")
    op.drop_table("lot")
    op.drop_index("ix_district_type", table_name="district")
    op.drop_index("ix_district_name", table_name="district")
    op.drop_table("district")