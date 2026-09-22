"""SupplierService — fornitori di oggetti da catalogo."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.economy.models import ShopItem
from simai.world.models import Location

#: Pezzi aggiunti per tipo ad ogni ciclo di restock.
RESTOCK_PER_TYPE: Final[int] = 5

#: Tetto massimo di stock per tipo.
MAX_STOCK_PER_TYPE: Final[int] = 30

#: Cap di restock al giorno (per performance).
MAX_RESTOCK_PER_DAY: Final[int] = 500


@dataclass(frozen=True, slots=True)
class SupplierOffer:
    """Offerta di un fornitore."""

    location_id: int
    location_name: str
    current_price: int
    stock: int  # -1 = illimitato


class SupplierService:
    """Gestisce i fornitori (ShopItem mappati su `ObjectCatalog.type_code`)."""

    @staticmethod
    def offers_of(session: Session, type_code: str) -> list[SupplierOffer]:
        """Tutti i fornitori che vendono `type_code`, ordinati per prezzo."""
        rows = list(session.scalars(select(ShopItem).where(ShopItem.item_type == type_code)))
        offers: list[SupplierOffer] = []
        for row in rows:
            loc = session.get(Location, row.location_id)
            if loc is None:
                continue
            offers.append(
                SupplierOffer(
                    location_id=loc.id,
                    location_name=loc.name,
                    current_price=row.current_price,
                    stock=row.stock,
                )
            )
        offers.sort(key=lambda o: o.current_price)
        return offers

    @staticmethod
    def find_supplier(session: Session, type_code: str) -> SupplierOffer | None:
        """Ritorna il fornitore più economico con stock disponibile."""
        for offer in SupplierService.offers_of(session, type_code):
            if offer.stock != 0:
                return offer
        return None

    @staticmethod
    def get_offer(session: Session, *, location_id: int, type_code: str) -> SupplierOffer | None:
        """Offerta specifica da un fornitore."""
        row = session.scalars(
            select(ShopItem).where(
                ShopItem.location_id == location_id,
                ShopItem.item_type == type_code,
            )
        ).first()
        if row is None:
            return None
        loc = session.get(Location, row.location_id)
        if loc is None:
            return None
        return SupplierOffer(
            location_id=loc.id,
            location_name=loc.name,
            current_price=row.current_price,
            stock=row.stock,
        )

    @staticmethod
    def decrement_stock(
        session: Session,
        *,
        location_id: int,
        type_code: str,
    ) -> bool:
        """Scala 1 dallo stock del fornitore. Ritorna True se ok.

        Stock = -1 è illimitato e non viene scalato.
        """
        item = session.scalars(
            select(ShopItem).where(
                ShopItem.location_id == location_id,
                ShopItem.item_type == type_code,
            )
        ).first()
        if item is None:
            return False
        if item.stock == 0:
            return False
        if item.stock > 0:
            item.stock -= 1
        session.flush()
        return True

    @staticmethod
    def restock_all(session: Session) -> int:
        """Rifornimento periodico di tutti i negozi.

        Aggiunge `RESTOCK_PER_TYPE` fino a `MAX_STOCK_PER_TYPE`.
        Ritorna il numero di item riforniti.
        """
        items = list(session.scalars(select(ShopItem)))
        restocked = 0
        for item in items:
            if restocked >= MAX_RESTOCK_PER_DAY:
                break
            if item.stock < 0:
                continue
            if item.stock >= MAX_STOCK_PER_TYPE:
                continue
            item.stock = min(MAX_STOCK_PER_TYPE, item.stock + RESTOCK_PER_TYPE)
            restocked += 1
        session.flush()
        return restocked


__all__ = [
    "MAX_RESTOCK_PER_DAY",
    "MAX_STOCK_PER_TYPE",
    "RESTOCK_PER_TYPE",
    "SupplierOffer",
    "SupplierService",
]
