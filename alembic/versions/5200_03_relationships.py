"""relationships between characters

Revision ID: 5200_03
Revises: 5200_02
Create Date: 2026-09-20

"""
from typing import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "5200_03"
down_revision: str | None = "5200_02"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "relationship",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "from_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=False,
        ),
        sa.Column(
            "to_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=False,
        ),
        sa.Column("kind", sa.String(length=24), nullable=False),
        sa.Column("strength", sa.Float(), nullable=False, server_default="0.5"),
        sa.Column("since_total_seconds", sa.BigInteger(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["from_id"], ["character.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["to_id"], ["character.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("from_id", "to_id", "kind", name="uq_relationship_triple"),
    )
    op.create_index("ix_relationship_from_id", "relationship", ["from_id"])
    op.create_index("ix_relationship_to_id", "relationship", ["to_id"])
    op.create_index("ix_relationship_kind", "relationship", ["kind"])


def downgrade() -> None:
    op.drop_index("ix_relationship_kind", table_name="relationship")
    op.drop_index("ix_relationship_to_id", table_name="relationship")
    op.drop_index("ix_relationship_from_id", table_name="relationship")
    op.drop_table("relationship")