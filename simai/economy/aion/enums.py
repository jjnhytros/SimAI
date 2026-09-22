"""Enum e costanti del dominio AION (Artificial Intelligence Online Network).

AION è la piattaforma e-commerce multivendor in-world di Anthalys.
Owner: Governo di Anthalys (FASE 6). Gestita da AI.

Convenzioni:
  - `AionSellerType`: chi pubblica un listing.
  - `AionProductType`: cosa si vende.
  - `AionFulfillmentMode`: come viene consegnato.
  - `AionListingStatus` / `AionOrderStatus`: macchine a stati.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Final


class AionSellerType(StrEnum):
    """Tipo di venditore su AION."""

    CHARACTER = "CHARACTER"  # NPC o Player
    COMPANY = "COMPANY"  # Azienda NPC
    GOVERNMENT = "GOVERNMENT"  # Governo di Anthalys (FASE 6)
    SYSTEM = "SYSTEM"  # AION stessa (es. liquidazioni)


class AionBuyerType(StrEnum):
    """Tipo di compratore su AION."""

    CHARACTER = "CHARACTER"
    COMPANY = "COMPANY"
    GOVERNMENT = "GOVERNMENT"


class AionProductType(StrEnum):
    """Cosa si vende su AION.

    In 5.4a è supportato solo `GOODS`. Gli altri valori sono dichiarati
    per estensioni future (5.4d).
    """

    GOODS = "GOODS"  # GameObject fisico (nuovo o usato)
    SERVICE = "SERVICE"  # servizio erogato
    LOT = "LOT"  # lotto immobiliare
    VEHICLE = "VEHICLE"  # veicolo
    STOCK = "STOCK"  # azioni / quote (5.5)


class AionFulfillmentMode(StrEnum):
    """Modalità di consegna.

    In 5.4a è supportato solo `SELLER_DIRECT`. Le altre modalità
    arrivano con 5.4b (spedizioni).
    """

    SELLER_DIRECT = "SELLER_DIRECT"  # merce dal venditore al compratore
    AION_WAREHOUSE = "AION_WAREHOUSE"  # merce stoccata in magazzino AION
    DROP_SHIP = "DROP_SHIP"  # merce astratta, no movimento fisico


class AionListingStatus(StrEnum):
    """Stato di un listing."""

    ACTIVE = "ACTIVE"
    SOLD_OUT = "SOLD_OUT"  # quantity == 0
    CANCELLED = "CANCELLED"  # cancellato dal venditore
    ARCHIVED = "ARCHIVED"  # storico


class AionOrderStatus(StrEnum):
    """Stato di un ordine.

    Flusso:
      PENDING → ESCROWED → SHIPPED → DELIVERED
      PENDING → ESCROWED → CANCELLED → REFUNDED
    """

    PENDING = "PENDING"  # creato, escrow non ancora confermato
    ESCROWED = "ESCROWED"  # fondi bloccati, in attesa di spedizione
    SHIPPED = "SHIPPED"  # merce in viaggio (5.4b)
    DELIVERED = "DELIVERED"  # consegnata, escrow rilasciato
    CANCELLED = "CANCELLED"  # cancellato
    REFUNDED = "REFUNDED"  # rimborsato (escrow → buyer)


# ---------------------------------------------------------------------------
# Costanti
# ---------------------------------------------------------------------------

#: Codice della piattaforma AION (singleton).
AION_PLATFORM_CODE: Final[str] = "aion"

#: Nome visualizzato.
AION_PLATFORM_NAME: Final[str] = "AION"

#: Commissione di default se non configurata per (seller_type, product_type).
DEFAULT_COMMISSION_RATE: Final[float] = 0.05  # 5%

#: Mappa di default delle commissioni per (seller_type, product_type).
#: Override possibile via `AionPlatform.metadata_json["commission_rates"]`.
DEFAULT_COMMISSION_RATES: Final[dict[str, dict[str, float]]] = {
    AionSellerType.CHARACTER.value: {
        AionProductType.GOODS.value: 0.07,  # 7% per privati
        AionProductType.SERVICE.value: 0.10,
        AionProductType.LOT.value: 0.03,
        AionProductType.VEHICLE.value: 0.05,
        AionProductType.STOCK.value: 0.02,
    },
    AionSellerType.COMPANY.value: {
        AionProductType.GOODS.value: 0.05,
        AionProductType.SERVICE.value: 0.07,
        AionProductType.LOT.value: 0.02,
        AionProductType.VEHICLE.value: 0.04,
        AionProductType.STOCK.value: 0.015,
    },
    AionSellerType.GOVERNMENT.value: {
        AionProductType.GOODS.value: 0.02,
        AionProductType.SERVICE.value: 0.02,
        AionProductType.LOT.value: 0.01,
        AionProductType.VEHICLE.value: 0.02,
        AionProductType.STOCK.value: 0.01,
    },
    AionSellerType.SYSTEM.value: {
        AionProductType.GOODS.value: 0.0,
        AionProductType.SERVICE.value: 0.0,
        AionProductType.LOT.value: 0.0,
        AionProductType.VEHICLE.value: 0.0,
        AionProductType.STOCK.value: 0.0,
    },
}

#: Profondità del magazzino globale sotto la città (metri).
GLOBAL_WAREHOUSE_DEPTH_METERS: Final[int] = -200

#: Codice del magazzino globale (singleton).
GLOBAL_WAREHOUSE_CODE: Final[str] = "aion:warehouse:global"

#: Capacità di default del magazzino globale (unità).
GLOBAL_WAREHOUSE_CAPACITY: Final[int] = 100_000


# ---------------------------------------------------------------------------
# Codici dei conti ledger AION
# ---------------------------------------------------------------------------

#: Conto REVENUE delle commissioni AION.
AION_REVENUE_CODE: Final[str] = "aion:revenue"

#: Conto LIABILITY dell'escrow (fondi bloccati per ordini pending).
AION_ESCROW_CODE: Final[str] = "aion:escrow"


class AionShipmentStatus(StrEnum):
    """Stato di una spedizione."""

    PENDING = "PENDING"  # creata, in attesa di partenza
    IN_TRANSIT = "IN_TRANSIT"  # in viaggio
    DELIVERED = "DELIVERED"  # consegnata
    FAILED = "FAILED"  # errore
    CANCELLED = "CANCELLED"  # annullata


class AionInventoryItemStatus(StrEnum):
    """Stato di un item nel magazzino AION."""

    STORED = "STORED"  # disponibile
    RESERVED = "RESERVED"  # riservato a un ordine in uscita
    SHIPPED = "SHIPPED"  # spedito
    RETURNED = "RETURNED"  # restituito al mittente


#: Distanza (in celle) sotto cui la consegna è immediata (nessuna spedizione).
SHIPPING_DELIVERY_RADIUS_CELLS: Final[float] = 3.0

#: Velocità cargo di default in celle/tick (auto). Usata per la durata.
CARGO_SPEED_CELLS_PER_TICK: Final[float] = 5.0

#: Costo base spedizione (Athel). In 5.4b è incluso nel prezzo → 0.
SHIPPING_BASE_COST: Final[int] = 0

#: Costo per cella di distanza (Athel). In 5.4b è incluso nel prezzo → 0.0.
SHIPPING_COST_PER_CELL: Final[float] = 0.0


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
    "AionBuyerType",
    "AionFulfillmentMode",
    "AionInventoryItemStatus",
    "AionListingStatus",
    "AionOrderStatus",
    "AionProductType",
    "AionSellerType",
    "AionShipmentStatus",
]
