"""Modello SQLAlchemy `ReflectionEntry`."""

from __future__ import annotations

from typing import Any

from sqlalchemy import BigInteger, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from simai.db.base import Base, IdMixin, TimestampMixin
from simai.npc.reflection.enums import ReflectionKind


class ReflectionEntry(IdMixin, TimestampMixin, Base):
    """Entry di diario / riflessione personale."""

    __tablename__ = "reflection_entry"

    character_id: Mapped[int] = mapped_column(
        ForeignKey("character.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    kind: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    at_total_seconds: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    sentiment: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    @property
    def type(self) -> ReflectionKind:
        return ReflectionKind(self.kind)

    def __repr__(self) -> str:
        return (
            f"ReflectionEntry(char={self.character_id}, "
            f"kind={self.kind}, sent={self.sentiment:+.2f})"
        )


__all__ = ["ReflectionEntry"]
