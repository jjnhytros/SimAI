"""locations and game objects

Revision ID: 5300_01
Revises: 5000_01
Create Date: 2026-09-20

"""
from typing import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "5300_01"
down_revision: str | None = "5000_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "location",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("type", sa.String(length=16), nullable=False),
        sa.Column("parent_id", sa.BigInteger().with_variant(sa.Integer, "sqlite"), nullable=True),
        sa.Column("lot_id", sa.Integer(), nullable=True),
        sa.Column("bounds_x", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("bounds_y", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("bounds_w", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("bounds_h", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("capacity", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("cleanliness_level", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("noise_level", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("crowd_level", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("safety_rating", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("aesthetic_score", sa.Float(), nullable=False, server_default="0.5"),
        sa.Column("attributes_json", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["parent_id"], ["location.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_location_name", "location", ["name"])
    op.create_index("ix_location_type", "location", ["type"])
    op.create_index("ix_location_parent_id", "location", ["parent_id"])
    op.create_index("ix_location_lot_id", "location", ["lot_id"])

    op.create_table(
        "location_edge",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column("from_location_id", sa.BigInteger().with_variant(sa.Integer, "sqlite"), nullable=False),
        sa.Column("to_location_id", sa.BigInteger().with_variant(sa.Integer, "sqlite"), nullable=False),
        sa.Column("kind", sa.String(length=16), nullable=False, server_default="DOOR"),
        sa.Column("distance", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("bidirectional", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_accessible", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.ForeignKeyConstraint(["from_location_id"], ["location.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["to_location_id"], ["location.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("from_location_id", "to_location_id", name="uq_location_edge_pair"),
    )
    op.create_index("ix_location_edge_from", "location_edge", ["from_location_id"])
    op.create_index("ix_location_edge_to", "location_edge", ["to_location_id"])

    op.create_table(
        "game_object",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("type", sa.String(length=64), nullable=False),
        sa.Column("location_id", sa.BigInteger().with_variant(sa.Integer, "sqlite"), nullable=True),
        sa.Column("state", sa.String(length=16), nullable=False, server_default="NEW"),
        sa.Column("condition", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("container_capacity", sa.Integer(), nullable=True),
        sa.Column("container_contents_json", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("interactions_json", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("metadata_json", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["location_id"], ["location.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_game_object_name", "game_object", ["name"])
    op.create_index("ix_game_object_type", "game_object", ["type"])
    op.create_index("ix_game_object_location_id", "game_object", ["location_id"])


def downgrade() -> None:
    op.drop_index("ix_game_object_location_id", table_name="game_object")
    op.drop_index("ix_game_object_type", table_name="game_object")
    op.drop_index("ix_game_object_name", table_name="game_object")
    op.drop_table("game_object")

    op.drop_index("ix_location_edge_to", table_name="location_edge")
    op.drop_index("ix_location_edge_from", table_name="location_edge")
    op.drop_table("location_edge")

    op.drop_index("ix_location_lot_id", table_name="location")
    op.drop_index("ix_location_parent_id", table_name="location")
    op.drop_index("ix_location_type", table_name="location")
    op.drop_index("ix_location_name", table_name="location")
    op.drop_table("location")