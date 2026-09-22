"""transport: vehicles and routes

Revision ID: 5300_10
Revises: 5300_09
Create Date: 2026-09-22

"""
from typing import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "5300_10"
down_revision: str | None = "5300_09"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "vehicle",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer, "sqlite"), autoincrement=True, nullable=False),
        sa.Column("owner_id", sa.BigInteger().with_variant(sa.Integer, "sqlite"), nullable=False),
        sa.Column("vehicle_type", sa.String(length=8), nullable=False, server_default="BIKE"),
        sa.Column("fuel", sa.Float(), nullable=False, server_default="100.0"),
        sa.Column("condition", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("location_id", sa.BigInteger().with_variant(sa.Integer, "sqlite"), nullable=True),
        sa.Column("is_parked", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("metadata_json", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["character.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["location_id"], ["location.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("owner_id", "vehicle_type", name="uq_vehicle_owner_type"),
    )
    op.create_index("ix_vehicle_owner_id", "vehicle", ["owner_id"])
    op.create_index("ix_vehicle_vehicle_type", "vehicle", ["vehicle_type"])
    op.create_index("ix_vehicle_location_id", "vehicle", ["location_id"])

    op.create_table(
        "transport_route",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer, "sqlite"), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("route_type", sa.String(length=8), nullable=False, server_default="BUS"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("base_fare", sa.Integer(), nullable=False, server_default="2"),
        sa.Column("speed_cells_per_tick", sa.Float(), nullable=False, server_default="3.0"),
        sa.Column("metadata_json", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_transport_route_route_type", "transport_route", ["route_type"])
    op.create_index("ix_transport_route_is_active", "transport_route", ["is_active"])

    op.create_table(
        "route_stop",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer, "sqlite"), autoincrement=True, nullable=False),
        sa.Column("route_id", sa.BigInteger().with_variant(sa.Integer, "sqlite"), nullable=False),
        sa.Column("location_id", sa.BigInteger().with_variant(sa.Integer, "sqlite"), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["route_id"], ["transport_route.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["location_id"], ["location.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("route_id", "sequence", name="uq_route_stop_seq"),
        sa.UniqueConstraint("route_id", "location_id", name="uq_route_stop_loc"),
    )
    op.create_index("ix_route_stop_route_id", "route_stop", ["route_id"])
    op.create_index("ix_route_stop_location_id", "route_stop", ["location_id"])


def downgrade() -> None:
    op.drop_index("ix_route_stop_location_id", table_name="route_stop")
    op.drop_index("ix_route_stop_route_id", table_name="route_stop")
    op.drop_table("route_stop")
    op.drop_index("ix_transport_route_is_active", table_name="transport_route")
    op.drop_index("ix_transport_route_route_type", table_name="transport_route")
    op.drop_table("transport_route")
    op.drop_index("ix_vehicle_location_id", table_name="vehicle")
    op.drop_index("ix_vehicle_vehicle_type", table_name="vehicle")
    op.drop_index("ix_vehicle_owner_id", table_name="vehicle")
    op.drop_table("vehicle")