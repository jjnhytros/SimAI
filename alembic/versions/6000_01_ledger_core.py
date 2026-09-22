"""ledger core: ledger_account, journal_entry, posting

Revision ID: 6000_01
Revises: 5300_11
Create Date: 2026-09-22

Chunk 5.1a — FASE 5 Economy: fondamenta del ledger double-entry.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "6000_01"
down_revision = "5300_11"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- ledger_account ---
    op.create_table(
        "ledger_account",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column("code", sa.String(length=128), nullable=False),
        sa.Column("kind", sa.String(length=16), nullable=False),
        sa.Column("owner_type", sa.String(length=16), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint("code", name="uq_ledger_account_code"),
    )
    op.create_index("ix_ledger_account_code", "ledger_account", ["code"], unique=True)
    op.create_index("ix_ledger_account_kind", "ledger_account", ["kind"])
    op.create_index("ix_ledger_account_owner_type", "ledger_account", ["owner_type"])
    op.create_index("ix_ledger_account_owner_id", "ledger_account", ["owner_id"])
    op.create_index("ix_ledger_account_is_active", "ledger_account", ["is_active"])
    op.create_index(
        "ix_ledger_account_owner", "ledger_account", ["owner_type", "owner_id"]
    )

    # --- journal_entry ---
    op.create_table(
        "journal_entry",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column("kind", sa.String(length=32), nullable=False),
        sa.Column("description", sa.String(length=256), nullable=False),
        sa.Column("at_total_seconds", sa.BigInteger(), nullable=False),
        sa.Column("reference_type", sa.String(length=64), nullable=True),
        sa.Column("reference_id", sa.Integer(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_journal_entry_kind", "journal_entry", ["kind"])
    op.create_index("ix_journal_entry_at", "journal_entry", ["at_total_seconds"])
    op.create_index("ix_journal_entry_ref_type", "journal_entry", ["reference_type"])
    op.create_index("ix_journal_entry_ref_id", "journal_entry", ["reference_id"])

    # --- posting ---
    op.create_table(
        "posting",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column("entry_id", sa.BigInteger().with_variant(sa.Integer, "sqlite"), nullable=False),
        sa.Column(
            "account_id", sa.BigInteger().with_variant(sa.Integer, "sqlite"), nullable=False
        ),
        sa.Column("direction", sa.String(length=8), nullable=False),
        sa.Column("amount", sa.BigInteger(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["entry_id"], ["journal_entry.id"], name="fk_posting_entry", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["account_id"],
            ["ledger_account.id"],
            name="fk_posting_account",
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint("amount > 0", name="ck_posting_amount_positive"),
        sa.UniqueConstraint(
            "entry_id",
            "account_id",
            "direction",
            name="uq_posting_entry_acc_dir",
        ),
    )
    op.create_index("ix_posting_entry", "posting", ["entry_id"])
    op.create_index("ix_posting_account", "posting", ["account_id"])
    op.create_index("ix_posting_direction", "posting", ["direction"])


def downgrade() -> None:
    op.drop_index("ix_posting_direction", table_name="posting")
    op.drop_index("ix_posting_account", table_name="posting")
    op.drop_index("ix_posting_entry", table_name="posting")
    op.drop_table("posting")

    op.drop_index("ix_journal_entry_ref_id", table_name="journal_entry")
    op.drop_index("ix_journal_entry_ref_type", table_name="journal_entry")
    op.drop_index("ix_journal_entry_at", table_name="journal_entry")
    op.drop_index("ix_journal_entry_kind", table_name="journal_entry")
    op.drop_table("journal_entry")

    op.drop_index("ix_ledger_account_owner", table_name="ledger_account")
    op.drop_index("ix_ledger_account_is_active", table_name="ledger_account")
    op.drop_index("ix_ledger_account_owner_id", table_name="ledger_account")
    op.drop_index("ix_ledger_account_owner_type", table_name="ledger_account")
    op.drop_index("ix_ledger_account_kind", table_name="ledger_account")
    op.drop_index("ix_ledger_account_code", table_name="ledger_account")
    op.drop_table("ledger_account")