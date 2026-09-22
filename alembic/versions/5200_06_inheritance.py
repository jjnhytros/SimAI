"""inheritance: athel_balance + owned locations + object ownership

Revision ID: 5200_06
Revises: 5200_05
Create Date: 2026-09-20

"""
from typing import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "5200_06"
down_revision: str | None = "5200_05"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. athel_balance su character
    with op.batch_alter_table("character") as batch_op:
        batch_op.add_column(
            sa.Column(
                "athel_balance",
                sa.BigInteger(),
                nullable=False,
                server_default="0",
            )
        )

    # 2. owner_character_id su game_object
    with op.batch_alter_table("game_object") as batch_op:
        batch_op.add_column(
            sa.Column(
                "owner_character_id",
                sa.BigInteger().with_variant(sa.Integer, "sqlite"),
                nullable=True,
            )
        )
        batch_op.create_index(
            "ix_game_object_owner_character_id", ["owner_character_id"]
        )
        batch_op.create_foreign_key(
            "fk_game_object_owner_character",
            "character",
            ["owner_character_id"],
            ["id"],
            ondelete="SET NULL",
        )

    # 3. character_owned_location
    op.create_table(
        "character_owned_location",
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
            "location_id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            nullable=False,
        ),
        sa.Column("share", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("since_total_seconds", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["character_id"], ["character.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["location_id"], ["location.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "character_id", "location_id", name="uq_owned_location_pair"
        ),
    )
    op.create_index(
        "ix_character_owned_location_character_id",
        "character_owned_location",
        ["character_id"],
    )
    op.create_index(
        "ix_character_owned_location_location_id",
        "character_owned_location",
        ["location_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_character_owned_location_location_id",
        table_name="character_owned_location",
    )
    op.drop_index(
        "ix_character_owned_location_character_id",
        table_name="character_owned_location",
    )
    op.drop_table("character_owned_location")

    with op.batch_alter_table("game_object") as batch_op:
        batch_op.drop_constraint(
            "fk_game_object_owner_character", type_="foreignkey"
        )
        batch_op.drop_index("ix_game_object_owner_character_id")
        batch_op.drop_column("owner_character_id")

    with op.batch_alter_table("character") as batch_op:
        batch_op.drop_column("athel_balance")