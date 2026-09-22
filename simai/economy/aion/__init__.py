"""Package `simai.economy.aion` — piattaforma e-commerce AION.

Range migrazione: dentro `6000_XX` (Economy esteso).

Contenuto:
  - `AionPlatform`, `AionWarehouse`, `AionListing`, `AionOrder` — modelli
  - `AionService` — API (bootstrap, listing, ordini con escrow)
  - `AionError`, `OrderResult`, `SettlementResult` — dataclass ed errori
"""

from simai.economy.aion.ai import AionAI, AionAIReport
from simai.economy.aion.enums import (
    AION_ESCROW_CODE,
    AION_PLATFORM_CODE,
    AION_PLATFORM_NAME,
    AION_REVENUE_CODE,
    CARGO_SPEED_CELLS_PER_TICK,
    DEFAULT_COMMISSION_RATE,
    DEFAULT_COMMISSION_RATES,
    GLOBAL_WAREHOUSE_CAPACITY,
    GLOBAL_WAREHOUSE_CODE,
    GLOBAL_WAREHOUSE_DEPTH_METERS,
    SHIPPING_BASE_COST,
    SHIPPING_COST_PER_CELL,
    SHIPPING_DELIVERY_RADIUS_CELLS,
    AionBuyerType,
    AionFulfillmentMode,
    AionInventoryItemStatus,
    AionListingStatus,
    AionOrderStatus,
    AionProductType,
    AionSellerType,
    AionShipmentStatus,
)
from simai.economy.aion.models import (
    AionInventoryItem,
    AionListing,
    AionOrder,
    AionPlatform,
    AionShipment,
    AionWarehouse,
)
from simai.economy.aion.seed import AionSeedResult, seed_demo_aion
from simai.economy.aion.service import (
    AionError,
    AionService,
    OrderResult,
    SettlementResult,
    ShipmentResult,
    ShipmentTickReport,
)

__all__ = [
    "AION_ESCROW_CODE",
    "AION_PLATFORM_CODE",
    "AION_PLATFORM_NAME",
    "AION_REVENUE_CODE",
    "CARGO_SPEED_CELLS_PER_TICK",
    "DEFAULT_COMMISSION_RATE",
    "DEFAULT_COMMISSION_RATES",
    "GLOBAL_WAREHOUSE_CAPACITY",
    "GLOBAL_WAREHOUSE_CODE",
    "GLOBAL_WAREHOUSE_DEPTH_METERS",
    "SHIPPING_BASE_COST",
    "SHIPPING_COST_PER_CELL",
    "SHIPPING_DELIVERY_RADIUS_CELLS",
    "AionAI",
    "AionAIReport",
    "AionBuyerType",
    "AionError",
    "AionFulfillmentMode",
    "AionInventoryItem",
    "AionInventoryItemStatus",
    "AionListing",
    "AionListingStatus",
    "AionOrder",
    "AionOrderStatus",
    "AionPlatform",
    "AionProductType",
    "AionSeedResult",
    "AionSellerType",
    "AionService",
    "AionShipment",
    "AionShipmentStatus",
    "AionWarehouse",
    "OrderResult",
    "SettlementResult",
    "ShipmentResult",
    "ShipmentTickReport",
    "seed_demo_aion",
]
