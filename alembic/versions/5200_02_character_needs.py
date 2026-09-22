"""character needs, mood, current action

Revision ID: 5200_02
Revises: 5200_01
Create Date: 2026-09-20

"""
from typing import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "5200_02"
down_revision: str | None = "5200_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("character") as batch_op:
        batch_op.add_column(
            sa.Column(
                "needs_json",
                sa.JSON(),
                nullable=False,
                server_default="{}",
            )
        )
        batch_op.add_column(
            sa.Column(
                "mood_json",
                sa.JSON(),
                nullable=False,
                server_default="{}",
            )
        )
        batch_op.add_column(
            sa.Column(
                "current_action_json",
                sa.JSON(),
                nullable=True,
            )
        )
        batch_op.add_column(
            sa.Column(
                "last_ai_tick",
                sa.BigInteger(),
                nullable=False,
                server_default="0",
            )
        )


def downgrade() -> None:
    with op.batch_alter_table("character") as batch_op:
        batch_op.drop_column("last_ai_tick")
        batch_op.drop_column("current_action_json")
        batch_op.drop_column("mood_json")
        batch_op.drop_column("needs_json")