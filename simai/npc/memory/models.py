"""Modello SQLAlchemy `Memory`."""

from __future__ import annotations

from typing import Any

from sqlalchemy import BigInteger, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from simai.db.base import Base, IdMixin, TimestampMixin


class Memory(IdMixin, TimestampMixin, Base):
    """Una memoria di un Character.

    Saliency: 0..1. Valence: -1..+1 (negativa -> positiva).
    La saliency decade nel tempo a tasso dipendente da `kind`.
    """

    __tablename__ = "memory"

    owner_id: Mapped[int] = mapped_column(
        ForeignKey("character.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    kind: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    tick_total_seconds: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    saliency: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    valence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    participants_json: Mapped[list[int]] = mapped_column(JSON, default=list, nullable=False)
    tags_json: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    def __repr__(self) -> str:
        return (
            f"Memory(id={self.id}, owner={self.owner_id}, kind={self.kind}, "
            f"saliency={self.saliency:.2f})"
        )


__all__ = ["Memory"]
