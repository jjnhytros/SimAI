"""infrastructure: roads and street lights

Revision ID: 5300_09
Revises: 5300_08
Create Date: 2026-09-22

"""
from typing import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "5300_09"
down_revision: str | None = "5300_08"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "road_tile",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column("x", sa.Integer(), nullable=False),
        sa.Column("y", sa.Integer(), nullable=False),
        sa.Column(
            "road_type",
            sa.String(length=16),
            nullable=False,
            server_default="STREET",
        ),
        sa.Column(
            "condition", sa.Float(), nullable=False, server_default="1.0"
        ),
        sa.Column(
            "district_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=True,
        ),
        sa.Column(
            "applied_at_total_seconds",
            sa.BigInteger(),
            nullable=False,
            server_default="0",
        ),
        sa.Column("metadata_json", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column(
            "created_at", sa.DateTime(),
            server_default=sa.func.now(), nullable=False,
        ),
        sa.Column(
            "updated_at", sa.DateTime(),
            server_default=sa.func.now(), nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["district_id"], ["district.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("x", "y", name="uq_road_tile_cell"),
    )
    op.create_index("ix_road_tile_x", "road_tile", ["x"])
    op.create_index("ix_road_tile_y", "road_tile", ["y"])
    op.create_index("ix_road_tile_district_id", "road_tile", ["district_id"])

    op.create_table(
        "street_light",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column("x", sa.Integer(), nullable=False),
        sa.Column("y", sa.Integer(), nullable=False),
        sa.Column(
            "light_type",
            sa.String(length=16),
            nullable=False,
            server_default="STANDARD",
        ),
        sa.Column(
            "radius", sa.Integer(), nullable=False, server_default="3"
        ),
        sa.Column(
            "condition", sa.Float(), nullable=False, server_default="1.0"
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        sa.Column(
            "district_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=True,
        ),
        sa.Column(
            "applied_at_total_seconds",
            sa.BigInteger(),
            nullable=False,
            server_default="0",
        ),
        sa.Column("metadata_json", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column(
            "created_at", sa.DateTime(),
            server_default=sa.func.now(), nullable=False,
        ),
        sa.Column(
            "updated_at", sa.DateTime(),
            server_default=sa.func.now(), nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["district_id"], ["district.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("x", "y", name="uq_street_light_cell"),
    )
    op.create_index("ix_street_light_x", "street_light", ["x"])
    op.create_index("ix_street_light_y", "street_light", ["y"])
    op.create_index(
        "ix_street_light_is_active", "street_light", ["is_active"]
    )
    op.create_index(
        "ix_street_light_district_id", "street_light", ["district_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_street_light_district_id", table_name="street_light")
    op.drop_index("ix_street_light_is_active", table_name="street_light")
    op.drop_index("ix_street_light_y", table_name="street_light")
    op.drop_index("ix_street_light_x", table_name="street_light")
    op.drop_table("street_light")
    op.drop_index("ix_road_tile_district_id", table_name="road_tile")
    op.drop_index("ix_road_tile_y", table_name="road_tile")
    op.drop_index("ix_road_tile_x", table_name="road_tile")
    op.drop_table("road_tile")