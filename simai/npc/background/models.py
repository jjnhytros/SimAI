"""Modello SQLAlchemy `FormativeEvent`."""

from __future__ import annotations

from typing import Any

from sqlalchemy import (
    BigInteger,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from simai.db.base import Base, IdMixin, TimestampMixin
from simai.npc.background.enums import FormativeEventKind


class FormativeEvent(IdMixin, TimestampMixin, Base):
    """Evento formativo nel passato di un Character.

    Unique su `(character_id, kind, occurred_at_age)`: previene duplicati
    dello stesso tipo allo stesso anno di età.
    """

    __tablename__ = "formative_event"

    character_id: Mapped[int] = mapped_column(
        ForeignKey("character.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    kind: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    occurred_at_age: Mapped[int] = mapped_column(Integer, nullable=False)
    occurred_at_total_seconds: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    severity: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    text: Mapped[str] = mapped_column(String(256), nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "character_id",
            "kind",
            "occurred_at_age",
            name="uq_formative_event",
        ),
    )

    @property
    def type(self) -> FormativeEventKind:
        return FormativeEventKind(self.kind)

    def __repr__(self) -> str:
        return (
            f"FormativeEvent(char={self.character_id}, kind={self.kind}, "
            f"age={self.occurred_at_age}, sev={self.severity:.2f})"
        )


__all__ = ["FormativeEvent"]
