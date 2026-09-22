"""Modello Terrain: TerrainTile."""

from __future__ import annotations

from sqlalchemy import (
    BigInteger,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from simai.db.base import Base, IdMixin, TimestampMixin


class TerrainTile(IdMixin, TimestampMixin, Base):
    """Tipo di suolo + elevazione per una cella del lotto."""

    __tablename__ = "terrain_tile"

    lot_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    x: Mapped[int] = mapped_column(Integer, nullable=False)
    y: Mapped[int] = mapped_column(Integer, nullable=False)
    terrain_type: Mapped[str] = mapped_column(
        String(16), nullable=False, default="GRASS", index=True
    )
    elevation: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    applied_at_total_seconds: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)

    __table_args__ = (UniqueConstraint("lot_id", "x", "y", name="uq_terrain_tile_cell"),)

    def __repr__(self) -> str:
        return (
            f"TerrainTile(lot={self.lot_id}, ({self.x},{self.y}), "
            f"type={self.terrain_type}, elev={self.elevation})"
        )


__all__ = ["TerrainTile"]
