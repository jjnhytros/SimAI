"""Modello SQLAlchemy `Addiction`."""

from __future__ import annotations

from sqlalchemy import (
    BigInteger,
    Float,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from simai.db.base import Base, IdMixin, TimestampMixin
from simai.npc.addictions.enums import AddictionKind


class Addiction(IdMixin, TimestampMixin, Base):
    """Una dipendenza di un Character.

    Unique su `(character_id, kind)`. Creata al primo uso che ha successo
    nell'innesco, o via CLI. Rimossa quando `dependence < MIN_DEPENDENCE`
    dopo un lungo periodo di astinenza.
    """

    __tablename__ = "addiction"

    character_id: Mapped[int] = mapped_column(
        ForeignKey("character.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    kind: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    dependence_level: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    tolerance: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    last_use_total_seconds: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    started_at_total_seconds: Mapped[int] = mapped_column(BigInteger, nullable=False)

    __table_args__ = (UniqueConstraint("character_id", "kind", name="uq_addiction_pair"),)

    @property
    def type(self) -> AddictionKind:
        return AddictionKind(self.kind)

    def __repr__(self) -> str:
        return (
            f"Addiction(char={self.character_id}, kind={self.kind}, "
            f"dep={self.dependence_level:.1f}, tol={self.tolerance:.1f})"
        )


__all__ = ["Addiction"]
