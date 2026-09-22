"""lot ownership and mortgages

Revision ID: 5300_03
Revises: 5300_02
Create Date: 2026-09-21

"""
from typing import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "5300_03"
down_revision: str | None = "5300_02"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "lot_ownership",
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
        sa.Column(
            "lot_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=False,
        ),
        sa.Column("share", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("purchase_price", sa.Integer(), nullable=False),
        sa.Column("purchase_at_total_seconds", sa.BigInteger(), nullable=False),
        sa.Column(
            "metadata_json", sa.JSON(), nullable=False, server_default="{}"
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
            ["character_id"], ["character.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["lot_id"], ["lot.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "character_id", "lot_id", name="uq_lot_ownership_pair"
        ),
    )
    op.create_index(
        "ix_lot_ownership_character_id", "lot_ownership", ["character_id"]
    )
    op.create_index("ix_lot_ownership_lot_id", "lot_ownership", ["lot_id"])

    op.create_table(
        "mortgage",
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
        sa.Column(
            "lot_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=False,
        ),
        sa.Column("principal", sa.Integer(), nullable=False),
        sa.Column(
            "remaining_principal", sa.Float(), nullable=False
        ),
        sa.Column("annual_interest_rate", sa.Float(), nullable=False),
        sa.Column("term_months", sa.Integer(), nullable=False),
        sa.Column("monthly_payment", sa.Integer(), nullable=False),
        sa.Column(
            "payments_made",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "payments_missed",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "next_payment_at_total_seconds", sa.BigInteger(), nullable=False
        ),
        sa.Column("started_at_total_seconds", sa.BigInteger(), nullable=False),
        sa.Column(
            "status",
            sa.String(length=16),
            nullable=False,
            server_default="ACTIVE",
        ),
        sa.Column(
            "metadata_json", sa.JSON(), nullable=False, server_default="{}"
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
            ["character_id"], ["character.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["lot_id"], ["lot.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_mortgage_character_id", "mortgage", ["character_id"])
    op.create_index("ix_mortgage_lot_id", "mortgage", ["lot_id"])
    op.create_index("ix_mortgage_status", "mortgage", ["status"])
    op.create_index(
        "ix_mortgage_next_payment_at_total_seconds",
        "mortgage",
        ["next_payment_at_total_seconds"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_mortgage_next_payment_at_total_seconds", table_name="mortgage"
    )
    op.drop_index("ix_mortgage_status", table_name="mortgage")
    op.drop_index("ix_mortgage_lot_id", table_name="mortgage")
    op.drop_index("ix_mortgage_character_id", table_name="mortgage")
    op.drop_table("mortgage")

    op.drop_index("ix_lot_ownership_lot_id", table_name="lot_ownership")
    op.drop_index(
        "ix_lot_ownership_character_id", table_name="lot_ownership"
    )
    op.drop_table("lot_ownership")