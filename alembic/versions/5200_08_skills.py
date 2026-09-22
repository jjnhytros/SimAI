"""skills table

Revision ID: 5200_08
Revises: 5200_07
Create Date: 2026-09-20

"""
from typing import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "5200_08"
down_revision: str | None = "5200_07"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "skill",
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
        sa.Column("skill_type", sa.String(length=32), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("progress", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("talent", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("last_used_total_seconds", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["character_id"], ["character.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("character_id", "skill_type", name="uq_skill_pair"),
    )
    op.create_index("ix_skill_character_id", "skill", ["character_id"])
    op.create_index("ix_skill_skill_type", "skill", ["skill_type"])
    op.create_index(
        "ix_skill_last_used_total_seconds", "skill", ["last_used_total_seconds"]
    )


def downgrade() -> None:
    op.drop_index("ix_skill_last_used_total_seconds", table_name="skill")
    op.drop_index("ix_skill_skill_type", table_name="skill")
    op.drop_index("ix_skill_character_id", table_name="skill")
    op.drop_table("skill")