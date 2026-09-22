"""AionAI — agenti autonomi che popolano AION con listing e ordini.

Il modulo è puramente applicativo: nessun nuovo modello SQLAlchemy, nessuna
nuova migrazione. Tutto passa per `AionService` (5.4a→5.4d).

Regole principali (tarabili via costanti in testa al file):

- Un NPC pubblica listing `GOODS` dai propri `GameObject` che non sono già
  oggetto di un listing attivo. Il prezzo è derivato da
  `metadata_json["base_price"]` (fallback `DEFAULT_GOODS_BASE_PRICE`),
  scalato in base alla `condition` e maggiorato di un markup casuale in
  `[MARKUP_MIN, MARKUP_MAX]`.
- Un NPC compra il listing attivo più economico che può permettersi,
  escludendo i propri, entro un budget pari a una frazione del saldo.
- Alla fine del tick avanziamo tutte le spedizioni in corso via
  `AionService.tick_shipments`.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Final

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from simai.core.anthalys_datetime import AnthalysDateTime
from simai.economy.aion.enums import (
    AionFulfillmentMode,
    AionListingStatus,
    AionProductType,
    AionSellerType,
)
from simai.economy.aion.models import AionListing
from simai.economy.aion.service import AionError, AionService
from simai.npc.models import Character
from simai.world.models import GameObject

# ---------------------------------------------------------------------------
# Policy (tarabili)
# ---------------------------------------------------------------------------

MAX_ACTIVE_LISTINGS_PER_SELLER: Final[int] = 4
"""Oltre questo numero di listing attivi, l'NPC smette di pubblicarne."""

MAX_ITEMS_TO_LIST_PER_TICK: Final[int] = 3
"""Numero massimo di nuovi listing per NPC per singolo tick."""

MAX_PURCHASES_PER_TICK: Final[int] = 3
"""Numero massimo di ordini che un NPC piazza per singolo tick."""

MIN_ATHEL_RESERVE_BEFORE_BUY: Final[int] = 200
"""Sotto questo saldo l'NPC non compra nulla."""

MAX_FRACTION_OF_BALANCE_FOR_PURCHASE: Final[float] = 0.25
"""Budget massimo di spesa in un singolo tick (frazione del saldo)."""

MARKUP_MIN: Final[float] = 1.15
MARKUP_MAX: Final[float] = 1.75

DEFAULT_GOODS_BASE_PRICE: Final[int] = 25
"""Prezzo base di fallback se `metadata_json["base_price"]` è assente."""

MIN_CONDITION_TO_SELL: Final[float] = 0.25
"""Sotto questa `condition` l'NPC non mette in vendita il GameObject."""

DEFAULT_LISTING_QUANTITY: Final[int] = 1
"""Un GameObject = un listing (quantity=1)."""

MAX_DAILY_SELLERS: Final[int] = 20
MAX_DAILY_BUYERS: Final[int] = 30

CANDIDATES_POOL_SIZE: Final[int] = 15
"""Quanti listing caricare per la scelta del compratore."""

TOP_CHEAPEST_LISTINGS: Final[int] = 3
"""Fra i N più economici, scegli a caso."""


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class AionAIReport:
    """Esito di un singolo `AionAI.daily_tick`."""

    sellers_evaluated: int = 0
    buyers_evaluated: int = 0
    listings_created: int = 0
    listings_by_product: dict[str, int] = field(default_factory=dict)
    orders_placed: int = 0
    orders_failed: int = 0
    shipments_advanced: int = 0
    shipments_delivered: int = 0
    errors: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# AI
# ---------------------------------------------------------------------------


class AionAI:
    """Coordina la partecipazione autonoma degli NPC al marketplace AION."""

    @staticmethod
    def daily_tick(
        session: Session,
        *,
        current_dt: AnthalysDateTime,
        rng: random.Random,
        max_sellers: int = MAX_DAILY_SELLERS,
        max_buyers: int = MAX_DAILY_BUYERS,
    ) -> AionAIReport:
        """Esegue un tick completo di attività AION autonoma.

        Sequenza:
        1. `ensure_platform` (idempotente).
        2. Per un campione di NPC "venditori": pubblica listing GOODS dai
           propri GameObject non già in vendita.
        3. Per un campione di NPC "compratori": piazza ordini sui listing
           più economici.
        4. Avanza tutte le spedizioni pendenti.
        """
        report = AionAIReport()

        AionService.ensure_platform(session)

        sellers = AionAI._pick_sellers(session, rng, max_sellers)
        report.sellers_evaluated = len(sellers)
        for character in sellers:
            try:
                created, by_type = AionAI._publish_listings(
                    session,
                    character=character,
                    current_dt=current_dt,
                    rng=rng,
                )
            except AionError as exc:
                msg = f"publish_listings char={character.id}: {exc}"
                logger.warning("AionAI: {}", msg)
                report.errors.append(msg)
                continue
            report.listings_created += created
            for ptype, n in by_type.items():
                report.listings_by_product[ptype] = report.listings_by_product.get(ptype, 0) + n

        buyers = AionAI._pick_buyers(session, rng, max_buyers)
        report.buyers_evaluated = len(buyers)
        for character in buyers:
            try:
                placed, failed = AionAI._browse_and_buy(
                    session,
                    character=character,
                    current_dt=current_dt,
                    rng=rng,
                )
            except AionError as exc:
                msg = f"browse_and_buy char={character.id}: {exc}"
                logger.warning("AionAI: {}", msg)
                report.errors.append(msg)
                continue
            report.orders_placed += placed
            report.orders_failed += failed

        try:
            AionAI._advance_shipments(session, report, current_dt=current_dt)
        except AionError as exc:
            msg = f"tick_shipments: {exc}"
            logger.warning("AionAI: {}", msg)
            report.errors.append(msg)

        logger.info(
            "AionAI.daily_tick: sellers={} buyers={} listings={} orders={} "
            "ship_adv={} ship_del={} errors={}",
            report.sellers_evaluated,
            report.buyers_evaluated,
            report.listings_created,
            report.orders_placed,
            report.shipments_advanced,
            report.shipments_delivered,
            len(report.errors),
        )
        return report

    # ------------------------------------------------------------------
    # Selezione NPC
    # ------------------------------------------------------------------

    @staticmethod
    def _pick_sellers(
        session: Session,
        rng: random.Random,
        limit: int,
    ) -> list[Character]:
        """NPC vivi che possiedono almeno un GameObject, mescolati via `rng`."""
        if limit <= 0:
            return []
        has_objects_sub = (
            select(GameObject.owner_character_id)
            .where(GameObject.owner_character_id.is_not(None))
            .distinct()
            .subquery()
        )
        stmt = (
            select(Character)
            .where(
                Character.is_alive.is_(True),
                Character.id.in_(select(has_objects_sub.c.owner_character_id)),
            )
            .order_by(Character.id)
        )
        characters = list(session.scalars(stmt).all())
        if not characters:
            return []
        rng.shuffle(characters)
        return characters[:limit]

    @staticmethod
    def _pick_buyers(
        session: Session,
        rng: random.Random,
        limit: int,
    ) -> list[Character]:
        """NPC vivi con saldo sufficiente, mescolati via `rng`."""
        if limit <= 0:
            return []
        stmt = (
            select(Character)
            .where(
                Character.is_alive.is_(True),
                Character.athel_balance >= MIN_ATHEL_RESERVE_BEFORE_BUY,
            )
            .order_by(Character.id)
        )
        characters = list(session.scalars(stmt).all())
        if not characters:
            return []
        rng.shuffle(characters)
        return characters[:limit]

    # ------------------------------------------------------------------
    # Pubblicazione listing
    # ------------------------------------------------------------------

    @staticmethod
    def _publish_listings(
        session: Session,
        *,
        character: Character,
        current_dt: AnthalysDateTime,
        rng: random.Random,
    ) -> tuple[int, dict[str, int]]:
        """Pubblica listing GOODS dai GameObject del personaggio.

        Ritorna `(numero_listing_creati, contatore_per_product_type)`.
        """
        active_count = int(
            session.scalar(
                select(func.count(AionListing.id)).where(
                    AionListing.seller_type == AionSellerType.CHARACTER.value,
                    AionListing.seller_id == character.id,
                    AionListing.status == AionListingStatus.ACTIVE.value,
                )
            )
            or 0
        )
        if active_count >= MAX_ACTIVE_LISTINGS_PER_SELLER:
            return 0, {}

        slots = min(
            MAX_ACTIVE_LISTINGS_PER_SELLER - active_count,
            MAX_ITEMS_TO_LIST_PER_TICK,
        )
        if slots <= 0:
            return 0, {}

        active_listed_sub = (
            select(AionListing.source_object_id)
            .where(
                AionListing.source_object_id.is_not(None),
                AionListing.status == AionListingStatus.ACTIVE.value,
            )
            .subquery()
        )
        obj_stmt = (
            select(GameObject)
            .where(
                GameObject.owner_character_id == character.id,
                GameObject.id.not_in(select(active_listed_sub.c.source_object_id)),
            )
            .order_by(GameObject.id)
        )
        objects = list(session.scalars(obj_stmt).all())
        if not objects:
            return 0, {}

        rng.shuffle(objects)
        objects = objects[:slots]

        created = 0
        by_type: dict[str, int] = {}
        for obj in objects:
            try:
                AionAI._create_listing_from_object(
                    session,
                    character=character,
                    obj=obj,
                    current_dt=current_dt,
                    rng=rng,
                )
            except AionError as exc:
                logger.debug(
                    "AionAI: skip object={} char={}: {}",
                    obj.id,
                    character.id,
                    exc,
                )
                continue
            created += 1
            key = AionProductType.GOODS.value
            by_type[key] = by_type.get(key, 0) + 1
        return created, by_type

    @staticmethod
    def _create_listing_from_object(
        session: Session,
        *,
        character: Character,
        obj: GameObject,
        current_dt: AnthalysDateTime,
        rng: random.Random,
    ) -> AionListing:
        """Deriva un listing GOODS da un `GameObject`."""
        condition = float(obj.condition or 1.0)
        if condition < MIN_CONDITION_TO_SELL:
            raise AionError(f"oggetto troppo usurato (condition={condition:.2f})")

        metadata = dict(obj.metadata_json or {})
        raw_base = metadata.get("base_price", DEFAULT_GOODS_BASE_PRICE)
        base_price: int
        if isinstance(raw_base, int) and not isinstance(raw_base, bool):
            base_price = raw_base
        elif isinstance(raw_base, float):
            base_price = int(raw_base)
        elif isinstance(raw_base, str):
            try:
                base_price = int(raw_base)
            except ValueError:
                base_price = DEFAULT_GOODS_BASE_PRICE
        else:
            base_price = DEFAULT_GOODS_BASE_PRICE
        if base_price <= 0:
            base_price = DEFAULT_GOODS_BASE_PRICE

        # Sconto proporzionale alla condizione (minimo 25% del base)
        adjusted_base = max(1, round(base_price * max(0.25, condition)))

        markup = rng.uniform(MARKUP_MIN, MARKUP_MAX)
        unit_price = max(1, round(adjusted_base * markup))

        item_type = AionAI._object_type_to_str(obj.type)
        item_name = item_type.replace("_", " ").title()

        listing = AionService.create_listing(
            session,
            seller=character,
            item_type=item_type,
            item_name=item_name,
            unit_price=unit_price,
            quantity=DEFAULT_LISTING_QUANTITY,
            product_type=AionProductType.GOODS,
            fulfillment_mode=AionFulfillmentMode.SELLER_DIRECT,
            condition=condition,
            description=f"Venduto da {character.full_name} su AION",
            current_dt=current_dt,
            source_object_id=obj.id,
            metadata={
                "source_object_id": obj.id,
                "base_price": base_price,
                "markup": round(markup, 4),
                "ai_generated": True,
            },
        )
        logger.debug(
            "AionAI: listing creato id={} char={} object={} price={}",
            listing.id,
            character.id,
            obj.id,
            unit_price,
        )
        return listing

    @staticmethod
    def _object_type_to_str(raw: object) -> str:
        """Normalizza un valore di tipo a stringa.

        Accetta `object` per restare robusto se in futuro `GameObject.type`
        diventa nullable o assume un enum. Il chiamante tipico passa
        `obj.type` (oggi `Mapped[str]`, quindi già `str`).
        """
        if raw is None:
            return "object"
        if isinstance(raw, StrEnum):
            return raw.value
        return str(raw)

    # ------------------------------------------------------------------
    # Acquisti
    # ------------------------------------------------------------------

    @staticmethod
    def _browse_and_buy(
        session: Session,
        *,
        character: Character,
        current_dt: AnthalysDateTime,
        rng: random.Random,
    ) -> tuple[int, int]:
        """Cerca listing convenienti e piazza fino a `MAX_PURCHASES_PER_TICK` ordini.

        Ritorna `(ordini_ok, ordini_falliti)`.
        """
        balance = int(character.athel_balance)
        if balance < MIN_ATHEL_RESERVE_BEFORE_BUY:
            return 0, 0

        budget = int(balance * MAX_FRACTION_OF_BALANCE_FOR_PURCHASE)
        if budget < 1:
            return 0, 0

        stmt = (
            select(AionListing)
            .where(
                AionListing.status == AionListingStatus.ACTIVE.value,
                AionListing.unit_price <= budget,
                AionListing.quantity > AionListing.quantity_sold,
            )
            .order_by(AionListing.unit_price.asc(), AionListing.id.asc())
            .limit(CANDIDATES_POOL_SIZE)
        )
        listings = list(session.scalars(stmt).all())
        if not listings:
            return 0, 0

        candidates = [
            listing
            for listing in listings
            if not (
                listing.seller_type == AionSellerType.CHARACTER.value
                and listing.seller_id == character.id
            )
        ]
        if not candidates:
            return 0, 0

        top = candidates[:TOP_CHEAPEST_LISTINGS]
        rng.shuffle(top)
        listing = top[0]

        placed = 0
        failed = 0
        for _ in range(MAX_PURCHASES_PER_TICK):
            remaining = int(listing.remaining_quantity)
            unit_price = int(listing.unit_price)
            if remaining < 1 or unit_price < 1:
                break
            affordable = int(character.athel_balance) // unit_price
            if affordable < 1:
                break
            qty = min(1, affordable, remaining)
            try:
                res = AionService.place_order(
                    session,
                    buyer=character,
                    listing=listing,
                    quantity=qty,
                    current_dt=current_dt,
                    auto_ship=True,
                )
            except AionError as exc:
                logger.debug(
                    "AionAI: place_order error char={} listing={}: {}",
                    character.id,
                    listing.id,
                    exc,
                )
                failed += 1
                break
            if not res.ok:
                logger.debug(
                    "AionAI: order respinta char={} listing={}: {}",
                    character.id,
                    listing.id,
                    res.reason,
                )
                failed += 1
                break
            placed += 1
        return placed, failed

    # ------------------------------------------------------------------
    # Spedizioni
    # ------------------------------------------------------------------

    @staticmethod
    def _advance_shipments(
        session: Session,
        report: AionAIReport,
        *,
        current_dt: AnthalysDateTime,
    ) -> None:
        """Avanza le spedizioni pendenti via `AionService.tick_shipments`."""
        tick_report = AionService.tick_shipments(session, current_dt=current_dt)
        report.shipments_delivered = int(tick_report.deliveries_completed)
        report.shipments_advanced = int(tick_report.deliveries_completed) + int(
            tick_report.shipments_failed
        )


__all__ = [
    "CANDIDATES_POOL_SIZE",
    "DEFAULT_GOODS_BASE_PRICE",
    "DEFAULT_LISTING_QUANTITY",
    "MARKUP_MAX",
    "MARKUP_MIN",
    "MAX_ACTIVE_LISTINGS_PER_SELLER",
    "MAX_DAILY_BUYERS",
    "MAX_DAILY_SELLERS",
    "MAX_FRACTION_OF_BALANCE_FOR_PURCHASE",
    "MAX_ITEMS_TO_LIST_PER_TICK",
    "MAX_PURCHASES_PER_TICK",
    "MIN_ATHEL_RESERVE_BEFORE_BUY",
    "MIN_CONDITION_TO_SELL",
    "TOP_CHEAPEST_LISTINGS",
    "AionAI",
    "AionAIReport",
]
