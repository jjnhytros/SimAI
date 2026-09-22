"""Modello SQLAlchemy `Relationship`."""

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


class Relationship(IdMixin, TimestampMixin, Base):
    """Relazione tra due Character.

    Convenzioni:
      - `PARENT_OF` e `MENTOR_OF` sono **dirette**: `from_id` è il genitore
        (o mentor) di `to_id`. Una sola riga per coppia.
      - Le altre relazioni sono **simmetriche**: la stessa relazione è
        memorizzata due volte (`from→to` e `to→from`) per uniformare le query.
    """

    __tablename__ = "relationship"

    from_id: Mapped[int] = mapped_column(
        ForeignKey("character.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    to_id: Mapped[int] = mapped_column(
        ForeignKey("character.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    kind: Mapped[str] = mapped_column(String(24), nullable=False, index=True)

    #: Intensità della relazione (0.0 = minima, 1.0 = massima).
    strength: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)

    #: Tick Anthalys (total_seconds) da cui la relazione è attiva.
    since_total_seconds: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    __table_args__ = (UniqueConstraint("from_id", "to_id", "kind", name="uq_relationship_triple"),)

    def __repr__(self) -> str:
        return (
            f"Relationship(from={self.from_id}, to={self.to_id}, "
            f"kind={self.kind}, strength={self.strength:.2f})"
        )


__all__ = ["Relationship"]
