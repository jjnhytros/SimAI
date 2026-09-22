"""Modelli SQLAlchemy del dominio AION."""

from __future__ import annotations

from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from simai.db.base import Base, IdMixin, TimestampMixin
from simai.economy.aion.enums import (
    AionBuyerType,
    AionFulfillmentMode,
    AionInventoryItemStatus,
    AionListingStatus,
    AionOrderStatus,
    AionProductType,
    AionShipmentStatus,
)


class AionPlatform(IdMixin, TimestampMixin, Base):
    """Configurazione della piattaforma AION (singleton)."""

    __tablename__ = "aion_platform"

    code: Mapped[str] = mapped_column(String(32), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="1", index=True
    )
    default_commission_rate: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.05, server_default="0.05"
    )
    default_fulfillment_mode: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=AionFulfillmentMode.SELLER_DIRECT.value,
        server_default="SELLER_DIRECT",
    )
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    def __repr__(self) -> str:
        return f"AionPlatform(code={self.code!r}, active={self.is_active})"


class AionWarehouse(IdMixin, TimestampMixin, Base):
    """Un magazzino AION.

    Il magazzino globale è sotterraneo (`depth_meters < 0`).
    `underground_x` / `underground_y` sono coordinate nella griglia
    sotterranea, indipendenti dalla griglia superficiale.
    `access_location_id` (opzionale) punta all'accesso in superficie.
    """

    __tablename__ = "aion_warehouse"

    code: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    warehouse_kind: Mapped[str] = mapped_column(
        String(16), nullable=False, default="GLOBAL", index=True
    )
    depth_meters: Mapped[int] = mapped_column(
        Integer, nullable=False, default=-200, server_default="-200"
    )
    underground_x: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    underground_y: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    access_location_id: Mapped[int | None] = mapped_column(
        ForeignKey("location.id", ondelete="SET NULL"), nullable=True, index=True
    )
    capacity: Mapped[int] = mapped_column(
        Integer, nullable=False, default=100_000, server_default="100000"
    )
    used_capacity: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="1", index=True
    )
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    def __repr__(self) -> str:
        return (
            f"AionWarehouse(code={self.code!r}, depth={self.depth_meters}m, "
            f"used={self.used_capacity}/{self.capacity})"
        )


class AionListing(IdMixin, TimestampMixin, Base):
    """Un'inserzione di vendita su AION."""

    __tablename__ = "aion_listing"

    seller_type: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    seller_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    product_type: Mapped[str] = mapped_column(
        String(16), nullable=False, default=AionProductType.GOODS.value, index=True
    )
    item_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    item_name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(String(512), nullable=False, default="")

    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    quantity_sold: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    unit_price: Mapped[int] = mapped_column(Integer, nullable=False)

    condition: Mapped[float] = mapped_column(
        Float, nullable=False, default=1.0, server_default="1.0"
    )
    quality_label: Mapped[str | None] = mapped_column(String(32), nullable=True)

    fulfillment_mode: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=AionFulfillmentMode.SELLER_DIRECT.value,
        server_default="SELLER_DIRECT",
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=AionListingStatus.ACTIVE.value,
        server_default="ACTIVE",
        index=True,
    )

    created_at_total_seconds: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    seller_character_id: Mapped[int | None] = mapped_column(
        ForeignKey("character.id", ondelete="SET NULL"), nullable=True, index=True
    )
    seller_company_id: Mapped[int | None] = mapped_column(
        ForeignKey("company.id", ondelete="SET NULL"), nullable=True, index=True
    )
    source_object_id: Mapped[int | None] = mapped_column(
        ForeignKey("game_object.id", ondelete="SET NULL"), nullable=True, index=True
    )
    lot_id: Mapped[int | None] = mapped_column(
        ForeignKey("lot.id", ondelete="SET NULL"), nullable=True, index=True
    )
    vehicle_id: Mapped[int | None] = mapped_column(
        ForeignKey("vehicle.id", ondelete="SET NULL"), nullable=True, index=True
    )
    warehouse_id: Mapped[int | None] = mapped_column(
        ForeignKey("aion_warehouse.id", ondelete="SET NULL"), nullable=True, index=True
    )
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    @property
    def remaining_quantity(self) -> int:
        return max(0, int(self.quantity) - int(self.quantity_sold))

    @property
    def is_sold_out(self) -> bool:
        return self.remaining_quantity <= 0

    def __repr__(self) -> str:
        return (
            f"AionListing(id={self.id}, seller={self.seller_type}:{self.seller_id}, "
            f"item={self.item_type!r}, price={self.unit_price}, "
            f"qty={self.quantity_sold}/{self.quantity}, status={self.status})"
        )


class AionOrder(IdMixin, TimestampMixin, Base):
    """Un ordine di acquisto su AION.

    L'escrow è tracciato tramite `escrow_entry_id` (JournalEntry) e
    `escrowed_amount`. Il rilascio è gestito da `AionService`.
    """

    __tablename__ = "aion_order"

    listing_id: Mapped[int] = mapped_column(
        ForeignKey("aion_listing.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    buyer_type: Mapped[str] = mapped_column(
        String(16), nullable=False, default=AionBuyerType.CHARACTER.value, index=True
    )
    buyer_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    buyer_character_id: Mapped[int | None] = mapped_column(
        ForeignKey("character.id", ondelete="SET NULL"), nullable=True, index=True
    )
    buyer_company_id: Mapped[int | None] = mapped_column(
        ForeignKey("company.id", ondelete="SET NULL"), nullable=True, index=True
    )

    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    unit_price: Mapped[int] = mapped_column(Integer, nullable=False)
    total_price: Mapped[int] = mapped_column(Integer, nullable=False)
    commission: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    net_to_seller: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    escrowed_amount: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    escrow_entry_id: Mapped[int | None] = mapped_column(
        ForeignKey("journal_entry.id", ondelete="SET NULL"), nullable=True, index=True
    )
    settlement_entry_id: Mapped[int | None] = mapped_column(
        ForeignKey("journal_entry.id", ondelete="SET NULL"), nullable=True, index=True
    )

    status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=AionOrderStatus.PENDING.value,
        server_default="PENDING",
        index=True,
    )
    created_at_total_seconds: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    delivered_at_total_seconds: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    def __repr__(self) -> str:
        return (
            f"AionOrder(id={self.id}, buyer={self.buyer_type}:{self.buyer_id}, "
            f"listing={self.listing_id}, qty={self.quantity}, "
            f"total={self.total_price}, status={self.status})"
        )


class AionShipment(IdMixin, TimestampMixin, Base):
    """Una spedizione associata a un ordine AION.

    Per `mode == SELLER_DIRECT` o `AION_WAREHOUSE`, la spedizione è
    fisica o immediata. Per `DROP_SHIP` è astratta (nessun movimento
    di oggetti reali, solo un tempo di consegna simulato).
    """

    __tablename__ = "aion_shipment"

    order_id: Mapped[int] = mapped_column(
        ForeignKey("aion_order.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    mode: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=AionFulfillmentMode.SELLER_DIRECT.value,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=AionShipmentStatus.PENDING.value,
        index=True,
    )

    # Origine
    origin_character_id: Mapped[int | None] = mapped_column(
        ForeignKey("character.id", ondelete="SET NULL"), nullable=True, index=True
    )
    origin_location_id: Mapped[int | None] = mapped_column(
        ForeignKey("location.id", ondelete="SET NULL"), nullable=True, index=True
    )
    origin_warehouse_id: Mapped[int | None] = mapped_column(
        ForeignKey("aion_warehouse.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Destinazione
    destination_character_id: Mapped[int | None] = mapped_column(
        ForeignKey("character.id", ondelete="SET NULL"), nullable=True, index=True
    )
    destination_location_id: Mapped[int | None] = mapped_column(
        ForeignKey("location.id", ondelete="SET NULL"), nullable=True, index=True
    )

    distance_cells: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0, server_default="0.0"
    )
    duration_ticks: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    shipping_cost: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )

    started_at_total_seconds: Mapped[int] = mapped_column(BigInteger, nullable=False)
    arrives_at_total_seconds: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    delivered_at_total_seconds: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    def __repr__(self) -> str:
        return (
            f"AionShipment(id={self.id}, order={self.order_id}, mode={self.mode}, "
            f"status={self.status}, distance={self.distance_cells:.1f})"
        )


class AionInventoryItem(IdMixin, TimestampMixin, Base):
    """Un item stoccato in un magazzino AION."""

    __tablename__ = "aion_inventory_item"

    warehouse_id: Mapped[int] = mapped_column(
        ForeignKey("aion_warehouse.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    listing_id: Mapped[int | None] = mapped_column(
        ForeignKey("aion_listing.id", ondelete="SET NULL"), nullable=True, index=True
    )
    object_id: Mapped[int | None] = mapped_column(
        ForeignKey("game_object.id", ondelete="SET NULL"), nullable=True, index=True
    )
    item_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    item_name: Mapped[str] = mapped_column(String(128), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    condition: Mapped[float] = mapped_column(
        Float, nullable=False, default=1.0, server_default="1.0"
    )
    quality_label: Mapped[str | None] = mapped_column(String(32), nullable=True)
    status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=AionInventoryItemStatus.STORED.value,
        server_default="STORED",
        index=True,
    )
    reserved_for_order_id: Mapped[int | None] = mapped_column(
        ForeignKey("aion_order.id", ondelete="SET NULL"), nullable=True, index=True
    )
    stored_at_total_seconds: Mapped[int] = mapped_column(BigInteger, nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    def __repr__(self) -> str:
        return (
            f"AionInventoryItem(id={self.id}, wh={self.warehouse_id}, "
            f"item={self.item_type!r} x{self.quantity}, status={self.status})"
        )


__all__ = [
    "AionInventoryItem",
    "AionListing",
    "AionOrder",
    "AionPlatform",
    "AionShipment",
    "AionWarehouse",
]
