"""MarketService — acquisto e vendita nei negozi."""

from __future__ import annotations

from dataclasses import dataclass

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.core.anthalys_datetime import AnthalysDateTime
from simai.economy.enums import SHOP_RESALE_MARGIN
from simai.economy.ledger import JournalEntryKind
from simai.economy.models import ShopItem
from simai.npc.economy.service import EconomyError, WealthService
from simai.npc.models import Character
from simai.world.models import GameObject, Location


@dataclass(frozen=True, slots=True)
class PurchaseResult:
    """Esito di un acquisto.

    - `price_paid`: totale effettivamente pagato (item + tax)
    - `item_price`: prezzo base dell'item (al netto della tassa)
    - `tax_paid`: quota versata alla città
    """

    success: bool
    reason: str
    object_id: int | None
    price_paid: int
    item_price: int = 0
    tax_paid: int = 0


@dataclass(frozen=True, slots=True)
class SaleResult:
    """Esito di una vendita.

    - `price_received`: prezzo finale pagato al venditore.
    - `quality_label`: label qualità dell'oggetto (o "" se non craftato).
    - `base_price`: prezzo base prima del moltiplicatore qualità.
    """

    success: bool
    reason: str
    price_received: int
    quality_label: str = ""
    base_price: int = 0


class MarketService:
    """Servizio stateless di acquisto/vendita."""

    @staticmethod
    def items_in(session: Session, location_id: int) -> list[ShopItem]:
        """Voci di catalogo di un negozio."""
        return list(
            session.scalars(
                select(ShopItem)
                .where(ShopItem.location_id == location_id)
                .order_by(ShopItem.item_type)
            )
        )

    @staticmethod
    def find_item(session: Session, *, location_id: int, item_type: str) -> ShopItem | None:
        return session.scalars(
            select(ShopItem).where(
                ShopItem.location_id == location_id,
                ShopItem.item_type == item_type,
            )
        ).first()

    # ------------------------------------------------------------------
    # Buy
    # ------------------------------------------------------------------

    @staticmethod
    def buy(
        session: Session,
        *,
        buyer: Character,
        shop: Location,
        item_type: str,
        current_dt: AnthalysDateTime,
    ) -> PurchaseResult:
        """Acquista `item_type` da `shop`. Crea un `GameObject` per il buyer.

        Applica la sales tax (5%) al prezzo dell'item. Il totale
        `price + tax` deve essere coperto dal bilancio del buyer.
        """
        if not buyer.is_alive:
            return PurchaseResult(False, "buyer_not_alive", None, 0)

        item = MarketService.find_item(session, location_id=shop.id, item_type=item_type)
        if item is None:
            return PurchaseResult(False, "item_not_found", None, 0)

        if item.stock == 0:
            return PurchaseResult(False, "out_of_stock", None, 0)

        price = int(item.current_price)

        # --- Sales tax (Chunk 4.7c) ---
        from simai.city.tax import TaxService

        tax = TaxService.preview_sales_tax(price)
        total_cost = price + tax

        if int(buyer.athel_balance) < total_cost:
            return PurchaseResult(
                False,
                f"insufficient_funds ({buyer.athel_balance} < {total_cost})",
                None,
                0,
            )

        # 1. Scala soldi (item price) — via ledger
        try:
            WealthService.add(
                session,
                buyer,
                -price,
                current_dt=current_dt,
                kind=JournalEntryKind.PURCHASE,
                description=f"Acquisto {item.item_name} da {shop.name}",
                reference_type="shop",
                reference_id=shop.id,
                metadata={"item_type": item_type, "shop_id": shop.id},
            )
        except EconomyError as exc:
            return PurchaseResult(False, f"wealth_error: {exc}", None, 0)

        # 2. Sales tax -> CityBudget
        tax_result = TaxService.collect_sales_tax(
            session,
            buyer=buyer,
            purchase_amount=price,
            current_dt=current_dt,
        )
        tax_paid = tax_result.amount if tax_result.ok else 0

        # 3. Crea GameObject
        obj = GameObject(
            name=item.item_name,
            type=item.item_type,
            location_id=shop.id,
            owner_character_id=buyer.id,
            state="NEW",
            condition=1.0,
            container_capacity=None,
            container_contents_json=[],
            interactions_json=[],
            metadata_json={"bought_from": shop.id},
        )
        session.add(obj)
        session.flush()

        # 4. Scala stock (se finito)
        if item.stock > 0:
            item.stock -= 1

        logger.info(
            "Acquisto: char={} shop={} item={} price={} tax={}",
            buyer.id,
            shop.id,
            item_type,
            price,
            tax_paid,
        )
        return PurchaseResult(
            success=True,
            reason="ok",
            object_id=obj.id,
            price_paid=total_cost,
            item_price=price,
            tax_paid=tax_paid,
        )

    # ------------------------------------------------------------------
    # Sell
    # ------------------------------------------------------------------

    @staticmethod
    def sell(
        session: Session,
        *,
        seller: Character,
        shop: Location,
        obj: GameObject,
        current_dt: AnthalysDateTime,
    ) -> SaleResult:
        """Vende `obj` al `shop`. Il prezzo è `current_price × (1 - margin)`,
        moltiplicato per il quality multiplier se l'oggetto è craftato.
        """
        if not seller.is_alive:
            return SaleResult(False, "seller_not_alive", 0)
        if obj.owner_character_id is None:
            return SaleResult(False, "object_has_no_owner", 0)
        if obj.owner_character_id != seller.id:
            return SaleResult(
                False,
                f"not_owner (owner is char {obj.owner_character_id})",
                0,
            )

        item = MarketService.find_item(session, location_id=shop.id, item_type=obj.type)
        if item is None:
            return SaleResult(False, "item_not_bought_here", 0)

        # Prezzo base con margine negozio
        base_price = int(item.current_price * (1.0 - SHOP_RESALE_MARGIN))

        # Quality multiplier (Chunk 4.8b)
        from simai.npc.crafting import QUALITY_PRICE_MULTIPLIER, CraftingQuality

        quality_label = ""
        quality_mult = 1.0
        meta = obj.metadata_json or {}
        if meta.get("crafted"):
            label_raw = str(meta.get("quality_label", ""))
            quality_label = label_raw
            try:
                quality_enum = CraftingQuality(label_raw)
                quality_mult = QUALITY_PRICE_MULTIPLIER.get(quality_enum, 1.0)
            except ValueError:
                quality_mult = 1.0

        price = max(1, int(base_price * quality_mult))

        # 1. Ritira oggetto dal seller
        obj.owner_character_id = None
        obj.location_id = shop.id

        # 2. Accredita soldi — via ledger
        WealthService.add(
            session,
            seller,
            price,
            current_dt=current_dt,
            kind=JournalEntryKind.SALE,
            description=f"Vendita {obj.name} a {shop.name}",
            reference_type="shop",
            reference_id=shop.id,
            metadata={
                "object_id": obj.id,
                "quality_label": quality_label,
                "base_price": base_price,
            },
        )

        # 3. Incrementa stock del negozio
        if item.stock >= 0:
            item.stock += 1

        logger.info(
            "Vendita: char={} shop={} obj={} base={} q={} final={}",
            seller.id,
            shop.id,
            obj.id,
            base_price,
            quality_label,
            price,
        )
        return SaleResult(
            success=True,
            reason="ok",
            price_received=price,
            quality_label=quality_label,
            base_price=base_price,
        )


__all__ = ["MarketService", "PurchaseResult", "SaleResult"]
