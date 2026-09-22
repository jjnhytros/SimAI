"""companies core: company, company_employee, company_transaction

Revision ID: 6000_04
Revises: 6000_03
Create Date: 2026-09-22

Chunk 5.3a — FASE 5 Economy: aziende NPC.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "6000_04"
down_revision = "6000_03"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- company ---
    op.create_table(
        "company",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("kind", sa.String(length=24), nullable=False, server_default="SHOP"),
        sa.Column(
            "owner_character_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=False,
        ),
        sa.Column(
            "location_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=True,
        ),
        sa.Column("athel_balance", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("base_daily_revenue", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("base_daily_cost", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="ACTIVE"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("founded_at_total_seconds", sa.BigInteger(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["owner_character_id"],
            ["character.id"],
            name="fk_company_owner",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["location_id"],
            ["location.id"],
            name="fk_company_location",
            ondelete="SET NULL",
        ),
    )
    op.create_index("ix_company_name", "company", ["name"])
    op.create_index("ix_company_kind", "company", ["kind"])
    op.create_index("ix_company_owner", "company", ["owner_character_id"])
    op.create_index("ix_company_location", "company", ["location_id"])
    op.create_index("ix_company_status", "company", ["status"])
    op.create_index("ix_company_is_active", "company", ["is_active"])

    # --- company_employee ---
    op.create_table(
        "company_employee",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column(
            "company_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=False,
        ),
        sa.Column(
            "character_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=False,
        ),
        sa.Column("role", sa.String(length=16), nullable=False, server_default="WORKER"),
        sa.Column("daily_wage", sa.Integer(), nullable=False, server_default="12"),
        sa.Column("hired_at_total_seconds", sa.BigInteger(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["company.id"],
            name="fk_company_employee_company",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["character_id"],
            ["character.id"],
            name="fk_company_employee_character",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "company_id", "character_id", name="uq_company_employee_pair"
        ),
    )
    op.create_index("ix_company_employee_company", "company_employee", ["company_id"])
    op.create_index("ix_company_employee_character", "company_employee", ["character_id"])
    op.create_index("ix_company_employee_role", "company_employee", ["role"])
    op.create_index("ix_company_employee_is_active", "company_employee", ["is_active"])

    # --- company_transaction ---
    op.create_table(
        "company_transaction",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column(
            "company_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=False,
        ),
        sa.Column("kind", sa.String(length=16), nullable=False, server_default="REVENUE"),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column(
            "character_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=True,
        ),
        sa.Column("at_total_seconds", sa.BigInteger(), nullable=False),
        sa.Column("description", sa.String(length=256), nullable=False, server_default=""),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["company.id"],
            name="fk_company_transaction_company",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["character_id"],
            ["character.id"],
            name="fk_company_transaction_character",
            ondelete="SET NULL",
        ),
    )
    op.create_index(
        "ix_company_transaction_company", "company_transaction", ["company_id"]
    )
    op.create_index("ix_company_transaction_kind", "company_transaction", ["kind"])
    op.create_index(
        "ix_company_transaction_character", "company_transaction", ["character_id"]
    )
    op.create_index(
        "ix_company_transaction_at", "company_transaction", ["at_total_seconds"]
    )


def downgrade() -> None:
    op.drop_index("ix_company_transaction_at", table_name="company_transaction")
    op.drop_index("ix_company_transaction_character", table_name="company_transaction")
    op.drop_index("ix_company_transaction_kind", table_name="company_transaction")
    op.drop_index("ix_company_transaction_company", table_name="company_transaction")
    op.drop_table("company_transaction")

    op.drop_index("ix_company_employee_is_active", table_name="company_employee")
    op.drop_index("ix_company_employee_role", table_name="company_employee")
    op.drop_index("ix_company_employee_character", table_name="company_employee")
    op.drop_index("ix_company_employee_company", table_name="company_employee")
    op.drop_table("company_employee")

    op.drop_index("ix_company_is_active", table_name="company")
    op.drop_index("ix_company_status", table_name="company")
    op.drop_index("ix_company_location", table_name="company")
    op.drop_index("ix_company_owner", table_name="company")
    op.drop_index("ix_company_kind", table_name="company")
    op.drop_index("ix_company_name", table_name="company")
    op.drop_table("company")