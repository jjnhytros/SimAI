"""population census

Revision ID: 5200_07
Revises: 5200_06
Create Date: 2026-09-20

"""
from typing import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "5200_07"
down_revision: str | None = "5400_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "population_census",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("total_alive", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_male", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_female", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_intersex", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("births_this_month", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("deaths_this_month", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("pediatric_breakdown_json", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("psychosocial_breakdown_json", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("recorded_at_total_seconds", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("year", "month", name="uq_population_census_month"),
    )
    op.create_index("ix_population_census_year", "population_census", ["year"])
    op.create_index(
        "ix_population_census_recorded_at_total_seconds",
        "population_census",
        ["recorded_at_total_seconds"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_population_census_recorded_at_total_seconds",
        table_name="population_census",
    )
    op.drop_index("ix_population_census_year", table_name="population_census")
    op.drop_table("population_census")