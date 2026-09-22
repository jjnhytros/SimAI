"""drop legacy transaction table

Revision ID: 6000_02
Revises: 6000_01
Create Date: 2026-09-22

Chunk 5.1d — FASE 5 Economy: rimozione della tabella `transaction`.

Il ledger double-entry (`ledger_account`, `journal_entry`, `posting`)
è ora la sorgente di verità per tutti i movimenti economici.

Il downgrade ricrea la tabella **vuota** (i dati storici non sono
recuperabili).
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "6000_02"
down_revision = "6000_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Gli indici della tabella `transaction` possono avere nomi diversi
    # a seconda di come è stata creata in `5400_XX`. Usiamo `if_exists=True`
    # per essere tolleranti. In SQLite `DROP TABLE` droppa comunque
    # automaticamente tutti gli indici residui.
    op.drop_index("ix_transaction_at", table_name="transaction", if_exists=True)
    op.drop_index("ix_transaction_kind", table_name="transaction", if_exists=True)
    op.drop_index(
        "ix_transaction_counterparty", table_name="transaction", if_exists=True
    )
    op.drop_index("ix_transaction_character", table_name="transaction", if_exists=True)
    op.drop_table("transaction")


def downgrade() -> None:
    op.create_table(
        "transaction",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column("character_id", sa.BigInteger().with_variant(sa.Integer, "sqlite"), nullable=False),
        sa.Column("kind", sa.String(length=16), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("counterparty_id", sa.BigInteger().with_variant(sa.Integer, "sqlite"), nullable=True),
        sa.Column("location_id", sa.BigInteger().with_variant(sa.Integer, "sqlite"), nullable=True),
        sa.Column("item_type", sa.String(length=64), nullable=True),
        sa.Column("at_total_seconds", sa.BigInteger(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["character_id"], ["character.id"], name="fk_transaction_character", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["counterparty_id"], ["character.id"], name="fk_transaction_counterparty", ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["location_id"], ["location.id"], name="fk_transaction_location", ondelete="SET NULL"
        ),
    )
    op.create_index("ix_transaction_character", "transaction", ["character_id"])
    op.create_index("ix_transaction_counterparty", "transaction", ["counterparty_id"])
    op.create_index("ix_transaction_kind", "transaction", ["kind"])
    op.create_index("ix_transaction_at", "transaction", ["at_total_seconds"])