"""lifecycle: death_cause + pregnancy table

Revision ID: 5200_04
Revises: 5200_03
Create Date: 2026-09-20

"""
from typing import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "5200_04"
down_revision: str | None = "5200_03"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Campo death_cause su character
    with op.batch_alter_table("character") as batch_op:
        batch_op.add_column(
            sa.Column("death_cause", sa.String(length=16), nullable=True)
        )
        batch_op.create_index("ix_character_death_cause", ["death_cause"])

    # 2. Tabella pregnancy
    op.create_table(
        "pregnancy",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "mother_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=False,
        ),
        sa.Column(
            "father_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=True,
        ),
        sa.Column("conception_total_seconds", sa.BigInteger(), nullable=False),
        sa.Column("due_total_seconds", sa.BigInteger(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("completed_total_seconds", sa.BigInteger(), nullable=True),
        sa.Column("child_ids_json", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("metadata_json", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["mother_id"], ["character.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["father_id"], ["character.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_pregnancy_mother_id", "pregnancy", ["mother_id"])
    op.create_index("ix_pregnancy_father_id", "pregnancy", ["father_id"])
    op.create_index("ix_pregnancy_status", "pregnancy", ["status"])
    op.create_index("ix_pregnancy_due_total_seconds", "pregnancy", ["due_total_seconds"])
    op.create_index(
        "ix_pregnancy_conception_total_seconds",
        "pregnancy",
        ["conception_total_seconds"],
    )


def downgrade() -> None:
    op.drop_index("ix_pregnancy_conception_total_seconds", table_name="pregnancy")
    op.drop_index("ix_pregnancy_due_total_seconds", table_name="pregnancy")
    op.drop_index("ix_pregnancy_status", table_name="pregnancy")
    op.drop_index("ix_pregnancy_father_id", table_name="pregnancy")
    op.drop_index("ix_pregnancy_mother_id", table_name="pregnancy")
    op.drop_table("pregnancy")

    with op.batch_alter_table("character") as batch_op:
        batch_op.drop_index("ix_character_death_cause")
        batch_op.drop_column("death_cause")