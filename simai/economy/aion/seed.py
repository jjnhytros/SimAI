"""Seed demo per AION — popola il marketplace con listing realistici.

Il seed crea `GameObject` di proprietà di NPC vivi, con `metadata_json["base_price"]`
valorizzato, e poi chiama `AionAI.daily_tick` per far partire listing, ordini e
spedizioni. Idempotente: se esistono già listing attivi, salta.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from simai.config.settings import get_settings
from simai.core.anthalys_datetime import AnthalysDateTime
from simai.economy.aion.ai import AionAI
from simai.economy.aion.enums import AionListingStatus
from simai.economy.aion.models import AionListing
from simai.economy.aion.service import AionService
from simai.npc.models import Character
from simai.world.models import GameObject, Location

# ---------------------------------------------------------------------------
# Policy
# ---------------------------------------------------------------------------

DEFAULT_ITEMS_PER_SELLER: int = 2
"""Quanti GameObject generare per NPC venditore."""

DEFAULT_SELLERS: int = 6
"""Quanti NPC venditori coinvolgere."""

MIN_BALANCE_TO_SELL: int = 200
"""Saldo minimo del venditore per entrare nel seed."""

DEMO_ITEM_TYPES: tuple[tuple[str, str, int], ...] = (
    ("bread", "Pane artigianale", 25),
    ("cheese", "Formaggio stagionato", 40),
    ("cloth", "Rotolo di stoffa", 60),
    ("tool", "Attrezzo da lavoro", 80),
    ("potion", "Pozione curativa", 50),
    ("book", "Libro rilegato", 70),
    ("wine", "Bottiglia di vino", 35),
    ("leather", "Pelle conciata", 45),
)
"""Triple `(item_type, display_name, base_price)`."""


@dataclass(frozen=True, slots=True)
class AionSeedResult:
    """Esito del seed AION."""

    sellers_processed: int
    objects_created: int
    listings_created: int
    orders_placed: int
    shipments_delivered: int
    errors: tuple[str, ...] = field(default_factory=tuple)
    reason: str = "ok"


# ---------------------------------------------------------------------------
# Seed
# ---------------------------------------------------------------------------


def seed_demo_aion(
    session: Session,
    *,
    current_dt: AnthalysDateTime,
    master_seed: int | None = None,
    n_sellers: int = DEFAULT_SELLERS,
    items_per_seller: int = DEFAULT_ITEMS_PER_SELLER,
) -> AionSeedResult:
    """Popola AION con listing demo.

    Sequenza:
      1. `ensure_platform` (idempotente).
      2. Se esistono già listing attivi, ritorna subito `already_seeded`.
      3. Seleziona `n_sellers` NPC vivi con saldo >= `MIN_BALANCE_TO_SELL`.
      4. Per ognuno, crea `items_per_seller` `GameObject` con
         `name`/`type`/`condition`/`metadata_json["base_price"]`.
      5. Chiama `AionAI.daily_tick` per generare listing + ordini + spedizioni.
    """
    if master_seed is None:
        master_seed = get_settings().master_seed
    rng = random.Random(master_seed + 7777)

    AionService.ensure_platform(session)

    # Idempotenza
    existing = int(
        session.scalar(
            select(func.count(AionListing.id)).where(
                AionListing.status == AionListingStatus.ACTIVE.value
            )
        )
        or 0
    )
    if existing > 0:
        logger.debug("Seed AION: {} listing già attivi, skip", existing)
        return AionSeedResult(
            sellers_processed=0,
            objects_created=0,
            listings_created=0,
            orders_placed=0,
            shipments_delivered=0,
            reason="already_seeded",
        )

    # Seleziona venditori
    sellers = list(
        session.scalars(
            select(Character)
            .where(
                Character.is_alive.is_(True),
                Character.athel_balance >= MIN_BALANCE_TO_SELL,
            )
            .order_by(Character.id)
        )
    )
    if not sellers:
        logger.warning("Seed AION: nessun NPC vivo con saldo >= {}", MIN_BALANCE_TO_SELL)
        return AionSeedResult(
            sellers_processed=0,
            objects_created=0,
            listings_created=0,
            orders_placed=0,
            shipments_delivered=0,
            reason="no_sellers",
        )
    rng.shuffle(sellers)
    sellers = sellers[:n_sellers]

    # Fallback location globale
    fallback_loc = session.scalars(select(Location).order_by(Location.id)).first()
    fallback_loc_id = fallback_loc.id if fallback_loc else None

    objects_created = 0
    for seller in sellers:
        loc_id = seller.location_id or fallback_loc_id
        if loc_id is None:
            logger.warning("Seed AION: nessuna location disponibile, skip seller={}", seller.id)
            continue
        for _ in range(items_per_seller):
            item_type, display_name, base_price = rng.choice(DEMO_ITEM_TYPES)
            obj = GameObject(
                name=f"{display_name}",
                type=item_type,
                location_id=loc_id,
                owner_character_id=seller.id,
                state="NEW",
                condition=round(rng.uniform(0.65, 1.0), 3),
                metadata_json={"base_price": base_price, "seed_demo": True},
            )
            session.add(obj)
            objects_created += 1
    session.flush()

    # Attiva AION
    report = AionAI.daily_tick(
        session,
        current_dt=current_dt,
        rng=rng,
    )

    logger.info(
        "Seed AION: sellers={} objects={} listings={} orders={} errors={}",
        len(sellers),
        objects_created,
        report.listings_created,
        report.orders_placed,
        len(report.errors),
    )

    return AionSeedResult(
        sellers_processed=len(sellers),
        objects_created=objects_created,
        listings_created=report.listings_created,
        orders_placed=report.orders_placed,
        shipments_delivered=report.shipments_delivered,
        errors=tuple(report.errors),
        reason="ok" if report.listings_created > 0 else "no_listings",
    )


__all__ = [
    "DEFAULT_ITEMS_PER_SELLER",
    "DEFAULT_SELLERS",
    "DEMO_ITEM_TYPES",
    "MIN_BALANCE_TO_SELL",
    "AionSeedResult",
    "seed_demo_aion",
]
