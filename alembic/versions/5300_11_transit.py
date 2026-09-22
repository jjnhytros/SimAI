"""transit jobs (temporal in-transit state)

Revision ID: 5300_11
Revises: 5300_10
Create Date: 2026-09-22

"""
from typing import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "5300_11"
down_revision: str | None = "5300_10"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "transit_job",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "character_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=False,
        ),
        sa.Column(
            "from_location_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=False,
        ),
        sa.Column(
            "to_location_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=False,
        ),
        sa.Column("mode", sa.String(length=8), nullable=False),
        sa.Column("started_at_total_seconds", sa.BigInteger(), nullable=False),
        sa.Column("arrives_at_total_seconds", sa.BigInteger(), nullable=False),
        sa.Column(
            "route_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=True,
        ),
        sa.Column("cost_paid", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "fuel_consumed", sa.Float(), nullable=False, server_default="0.0"
        ),
        sa.Column(
            "status",
            sa.String(length=16),
            nullable=False,
            server_default="ACTIVE",
        ),
        sa.Column("metadata_json", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column(
            "created_at", sa.DateTime(),
            server_default=sa.func.now(), nullable=False,
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["character_id"], ["character.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["from_location_id"], ["location.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["to_location_id"], ["location.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["route_id"], ["transport_route.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_transit_job_character_id", "transit_job", ["character_id"]
    )
    op.create_index(
        "ix_transit_job_to_location_id", "transit_job", ["to_location_id"]
    )
    op.create_index(
        "ix_transit_job_status", "transit_job", ["status"]
    )
    op.create_index(
        "ix_transit_job_started_at_total_seconds",
        "transit_job",
        ["started_at_total_seconds"],
    )
    op.create_index(
        "ix_transit_job_arrives_at_total_seconds",
        "transit_job",
        ["arrives_at_total_seconds"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_transit_job_arrives_at_total_seconds", table_name="transit_job"
    )
    op.drop_index(
        "ix_transit_job_started_at_total_seconds", table_name="transit_job"
    )
    op.drop_index("ix_transit_job_status", table_name="transit_job")
    op.drop_index("ix_transit_job_to_location_id", table_name="transit_job")
    op.drop_index("ix_transit_job_character_id", table_name="transit_job")
    op.drop_table("transit_job")