"""Modelli SQLAlchemy del dominio reputazione."""

from __future__ import annotations

from typing import Any

from sqlalchemy import (
    BigInteger,
    Float,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from simai.db.base import Base, IdMixin, TimestampMixin


class Opinion(IdMixin, TimestampMixin, Base):
    """Opinione di un Character su un altro."""

    __tablename__ = "opinion"

    observer_id: Mapped[int] = mapped_column(
        ForeignKey("character.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_id: Mapped[int] = mapped_column(
        ForeignKey("character.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    last_updated_at_total_seconds: Mapped[int] = mapped_column(BigInteger, nullable=False)

    __table_args__ = (UniqueConstraint("observer_id", "target_id", name="uq_opinion_pair"),)

    def __repr__(self) -> str:
        return f"Opinion(obs={self.observer_id}, target={self.target_id}, score={self.score:+.1f})"


class GossipEvent(IdMixin, TimestampMixin, Base):
    """Un pettegolezzo propagato tra due character (audit + saliency)."""

    __tablename__ = "gossip_event"

    source_id: Mapped[int] = mapped_column(
        ForeignKey("character.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_id: Mapped[int] = mapped_column(
        ForeignKey("character.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    listener_id: Mapped[int] = mapped_column(
        ForeignKey("character.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    topic: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    sentiment: Mapped[float] = mapped_column(Float, nullable=False)
    strength: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    text: Mapped[str] = mapped_column(String(256), nullable=False)
    occurred_at_total_seconds: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    def __repr__(self) -> str:
        return (
            f"GossipEvent({self.source_id}->{self.listener_id} about "
            f"{self.target_id}, topic={self.topic})"
        )


__all__ = ["GossipEvent", "Opinion"]
