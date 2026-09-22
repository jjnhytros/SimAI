"""city: public services, budget, tax payments

Revision ID: 5300_08
Revises: 5300_07
Create Date: 2026-09-22

"""
from typing import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "5300_08"
down_revision: str | None = "5300_07"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "public_service",
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
        sa.Column("type", sa.String(length=16), nullable=False),
        sa.Column(
            "location_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=True,
        ),
        sa.Column(
            "quality", sa.Float(), nullable=False, server_default="0.6"
        ),
        sa.Column(
            "daily_cost", sa.Integer(), nullable=False, server_default="10"
        ),
        sa.Column(
            "coverage_radius",
            sa.Integer(),
            nullable=False,
            server_default="40",
        ),
        sa.Column(
            "staff_count", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        sa.Column("metadata_json", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column(
            "created_at", sa.DateTime(),
            server_default=sa.func.now(), nullable=False,
        ),
        sa.Column(
            "updated_at", sa.DateTime(),
            server_default=sa.func.now(), nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["district_id"], ["district.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["location_id"], ["location.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "district_id", "type", name="uq_public_service_district_type"
        ),
    )
    op.create_index("ix_public_service_district_id", "public_service", ["district_id"])
    op.create_index("ix_public_service_type", "public_service", ["type"])
    op.create_index("ix_public_service_is_active", "public_service", ["is_active"])
    op.create_index("ix_public_service_location_id", "public_service", ["location_id"])

    op.create_table(
        "city_budget",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column("balance", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "total_revenue", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "total_expenses", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "last_revenue_at_total_seconds",
            sa.BigInteger(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "last_expense_at_total_seconds",
            sa.BigInteger(),
            nullable=False,
            server_default="0",
        ),
        sa.Column("metadata_json", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column(
            "created_at", sa.DateTime(),
            server_default=sa.func.now(), nullable=False,
        ),
        sa.Column(
            "updated_at", sa.DateTime(),
            server_default=sa.func.now(), nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "tax_payment",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "character_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=False,
        ),
        sa.Column("kind", sa.String(length=16), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("at_total_seconds", sa.BigInteger(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column(
            "created_at", sa.DateTime(),
            server_default=sa.func.now(), nullable=False,
        ),
        sa.Column(
            "updated_at", sa.DateTime(),
            server_default=sa.func.now(), nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["character_id"], ["character.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_tax_payment_character_id", "tax_payment", ["character_id"])
    op.create_index("ix_tax_payment_kind", "tax_payment", ["kind"])
    op.create_index(
        "ix_tax_payment_at_total_seconds", "tax_payment", ["at_total_seconds"]
    )


def downgrade() -> None:
    op.drop_index("ix_tax_payment_at_total_seconds", table_name="tax_payment")
    op.drop_index("ix_tax_payment_kind", table_name="tax_payment")
    op.drop_index("ix_tax_payment_character_id", table_name="tax_payment")
    op.drop_table("tax_payment")
    op.drop_table("city_budget")
    op.drop_index("ix_public_service_location_id", table_name="public_service")
    op.drop_index("ix_public_service_is_active", table_name="public_service")
    op.drop_index("ix_public_service_type", table_name="public_service")
    op.drop_index("ix_public_service_district_id", table_name="public_service")
    op.drop_table("public_service")