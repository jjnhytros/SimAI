"""banking core: bank, bank_account, loan, loan_payment, interest_accrual

Revision ID: 6000_03
Revises: 6000_02
Create Date: 2026-09-22

Chunk 5.2a — FASE 5 Economy: banche commerciali, conti, prestiti.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "6000_03"
down_revision = "6000_02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- bank ---
    op.create_table(
        "bank",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("kind", sa.String(length=16), nullable=False, server_default="COMMERCIAL"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column(
            "owner_character_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=True,
        ),
        sa.Column("reserve_ratio", sa.Float(), nullable=False, server_default="0.10"),
        sa.Column("deposit_interest_rate", sa.Float(), nullable=False, server_default="0.02"),
        sa.Column("loan_interest_rate", sa.Float(), nullable=False, server_default="0.08"),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("code", name="uq_bank_code"),
        sa.ForeignKeyConstraint(
            ["owner_character_id"],
            ["character.id"],
            name="fk_bank_owner",
            ondelete="SET NULL",
        ),
    )
    op.create_index("ix_bank_code", "bank", ["code"], unique=True)
    op.create_index("ix_bank_kind", "bank", ["kind"])
    op.create_index("ix_bank_is_active", "bank", ["is_active"])
    op.create_index("ix_bank_owner", "bank", ["owner_character_id"])

    # --- bank_account ---
    op.create_table(
        "bank_account",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column(
            "bank_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=False,
        ),
        sa.Column(
            "character_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=False,
        ),
        sa.Column("kind", sa.String(length=16), nullable=False, server_default="CHECKING"),
        sa.Column("balance", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("interest_rate", sa.Float(), nullable=False, server_default="0.02"),
        sa.Column("opened_at_total_seconds", sa.BigInteger(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("is_frozen", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["bank_id"], ["bank.id"], name="fk_bank_account_bank", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["character_id"],
            ["character.id"],
            name="fk_bank_account_character",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "bank_id", "character_id", "kind", name="uq_bank_account_triple"
        ),
    )
    op.create_index("ix_bank_account_bank", "bank_account", ["bank_id"])
    op.create_index("ix_bank_account_character", "bank_account", ["character_id"])
    op.create_index("ix_bank_account_kind", "bank_account", ["kind"])
    op.create_index("ix_bank_account_is_active", "bank_account", ["is_active"])
    op.create_index("ix_bank_account_is_frozen", "bank_account", ["is_frozen"])

    # --- loan ---
    op.create_table(
        "loan",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column(
            "bank_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=False,
        ),
        sa.Column(
            "character_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=False,
        ),
        sa.Column("principal", sa.Integer(), nullable=False),
        sa.Column("remaining_principal", sa.Float(), nullable=False),
        sa.Column("annual_interest_rate", sa.Float(), nullable=False),
        sa.Column("term_months", sa.Integer(), nullable=False),
        sa.Column("monthly_payment", sa.Integer(), nullable=False),
        sa.Column("payments_made", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("payments_missed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("next_payment_at_total_seconds", sa.BigInteger(), nullable=False),
        sa.Column("started_at_total_seconds", sa.BigInteger(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="ACTIVE"),
        sa.Column(
            "collateral_lot_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=True,
        ),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["bank_id"], ["bank.id"], name="fk_loan_bank", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["character_id"], ["character.id"], name="fk_loan_character", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["collateral_lot_id"],
            ["lot.id"],
            name="fk_loan_collateral",
            ondelete="SET NULL",
        ),
    )
    op.create_index("ix_loan_bank", "loan", ["bank_id"])
    op.create_index("ix_loan_character", "loan", ["character_id"])
    op.create_index("ix_loan_status", "loan", ["status"])
    op.create_index("ix_loan_next_payment", "loan", ["next_payment_at_total_seconds"])
    op.create_index("ix_loan_collateral", "loan", ["collateral_lot_id"])

    # --- loan_payment ---
    op.create_table(
        "loan_payment",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column(
            "loan_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=False,
        ),
        sa.Column("amount", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("interest_part", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("principal_part", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("remaining_after", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("paid_at_total_seconds", sa.BigInteger(), nullable=False),
        sa.Column("success", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("reason", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["loan_id"], ["loan.id"], name="fk_loan_payment_loan", ondelete="CASCADE"
        ),
    )
    op.create_index("ix_loan_payment_loan", "loan_payment", ["loan_id"])
    op.create_index("ix_loan_payment_paid_at", "loan_payment", ["paid_at_total_seconds"])

    # --- interest_accrual ---
    op.create_table(
        "interest_accrual",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column(
            "loan_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=False,
        ),
        sa.Column("accrued_amount", sa.Float(), nullable=False),
        sa.Column("at_total_seconds", sa.BigInteger(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["loan_id"],
            ["loan.id"],
            name="fk_interest_accrual_loan",
            ondelete="CASCADE",
        ),
    )
    op.create_index("ix_interest_accrual_loan", "interest_accrual", ["loan_id"])
    op.create_index("ix_interest_accrual_at", "interest_accrual", ["at_total_seconds"])


def downgrade() -> None:
    op.drop_index("ix_interest_accrual_at", table_name="interest_accrual")
    op.drop_index("ix_interest_accrual_loan", table_name="interest_accrual")
    op.drop_table("interest_accrual")

    op.drop_index("ix_loan_payment_paid_at", table_name="loan_payment")
    op.drop_index("ix_loan_payment_loan", table_name="loan_payment")
    op.drop_table("loan_payment")

    op.drop_index("ix_loan_collateral", table_name="loan")
    op.drop_index("ix_loan_next_payment", table_name="loan")
    op.drop_index("ix_loan_status", table_name="loan")
    op.drop_index("ix_loan_character", table_name="loan")
    op.drop_index("ix_loan_bank", table_name="loan")
    op.drop_table("loan")

    op.drop_index("ix_bank_account_is_frozen", table_name="bank_account")
    op.drop_index("ix_bank_account_is_active", table_name="bank_account")
    op.drop_index("ix_bank_account_kind", table_name="bank_account")
    op.drop_index("ix_bank_account_character", table_name="bank_account")
    op.drop_index("ix_bank_account_bank", table_name="bank_account")
    op.drop_table("bank_account")

    op.drop_index("ix_bank_owner", table_name="bank")
    op.drop_index("ix_bank_is_active", table_name="bank")
    op.drop_index("ix_bank_kind", table_name="bank")
    op.drop_index("ix_bank_code", table_name="bank")
    op.drop_table("bank")