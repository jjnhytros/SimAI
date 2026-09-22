"""job skill requirements

Revision ID: 5400_02
Revises: 5200_08
Create Date: 2026-09-20

"""
from typing import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "5400_02"
down_revision: str | None = "5200_08"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("job") as batch_op:
        batch_op.add_column(
            sa.Column("required_skill_type", sa.String(length=32), nullable=True)
        )
        batch_op.add_column(
            sa.Column(
                "min_skill_level", sa.Integer(), nullable=False, server_default="0"
            )
        )
        batch_op.add_column(
            sa.Column(
                "wage_skill_scale",
                sa.Float(),
                nullable=False,
                server_default="0.0",
            )
        )
        batch_op.add_column(
            sa.Column(
                "promotion_skill_level",
                sa.Integer(),
                nullable=False,
                server_default="10",
            )
        )
        batch_op.add_column(
            sa.Column("promoted_title", sa.String(length=64), nullable=True)
        )
        batch_op.create_index(
            "ix_job_required_skill_type", ["required_skill_type"]
        )


def downgrade() -> None:
    with op.batch_alter_table("job") as batch_op:
        batch_op.drop_index("ix_job_required_skill_type")
        batch_op.drop_column("promoted_title")
        batch_op.drop_column("promotion_skill_level")
        batch_op.drop_column("wage_skill_scale")
        batch_op.drop_column("min_skill_level")
        batch_op.drop_column("required_skill_type")