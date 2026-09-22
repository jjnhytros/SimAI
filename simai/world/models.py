"""Modelli SQLAlchemy di World: Location, LocationEdge, GameObject."""

from __future__ import annotations

from typing import Any

from sqlalchemy import (
    Boolean,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from simai.db.base import Base, IdMixin, TimestampMixin
from simai.world.enums import EdgeKind, GameObjectState, LocationType


class Location(IdMixin, TimestampMixin, Base):
    """Una location del mondo (stanza, edificio, lotto, distretto)."""

    __tablename__ = "location"

    name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    type: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=str(LocationType.ROOM),
        index=True,
    )
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("location.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    lot_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)

    # Griglia 2D (bounds)
    bounds_x: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    bounds_y: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    bounds_w: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    bounds_h: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Attributi statici
    capacity: Mapped[int] = mapped_column(Integer, default=10, nullable=False)

    # Attributi dinamici (0.0 - 1.0 salvo crowd_level)
    cleanliness_level: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    noise_level: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    crowd_level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    safety_rating: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    aesthetic_score: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)

    attributes_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    parent: Mapped[Location | None] = relationship(
        "Location",
        remote_side="Location.id",
        back_populates="children",
    )
    children: Mapped[list[Location]] = relationship(
        "Location",
        back_populates="parent",
        cascade="all",
        passive_deletes=True,
    )
    objects: Mapped[list[GameObject]] = relationship(
        "GameObject",
        back_populates="location",
        cascade="save-update",
        passive_deletes=True,
    )

    def center(self) -> tuple[float, float]:
        """Centro geometrico dei bounds (per euristica A*)."""
        return (
            self.bounds_x + self.bounds_w / 2.0,
            self.bounds_y + self.bounds_h / 2.0,
        )

    def __repr__(self) -> str:
        return f"Location(id={self.id}, name={self.name!r}, type={self.type})"


class LocationEdge(IdMixin, Base):
    """Arco del grafo di navigazione tra due Location."""

    __tablename__ = "location_edge"

    from_location_id: Mapped[int] = mapped_column(
        ForeignKey("location.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    to_location_id: Mapped[int] = mapped_column(
        ForeignKey("location.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    kind: Mapped[str] = mapped_column(String(16), nullable=False, default=str(EdgeKind.DOOR))
    distance: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    bidirectional: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_accessible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "from_location_id",
            "to_location_id",
            name="uq_location_edge_pair",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"LocationEdge({self.from_location_id} -> {self.to_location_id}, "
            f"kind={self.kind}, d={self.distance})"
        )


class GameObject(IdMixin, TimestampMixin, Base):
    """Oggetto di gioco (mobile, elettrodomestico, contenitore, ...)."""

    __tablename__ = "game_object"

    name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    location_id: Mapped[int | None] = mapped_column(
        ForeignKey("location.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    owner_character_id: Mapped[int | None] = mapped_column(
        ForeignKey("character.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # --- Buy mode (Chunk 4.4) ---
    catalog_type_id: Mapped[int | None] = mapped_column(
        ForeignKey("object_catalog.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    lot_id: Mapped[int | None] = mapped_column(
        ForeignKey("lot.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    position_x: Mapped[int | None] = mapped_column(Integer, nullable=True)
    position_y: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rotation: Mapped[int] = mapped_column(Integer, default=0, nullable=False, server_default="0")

    state: Mapped[str] = mapped_column(String(16), nullable=False, default=str(GameObjectState.NEW))
    condition: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)

    # Container
    container_capacity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    container_contents_json: Mapped[list[int]] = mapped_column(JSON, default=list, nullable=False)

    # Interazioni e metadati
    interactions_json: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    location: Mapped[Location | None] = relationship(
        "Location",
        back_populates="objects",
    )

    def __repr__(self) -> str:
        return (
            f"GameObject(id={self.id}, name={self.name!r}, type={self.type}, "
            f"state={self.state}, cond={self.condition:.2f})"
        )
