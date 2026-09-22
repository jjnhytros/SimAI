"""terrain mode: terrain tiles

Revision ID: 5300_07
Revises: 5300_06
Create Date: 2026-09-22

"""
from typing import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "5300_07"
down_revision: str | None = "5300_06"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "terrain_tile",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column("lot_id", sa.Integer(), nullable=False),
        sa.Column("x", sa.Integer(), nullable=False),
        sa.Column("y", sa.Integer(), nullable=False),
        sa.Column(
            "terrain_type",
            sa.String(length=16),
            nullable=False,
            server_default="GRASS",
        ),
        sa.Column(
            "elevation", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "applied_at_total_seconds",
            sa.BigInteger(),
            nullable=False,
            server_default="0",
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
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("lot_id", "x", "y", name="uq_terrain_tile_cell"),
    )
    op.create_index("ix_terrain_tile_lot_id", "terrain_tile", ["lot_id"])
    op.create_index(
        "ix_terrain_tile_terrain_type", "terrain_tile", ["terrain_type"]
    )


def downgrade() -> None:
    op.drop_index("ix_terrain_tile_terrain_type", table_name="terrain_tile")
    op.drop_index("ix_terrain_tile_lot_id", table_name="terrain_tile")
    op.drop_table("terrain_tile")