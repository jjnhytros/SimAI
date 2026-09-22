"""Modelli infrastrutture: RoadTile, StreetLight."""

from __future__ import annotations

from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from simai.city.infrastructure.enums import LightType, RoadType
from simai.db.base import Base, IdMixin, TimestampMixin


class RoadTile(IdMixin, TimestampMixin, Base):
    """Una cella di strada sulla griglia mondiale."""

    __tablename__ = "road_tile"

    x: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    y: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    road_type: Mapped[str] = mapped_column(
        String(16), nullable=False, default=RoadType.STREET.value
    )
    condition: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    district_id: Mapped[int | None] = mapped_column(
        ForeignKey("district.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    applied_at_total_seconds: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    __table_args__ = (UniqueConstraint("x", "y", name="uq_road_tile_cell"),)

    def __repr__(self) -> str:
        return f"RoadTile(({self.x},{self.y}), type={self.road_type}, cond={self.condition:.2f})"


class StreetLight(IdMixin, TimestampMixin, Base):
    """Un lampione pubblico sulla griglia mondiale."""

    __tablename__ = "street_light"

    x: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    y: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    light_type: Mapped[str] = mapped_column(
        String(16), nullable=False, default=LightType.STANDARD.value
    )
    radius: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    condition: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    district_id: Mapped[int | None] = mapped_column(
        ForeignKey("district.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    applied_at_total_seconds: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    __table_args__ = (UniqueConstraint("x", "y", name="uq_street_light_cell"),)

    def __repr__(self) -> str:
        return (
            f"StreetLight(id={self.id}, ({self.x},{self.y}), "
            f"type={self.light_type}, active={self.is_active})"
        )


__all__ = ["RoadTile", "StreetLight"]
