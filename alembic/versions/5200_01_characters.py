"""character table

Revision ID: 5200_01
Revises: 5300_01
Create Date: 2026-09-20

Note:
    Il range 5200-5299 è per il modulo NPC. La catena `down_revision`
    punta a `5300_01` (world) perché `character.location_id` referenzia
    `location.id`, che deve esistere prima.
"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "5200_01"
down_revision: str | None = "5300_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "character",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column("first_name", sa.String(length=64), nullable=False),
        sa.Column("last_name", sa.String(length=64), nullable=False),
        sa.Column("sex", sa.String(length=16), nullable=False),
        sa.Column("gender", sa.String(length=32), nullable=False, server_default="unspecified"),
        sa.Column("birth_total_seconds", sa.BigInteger(), nullable=False),
        sa.Column("birth_iso", sa.String(length=20), nullable=False),
        sa.Column("death_total_seconds", sa.BigInteger(), nullable=True),
        sa.Column("death_iso", sa.String(length=20), nullable=True),
        sa.Column("is_alive", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("life_stage_pediatric", sa.String(length=24), nullable=False),
        sa.Column("life_stage_psychosocial", sa.String(length=24), nullable=False),
        sa.Column(
            "location_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=True,
        ),
        sa.Column("master_seed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("appearance_json", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("traits_json", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("aspirations_json", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("genome_json", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("attributes_json", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["location_id"], ["location.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_character_first_name", "character", ["first_name"])
    op.create_index("ix_character_last_name", "character", ["last_name"])
    op.create_index("ix_character_sex", "character", ["sex"])
    op.create_index("ix_character_is_alive", "character", ["is_alive"])
    op.create_index(
        "ix_character_life_stage_pediatric", "character", ["life_stage_pediatric"]
    )
    op.create_index(
        "ix_character_life_stage_psychosocial",
        "character",
        ["life_stage_psychosocial"],
    )
    op.create_index(
        "ix_character_birth_total_seconds", "character", ["birth_total_seconds"]
    )
    op.create_index(
        "ix_character_death_total_seconds", "character", ["death_total_seconds"]
    )
    op.create_index("ix_character_location_id", "character", ["location_id"])


def downgrade() -> None:
    op.drop_index("ix_character_location_id", table_name="character")
    op.drop_index("ix_character_death_total_seconds", table_name="character")
    op.drop_index("ix_character_birth_total_seconds", table_name="character")
    op.drop_index("ix_character_life_stage_psychosocial", table_name="character")
    op.drop_index("ix_character_life_stage_pediatric", table_name="character")
    op.drop_index("ix_character_is_alive", table_name="character")
    op.drop_index("ix_character_sex", table_name="character")
    op.drop_index("ix_character_last_name", table_name="character")
    op.drop_index("ix_character_first_name", table_name="character")
    op.drop_table("character")