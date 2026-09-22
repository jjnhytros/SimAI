"""opinion and gossip_event tables

Revision ID: 5200_11
Revises: 5200_10
Create Date: 2026-09-21

"""
from typing import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "5200_11"
down_revision: str | None = "5200_10"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "opinion",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer, "sqlite"), autoincrement=True, nullable=False),
        sa.Column("observer_id", sa.BigInteger().with_variant(sa.Integer, "sqlite"), nullable=False),
        sa.Column("target_id", sa.BigInteger().with_variant(sa.Integer, "sqlite"), nullable=False),
        sa.Column("score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("last_updated_at_total_seconds", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["observer_id"], ["character.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["target_id"], ["character.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("observer_id", "target_id", name="uq_opinion_pair"),
    )
    op.create_index("ix_opinion_observer_id", "opinion", ["observer_id"])
    op.create_index("ix_opinion_target_id", "opinion", ["target_id"])

    op.create_table(
        "gossip_event",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer, "sqlite"), autoincrement=True, nullable=False),
        sa.Column("source_id", sa.BigInteger().with_variant(sa.Integer, "sqlite"), nullable=False),
        sa.Column("target_id", sa.BigInteger().with_variant(sa.Integer, "sqlite"), nullable=False),
        sa.Column("listener_id", sa.BigInteger().with_variant(sa.Integer, "sqlite"), nullable=False),
        sa.Column("topic", sa.String(length=32), nullable=False),
        sa.Column("sentiment", sa.Float(), nullable=False),
        sa.Column("strength", sa.Float(), nullable=False, server_default="0.5"),
        sa.Column("text", sa.String(length=256), nullable=False),
        sa.Column("occurred_at_total_seconds", sa.BigInteger(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["character.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["target_id"], ["character.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["listener_id"], ["character.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_gossip_event_source_id", "gossip_event", ["source_id"])
    op.create_index("ix_gossip_event_target_id", "gossip_event", ["target_id"])
    op.create_index("ix_gossip_event_listener_id", "gossip_event", ["listener_id"])
    op.create_index("ix_gossip_event_topic", "gossip_event", ["topic"])
    op.create_index(
        "ix_gossip_event_occurred_at_total_seconds",
        "gossip_event",
        ["occurred_at_total_seconds"],
    )


def downgrade() -> None:
    op.drop_index("ix_gossip_event_occurred_at_total_seconds", table_name="gossip_event")
    op.drop_index("ix_gossip_event_topic", table_name="gossip_event")
    op.drop_index("ix_gossip_event_listener_id", table_name="gossip_event")
    op.drop_index("ix_gossip_event_target_id", table_name="gossip_event")
    op.drop_index("ix_gossip_event_source_id", table_name="gossip_event")
    op.drop_table("gossip_event")

    op.drop_index("ix_opinion_target_id", table_name="opinion")
    op.drop_index("ix_opinion_observer_id", table_name="opinion")
    op.drop_table("opinion")