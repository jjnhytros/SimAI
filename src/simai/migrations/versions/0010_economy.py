"""economy: balance, jobs, transactions

Revision ID: 0010
Revises: 0009
Create Date: 2026-10-20

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0010"
down_revision: str | None = "0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("characters") as batch:
        batch.add_column(
            sa.Column(
                "balance",
                sa.Float,
                nullable=False,
                server_default="100.0",
            )
        )
    op.create_table(
        "jobs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "character_id",
            sa.Integer,
            sa.ForeignKey("characters.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("title", sa.String(32), nullable=False),
        sa.Column("location_key", sa.String(32), nullable=False),
        sa.Column(
            "daily_wage",
            sa.Float,
            nullable=False,
            server_default="0.0",
        ),
        sa.Column(
            "schedule_start_tick",
            sa.Integer,
            nullable=False,
            server_default="8",
        ),
        sa.Column(
            "schedule_end_tick",
            sa.Integer,
            nullable=False,
            server_default="16",
        ),
    )
    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("tick_index", sa.Integer, nullable=False),
        sa.Column(
            "from_character_id",
            sa.Integer,
            sa.ForeignKey("characters.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "to_character_id",
            sa.Integer,
            sa.ForeignKey("characters.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("amount", sa.Float, nullable=False),
        sa.Column("kind", sa.String(16), nullable=False),
        sa.Column(
            "note",
            sa.String(128),
            nullable=False,
            server_default="",
        ),
    )
    op.create_index(
        "ix_transactions_from",
        "transactions",
        ["from_character_id"],
    )
    op.create_index(
        "ix_transactions_to",
        "transactions",
        ["to_character_id"],
    )
    op.create_index(
        "ix_transactions_tick",
        "transactions",
        ["tick_index"],
    )


def downgrade() -> None:
    op.drop_index("ix_transactions_tick", table_name="transactions")
    op.drop_index("ix_transactions_to", table_name="transactions")
    op.drop_index("ix_transactions_from", table_name="transactions")
    op.drop_table("transactions")
    op.drop_table("jobs")
    with op.batch_alter_table("characters") as batch:
        batch.drop_column("balance")
