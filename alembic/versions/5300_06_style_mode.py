"""style mode: style catalog, floor tiles, wall coverings

Revision ID: 5300_06
Revises: 5300_05
Create Date: 2026-09-22

"""
from typing import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "5300_06"
down_revision: str | None = "5300_05"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "style_catalog",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column("type_code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column(
            "kind",
            sa.String(length=8),
            nullable=False,
            server_default="FLOOR",
        ),
        sa.Column(
            "color_hex",
            sa.String(length=9),
            nullable=False,
            server_default="#808080",
        ),
        sa.Column("base_price", sa.Integer(), nullable=False, server_default="10"),
        sa.Column(
            "pattern",
            sa.String(length=32),
            nullable=False,
            server_default="solid",
        ),
        sa.Column(
            "icon",
            sa.String(length=32),
            nullable=False,
            server_default="bi-palette",
        ),
        sa.Column("metadata_json", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("type_code", name="uq_style_catalog_type_code"),
    )
    op.create_index("ix_style_catalog_type_code", "style_catalog", ["type_code"])
    op.create_index("ix_style_catalog_kind", "style_catalog", ["kind"])

    op.create_table(
        "floor_tile",
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
            "style_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=False,
        ),
        sa.Column("applied_at_total_seconds", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["lot_id"], ["lot.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["style_id"], ["style_catalog.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("lot_id", "x", "y", name="uq_floor_tile_cell"),
    )
    op.create_index("ix_floor_tile_lot_id", "floor_tile", ["lot_id"])
    op.create_index("ix_floor_tile_style_id", "floor_tile", ["style_id"])

    op.create_table(
        "wall_covering",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "wall_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=False,
        ),
        sa.Column(
            "side",
            sa.String(length=8),
            nullable=False,
            server_default="INTERIOR",
        ),
        sa.Column(
            "style_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=False,
        ),
        sa.Column("applied_at_total_seconds", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["wall_id"], ["wall.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["style_id"], ["style_catalog.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("wall_id", "side", name="uq_wall_covering_side"),
    )
    op.create_index("ix_wall_covering_wall_id", "wall_covering", ["wall_id"])
    op.create_index("ix_wall_covering_style_id", "wall_covering", ["style_id"])


def downgrade() -> None:
    op.drop_index("ix_wall_covering_style_id", table_name="wall_covering")
    op.drop_index("ix_wall_covering_wall_id", table_name="wall_covering")
    op.drop_table("wall_covering")

    op.drop_index("ix_floor_tile_style_id", table_name="floor_tile")
    op.drop_index("ix_floor_tile_lot_id", table_name="floor_tile")
    op.drop_table("floor_tile")

    op.drop_index("ix_style_catalog_kind", table_name="style_catalog")
    op.drop_index("ix_style_catalog_type_code", table_name="style_catalog")
    op.drop_table("style_catalog")