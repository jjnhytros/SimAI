"""Modelli Buy mode: ObjectCatalog."""

from __future__ import annotations

from typing import Any

from sqlalchemy import (
    Boolean,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from simai.db.base import Base, IdMixin, TimestampMixin
from simai.world.buy.enums import ObjectCategory


class ObjectCatalog(IdMixin, TimestampMixin, Base):
    """Voce del catalogo oggetti acquistabili."""

    __tablename__ = "object_catalog"

    type_code: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    category: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=ObjectCategory.FURNITURE.value,
        index=True,
    )

    base_price: Mapped[int] = mapped_column(Integer, default=50, nullable=False)

    # Footprint su griglia (1x1 default)
    footprint_w: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    footprint_h: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Comportamento
    is_wall_mounted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_container: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    container_capacity: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Icona (Bootstrap Icons class name, es. "bi-lamp")
    icon: Mapped[str] = mapped_column(String(32), default="bi-box", nullable=False)

    interactions_json: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    def effective_footprint(self, rotation: int) -> tuple[int, int]:
        """Footprint effettivo dato `rotation` (0/90/180/270)."""
        if rotation in (90, 270):
            return (self.footprint_h, self.footprint_w)
        return (self.footprint_w, self.footprint_h)

    def __repr__(self) -> str:
        return (
            f"ObjectCatalog(code={self.type_code!r}, name={self.name!r}, price={self.base_price})"
        )


__all__ = ["ObjectCatalog"]
