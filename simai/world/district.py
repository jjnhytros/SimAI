"""District — quartiere con bounds, tassazione locale, qualità."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from simai.db.base import Base, IdMixin, TimestampMixin
from simai.world.enums import DistrictType


class District(IdMixin, TimestampMixin, Base):
    """Un quartiere della città."""

    __tablename__ = "district"

    name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    type: Mapped[str] = mapped_column(
        String(16), nullable=False, default=DistrictType.MIXED.value, index=True
    )

    # Griglia 2D
    bounds_x: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    bounds_y: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    bounds_w: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    bounds_h: Mapped[int] = mapped_column(Integer, default=50, nullable=False)

    # Tassazione e rating locale
    tax_rate: Mapped[float] = mapped_column(Float, default=0.05, nullable=False)
    safety_rating: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    aesthetic_score: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)

    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    def center(self) -> tuple[float, float]:
        return (
            self.bounds_x + self.bounds_w / 2.0,
            self.bounds_y + self.bounds_h / 2.0,
        )

    def __repr__(self) -> str:
        return f"District(id={self.id}, name={self.name!r}, type={self.type})"


@dataclass(frozen=True, slots=True)
class DistrictSummary:
    """Riepilogo per UI/CLI."""

    id: int
    name: str
    type: str
    bounds: tuple[int, int, int, int]
    tax_rate: float
    lot_count: int


__all__ = ["District", "DistrictSummary"]
