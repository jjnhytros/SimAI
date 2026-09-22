"""buy mode: object catalog

Revision ID: 5300_05
Revises: 5300_04
Create Date: 2026-09-22

"""
from typing import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "5300_05"
down_revision: str | None = "5300_04"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. object_catalog
    op.create_table(
        "object_catalog",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column("type_code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column(
            "category",
            sa.String(length=16),
            nullable=False,
            server_default="FURNITURE",
        ),
        sa.Column(
            "base_price", sa.Integer(), nullable=False, server_default="50"
        ),
        sa.Column(
            "footprint_w", sa.Integer(), nullable=False, server_default="1"
        ),
        sa.Column(
            "footprint_h", sa.Integer(), nullable=False, server_default="1"
        ),
        sa.Column(
            "is_wall_mounted",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column(
            "is_container",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column("container_capacity", sa.Integer(), nullable=True),
        sa.Column(
            "icon",
            sa.String(length=32),
            nullable=False,
            server_default="bi-box",
        ),
        sa.Column(
            "interactions_json", sa.JSON(), nullable=False, server_default="[]"
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
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("type_code", name="uq_object_catalog_type_code"),
    )
    op.create_index(
        "ix_object_catalog_type_code", "object_catalog", ["type_code"]
    )
    op.create_index(
        "ix_object_catalog_category", "object_catalog", ["category"]
    )

    # 2. game_object: nuovi campi
    with op.batch_alter_table("game_object") as batch_op:
        batch_op.add_column(
            sa.Column(
                "catalog_type_id",
                sa.BigInteger().with_variant(sa.Integer, "sqlite"),
                nullable=True,
            )
        )
        batch_op.add_column(
            sa.Column(
                "lot_id",
                sa.BigInteger().with_variant(sa.Integer, "sqlite"),
                nullable=True,
            )
        )
        batch_op.add_column(sa.Column("position_x", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("position_y", sa.Integer(), nullable=True))
        batch_op.add_column(
            sa.Column(
                "rotation",
                sa.Integer(),
                nullable=False,
                server_default="0",
            )
        )
        batch_op.create_index(
            "ix_game_object_catalog_type_id", ["catalog_type_id"]
        )
        batch_op.create_index("ix_game_object_lot_id", ["lot_id"])


def downgrade() -> None:
    with op.batch_alter_table("game_object") as batch_op:
        batch_op.drop_index("ix_game_object_lot_id")
        batch_op.drop_index("ix_game_object_catalog_type_id")
        batch_op.drop_column("rotation")
        batch_op.drop_column("position_y")
        batch_op.drop_column("position_x")
        batch_op.drop_column("lot_id")
        batch_op.drop_column("catalog_type_id")

    op.drop_index("ix_object_catalog_category", table_name="object_catalog")
    op.drop_index(
        "ix_object_catalog_type_code", table_name="object_catalog"
    )
    op.drop_table("object_catalog")