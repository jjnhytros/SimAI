"""build mode: walls and openings

Revision ID: 5300_04
Revises: 5300_03
Create Date: 2026-09-22

"""
from typing import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "5300_04"
down_revision: str | None = "5300_03"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "wall",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "lot_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=False,
        ),
        sa.Column("x", sa.Integer(), nullable=False),
        sa.Column("y", sa.Integer(), nullable=False),
        sa.Column(
            "orientation",
            sa.String(length=1),
            nullable=False,
            server_default="H",
        ),
        sa.Column(
            "material",
            sa.String(length=16),
            nullable=False,
            server_default="WOOD",
        ),
        sa.Column("quality", sa.Float(), nullable=False, server_default="1.0"),
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
        sa.ForeignKeyConstraint(["lot_id"], ["lot.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "lot_id", "x", "y", "orientation", name="uq_wall_segment"
        ),
    )
    op.create_index("ix_wall_lot_id", "wall", ["lot_id"])

    op.create_table(
        "opening",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "lot_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=False,
        ),
        sa.Column(
            "wall_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=False,
        ),
        sa.Column(
            "kind",
            sa.String(length=8),
            nullable=False,
            server_default="DOOR",
        ),
        sa.Column(
            "is_locked",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
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
        sa.ForeignKeyConstraint(["lot_id"], ["lot.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["wall_id"], ["wall.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("wall_id", name="uq_opening_wall"),
    )
    op.create_index("ix_opening_lot_id", "opening", ["lot_id"])
    op.create_index("ix_opening_wall_id", "opening", ["wall_id"])


def downgrade() -> None:
    op.drop_index("ix_opening_wall_id", table_name="opening")
    op.drop_index("ix_opening_lot_id", table_name="opening")
    op.drop_table("opening")
    op.drop_index("ix_wall_lot_id", table_name="wall")
    op.drop_table("wall")