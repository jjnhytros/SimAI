"""Modelli Style mode: StyleCatalog, FloorTile, WallCovering."""

from __future__ import annotations

from typing import Any

from sqlalchemy import (
    BigInteger,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from simai.db.base import Base, IdMixin, TimestampMixin
from simai.world.style.enums import StyleKind, WallSide


class StyleCatalog(IdMixin, TimestampMixin, Base):
    """Voce del catalogo stili (pavimenti e muri)."""

    __tablename__ = "style_catalog"

    type_code: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    kind: Mapped[str] = mapped_column(
        String(8), nullable=False, default=StyleKind.FLOOR.value, index=True
    )
    color_hex: Mapped[str] = mapped_column(String(9), nullable=False, default="#808080")
    # Prezzo per applicazione (1 cella per FLOOR, 1 segmento per WALL)
    base_price: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    # Pattern "decorativo" (opzionale): stripes, dots, floral, wood, tile
    pattern: Mapped[str] = mapped_column(String(32), nullable=False, default="solid")
    icon: Mapped[str] = mapped_column(String(32), nullable=False, default="bi-palette")
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    def __repr__(self) -> str:
        return (
            f"StyleCatalog(code={self.type_code!r}, kind={self.kind}, "
            f"color={self.color_hex}, price={self.base_price})"
        )


class FloorTile(IdMixin, TimestampMixin, Base):
    """Stile applicato a una cella del lotto."""

    __tablename__ = "floor_tile"

    lot_id: Mapped[int] = mapped_column(
        ForeignKey("lot.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    x: Mapped[int] = mapped_column(Integer, nullable=False)
    y: Mapped[int] = mapped_column(Integer, nullable=False)
    style_id: Mapped[int] = mapped_column(
        ForeignKey("style_catalog.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    applied_at_total_seconds: Mapped[int] = mapped_column(BigInteger, nullable=False)

    __table_args__ = (UniqueConstraint("lot_id", "x", "y", name="uq_floor_tile_cell"),)

    def __repr__(self) -> str:
        return f"FloorTile(lot={self.lot_id}, ({self.x},{self.y}), style={self.style_id})"


class WallCovering(IdMixin, TimestampMixin, Base):
    """Stile applicato a un muro (per lato)."""

    __tablename__ = "wall_covering"

    wall_id: Mapped[int] = mapped_column(
        ForeignKey("wall.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    side: Mapped[str] = mapped_column(String(8), nullable=False, default=WallSide.INTERIOR.value)
    style_id: Mapped[int] = mapped_column(
        ForeignKey("style_catalog.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    applied_at_total_seconds: Mapped[int] = mapped_column(BigInteger, nullable=False)

    __table_args__ = (UniqueConstraint("wall_id", "side", name="uq_wall_covering_side"),)

    def __repr__(self) -> str:
        return f"WallCovering(wall={self.wall_id}, side={self.side}, style={self.style_id})"


__all__ = ["FloorTile", "StyleCatalog", "WallCovering"]
