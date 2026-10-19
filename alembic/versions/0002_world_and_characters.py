"""world and characters

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-20

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "locations",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("key", sa.String(32), nullable=False, unique=True),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("kind", sa.String(32), nullable=False),
        sa.Column(
            "description",
            sa.Text,
            nullable=False,
            server_default="",
        ),
        sa.Column(
            "capacity",
            sa.Integer,
            nullable=False,
            server_default="8",
        ),
    )
    op.create_table(
        "characters",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("key", sa.String(32), nullable=False, unique=True),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("age_years", sa.Integer, nullable=False),
        sa.Column(
            "is_player",
            sa.Boolean,
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "location_id",
            sa.Integer,
            sa.ForeignKey("locations.id"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("characters")
    op.drop_table("locations")