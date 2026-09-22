"""Modelli trasporti: Vehicle, TransportRoute, RouteStop."""

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
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from simai.city.transport.enums import RouteType, VehicleType
from simai.db.base import Base, IdMixin, TimestampMixin


class Vehicle(IdMixin, TimestampMixin, Base):
    """Veicolo personale (auto o bicicletta) di un Character."""

    __tablename__ = "vehicle"

    owner_id: Mapped[int] = mapped_column(
        ForeignKey("character.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    vehicle_type: Mapped[str] = mapped_column(
        String(8), nullable=False, default=VehicleType.BIKE.value, index=True
    )
    fuel: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)
    condition: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    location_id: Mapped[int | None] = mapped_column(
        ForeignKey("location.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    is_parked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    __table_args__ = (UniqueConstraint("owner_id", "vehicle_type", name="uq_vehicle_owner_type"),)

    def __repr__(self) -> str:
        return (
            f"Vehicle(id={self.id}, type={self.vehicle_type}, "
            f"fuel={self.fuel:.1f}, owner={self.owner_id})"
        )


class TransportRoute(IdMixin, TimestampMixin, Base):
    """Linea di trasporto pubblico (bus o metro)."""

    __tablename__ = "transport_route"

    name: Mapped[str] = mapped_column(String(128), nullable=False)
    route_type: Mapped[str] = mapped_column(
        String(8), nullable=False, default=RouteType.BUS.value, index=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    base_fare: Mapped[int] = mapped_column(Integer, nullable=False, default=2)
    speed_cells_per_tick: Mapped[float] = mapped_column(Float, nullable=False, default=3.0)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    def __repr__(self) -> str:
        return f"TransportRoute(id={self.id}, name={self.name!r}, type={self.route_type})"


class RouteStop(IdMixin, TimestampMixin, Base):
    """Una fermata di una linea (Location + posizione nella sequenza)."""

    __tablename__ = "route_stop"

    route_id: Mapped[int] = mapped_column(
        ForeignKey("transport_route.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    location_id: Mapped[int] = mapped_column(
        ForeignKey("location.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint("route_id", "sequence", name="uq_route_stop_seq"),
        UniqueConstraint("route_id", "location_id", name="uq_route_stop_loc"),
    )

    def __repr__(self) -> str:
        return f"RouteStop(route={self.route_id}, loc={self.location_id}, seq={self.sequence})"


__all__ = ["RouteStop", "TransportRoute", "Vehicle"]
