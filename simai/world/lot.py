"""Lot — lotto edificabile con bounds, uso, prezzo base."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from simai.db.base import Base, IdMixin, TimestampMixin
from simai.world.enums import LotUsage


class Lot(IdMixin, TimestampMixin, Base):
    """Un lotto edificabile in un quartiere."""

    __tablename__ = "lot"

    district_id: Mapped[int] = mapped_column(
        ForeignKey("district.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    usage: Mapped[str] = mapped_column(
        String(16), nullable=False, default=LotUsage.VACANT.value, index=True
    )

    # Griglia 2D
    bounds_x: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    bounds_y: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    bounds_w: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    bounds_h: Mapped[int] = mapped_column(Integer, default=10, nullable=False)

    # Economia
    base_price: Mapped[int] = mapped_column(Integer, default=1000, nullable=False)
    is_developed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Location "centrale" (l'edificio sul lotto, se esiste)
    location_id: Mapped[int | None] = mapped_column(
        ForeignKey("location.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    # Rating dinamici (aggiornabili)
    current_value: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    def __repr__(self) -> str:
        return f"Lot(id={self.id}, name={self.name!r}, usage={self.usage}, price={self.base_price})"


@dataclass(frozen=True, slots=True)
class LotSummary:
    """Riepilogo per UI/CLI."""

    id: int
    name: str
    district_id: int
    usage: str
    bounds: tuple[int, int, int, int]
    base_price: int
    is_developed: bool
    location_id: int | None


__all__ = ["Lot", "LotSummary"]
