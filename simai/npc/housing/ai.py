"""RealEstateAI — decide autonomamente se comprare/vendere lotti."""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from loguru import logger
from sqlalchemy.orm import Session

from simai.config.anthalys import SECONDS_PER_YEAR
from simai.core.anthalys_datetime import AnthalysDateTime
from simai.economy.property import (
    LotOwnershipService,
    LotPurchaseService,
    MortgageService,
)
from simai.npc.housing.enums import (
    BROKE_THRESHOLD,
    BUY_HOME_PROBABILITY,
    BUY_SHOP_PROBABILITY,
    MAX_PURCHASES_PER_DAY,
    MIN_AGE_BUY,
    MIN_AGE_BUY_SHOP,
    MIN_DOWN_PAYMENT_RATIO,
    MIN_RESERVE,
    MIN_SKILL_FOR_SHOP,
    PREFERRED_DOWN_PAYMENT_RATIO,
    SELL_PROBABILITY,
    SENIOR_AGE,
    HousingAction,
)
from simai.npc.lifestage_service import LifeStageService
from simai.npc.models import Character
from simai.npc.skills.enums import SkillType
from simai.npc.skills.service import SkillService
from simai.world.enums import LotUsage
from simai.world.lot import Lot


@dataclass(frozen=True, slots=True)
class HousingEvent:
    """Evento immobiliare registrato."""

    character_id: int
    action: HousingAction
    lot_id: int
    reason: str
    cash_paid: int = 0
    mortgage_id: int | None = None


@dataclass(slots=True)
class HousingReport:
    """Esito di un tick di housing AI."""

    events: list[HousingEvent] = field(default_factory=list)
    candidates_evaluated: int = 0


class RealEstateAI:
    """Servizio stateless di decisioni immobiliari per NPC."""

    @staticmethod
    def daily_tick(
        session: Session,
        characters: list[Character],
        *,
        current_dt: AnthalysDateTime,
        rng: random.Random,
    ) -> HousingReport:
        """Valuta ogni character e applica decisioni immobiliari.

        Ordine:
          1. Vendite forzate (per povertà).
          2. Acquisti (case, poi negozi).
        """
        report = HousingReport()
        purchases_budget = MAX_PURCHASES_PER_DAY

        # 1. Vendite (broke)
        for c in characters:
            if not c.is_alive:
                continue
            report.candidates_evaluated += 1
            sold = RealEstateAI._maybe_sell(session, c, current_dt=current_dt, rng=rng)
            if sold is not None:
                report.events.append(sold)

        # 2. Acquisti
        for c in characters:
            if not c.is_alive or purchases_budget <= 0:
                continue

            # Casa
            bought = RealEstateAI._maybe_buy_home(session, c, current_dt=current_dt, rng=rng)
            if bought is not None:
                report.events.append(bought)
                purchases_budget -= 1
                continue

            # Negozio
            if purchases_budget <= 0:
                continue
            bought = RealEstateAI._maybe_buy_shop(session, c, current_dt=current_dt, rng=rng)
            if bought is not None:
                report.events.append(bought)
                purchases_budget -= 1

        return report

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    @staticmethod
    def _age_years(character: Character, current_dt: AnthalysDateTime) -> int:
        age_secs = LifeStageService.age_seconds_at(character.birth_total_seconds, current_dt)
        return int(age_secs // SECONDS_PER_YEAR)

    @staticmethod
    def _owns_residential(session: Session, character_id: int) -> bool:
        for o in LotOwnershipService.owned_by(session, character_id):
            lot = session.get(Lot, o.lot_id)
            if lot is not None and lot.usage == LotUsage.RESIDENTIAL.value:
                return True
        return False

    @staticmethod
    def _owns_commercial(session: Session, character_id: int) -> bool:
        for o in LotOwnershipService.owned_by(session, character_id):
            lot = session.get(Lot, o.lot_id)
            if lot is not None and lot.usage == LotUsage.COMMERCIAL.value:
                return True
        return False

    @staticmethod
    def _has_active_job(session: Session, character_id: int) -> bool:
        from simai.economy.jobs import JobService

        return JobService.job_of(session, character_id) is not None

    @staticmethod
    def _find_vacant_lot(session: Session, usage: LotUsage) -> Lot | None:
        """Ritorna il primo lotto vacante dell'uso dato (ordinato per prezzo)."""
        from sqlalchemy import select as _sel

        return session.scalars(
            _sel(Lot)
            .where(
                Lot.usage == usage.value,
                Lot.is_developed.is_(False),
            )
            .order_by(Lot.base_price.asc())
        ).first()

    @staticmethod
    def _find_first_available(session: Session, usage: LotUsage) -> Lot | None:
        """Ritorna il primo lotto NON posseduto dell'uso dato."""
        from sqlalchemy import select as _sel

        candidates = list(
            session.scalars(
                _sel(Lot).where(Lot.usage == usage.value).order_by(Lot.base_price.asc())
            )
        )
        for lot in candidates:
            if not LotOwnershipService.has_owner(session, lot.id):
                return lot
        return None

    # ------------------------------------------------------------------
    # Buy
    # ------------------------------------------------------------------

    @staticmethod
    def _maybe_buy_home(
        session: Session,
        c: Character,
        *,
        current_dt: AnthalysDateTime,
        rng: random.Random,
    ) -> HousingEvent | None:
        age = RealEstateAI._age_years(c, current_dt)
        if age < MIN_AGE_BUY:
            return None
        if RealEstateAI._owns_residential(session, c.id):
            return None
        if not RealEstateAI._has_active_job(session, c.id):
            return None
        if rng.random() >= BUY_HOME_PROBABILITY:
            return None

        lot = RealEstateAI._find_first_available(session, LotUsage.RESIDENTIAL)
        if lot is None:
            return None

        return RealEstateAI._execute_purchase(session, c, lot, current_dt=current_dt)

    @staticmethod
    def _maybe_buy_shop(
        session: Session,
        c: Character,
        *,
        current_dt: AnthalysDateTime,
        rng: random.Random,
    ) -> HousingEvent | None:
        age = RealEstateAI._age_years(c, current_dt)
        if age < MIN_AGE_BUY_SHOP:
            return None
        if RealEstateAI._owns_commercial(session, c.id):
            return None
        if not RealEstateAI._has_active_job(session, c.id):
            return None

        # Serve skill lavorativa >= soglia
        job = None
        from simai.economy.jobs import JobService

        job = JobService.job_of(session, c.id)
        if job is None or job.required_skill_type is None:
            return None
        try:
            st = SkillType(job.required_skill_type)
        except ValueError:
            return None
        skill = SkillService.get_skill(session, c.id, st)
        if skill is None or skill.level < MIN_SKILL_FOR_SHOP:
            return None

        if rng.random() >= BUY_SHOP_PROBABILITY:
            return None

        lot = RealEstateAI._find_first_available(session, LotUsage.COMMERCIAL)
        if lot is None:
            return None

        return RealEstateAI._execute_purchase(session, c, lot, current_dt=current_dt)

    @staticmethod
    def _execute_purchase(
        session: Session,
        c: Character,
        lot: Lot,
        *,
        current_dt: AnthalysDateTime,
    ) -> HousingEvent | None:
        """Tenta acquisto: prima cash se possibile, altrimenti mutuo."""
        price = int(lot.current_value or lot.base_price)
        if price <= 0:
            return None

        balance = int(c.athel_balance)
        required_reserve = MIN_RESERVE

        # Tentativo 1: cash
        if balance >= price + required_reserve:
            outcome = LotPurchaseService.buy_cash(
                session, buyer=c, lot=lot, current_dt=current_dt, price=price
            )
            if outcome.ok:
                RealEstateAI._move_into_lot(session, c, lot)
                action = (
                    HousingAction.BOUGHT_HOME_CASH
                    if lot.usage == LotUsage.RESIDENTIAL.value
                    else HousingAction.BOUGHT_SHOP_CASH
                )
                logger.info(
                    "Housing AI: char={} bought lot={} cash={}",
                    c.id,
                    lot.id,
                    price,
                )
                return HousingEvent(
                    character_id=c.id,
                    action=action,
                    lot_id=lot.id,
                    reason="cash",
                    cash_paid=price,
                )

        # Tentativo 2: mutuo
        min_down = int(price * MIN_DOWN_PAYMENT_RATIO)
        preferred_down = int(price * PREFERRED_DOWN_PAYMENT_RATIO)
        down = min(preferred_down, balance - required_reserve)
        if down < min_down:
            return None

        outcome = LotPurchaseService.buy_with_mortgage(
            session,
            buyer=c,
            lot=lot,
            current_dt=current_dt,
            down_payment=down,
            price=price,
        )
        if not outcome.ok:
            return None

        RealEstateAI._move_into_lot(session, c, lot)
        action = (
            HousingAction.BOUGHT_HOME_MORTGAGE
            if lot.usage == LotUsage.RESIDENTIAL.value
            else HousingAction.BOUGHT_SHOP_MORTGAGE
        )
        logger.info(
            "Housing AI: char={} bought lot={} via mortgage (down={})",
            c.id,
            lot.id,
            down,
        )
        return HousingEvent(
            character_id=c.id,
            action=action,
            lot_id=lot.id,
            reason=f"mortgage_down_{down}",
            cash_paid=down,
            mortgage_id=outcome.mortgage_id,
        )

    @staticmethod
    def _move_into_lot(session: Session, c: Character, lot: Lot) -> None:
        """Se il lotto ha una location associata, ci sposta il character."""
        if lot.location_id is not None:
            c.location_id = lot.location_id
            session.flush()

    # ------------------------------------------------------------------
    # Sell
    # ------------------------------------------------------------------

    @staticmethod
    def _maybe_sell(
        session: Session,
        c: Character,
        *,
        current_dt: AnthalysDateTime,
        rng: random.Random,
    ) -> HousingEvent | None:
        balance = int(c.athel_balance)
        age = RealEstateAI._age_years(c, current_dt)

        # Vendita solo se: broke o anziano
        is_broke = balance < BROKE_THRESHOLD
        is_senior = age >= SENIOR_AGE

        if not (is_broke or is_senior):
            return None
        if rng.random() >= SELL_PROBABILITY:
            return None

        ownerships = LotOwnershipService.owned_by(session, c.id)
        if not ownerships:
            return None

        # Vendita prioritaria: commerciale se broke, residenziale se senior
        target_lot: Lot | None = None
        for o in ownerships:
            lot = session.get(Lot, o.lot_id)
            if lot is None:
                continue
            if is_broke and lot.usage == LotUsage.COMMERCIAL.value:
                target_lot = lot
                break
            if is_senior and lot.usage == LotUsage.RESIDENTIAL.value:
                target_lot = lot
                break
        if target_lot is None:
            # Fallback: il primo disponibile
            for o in ownerships:
                lot = session.get(Lot, o.lot_id)
                if lot is not None:
                    target_lot = lot
                    break
        if target_lot is None:
            return None

        # Se c'è mutuo attivo, verifica di poterlo saldare
        mortgage = MortgageService.of_lot(session, target_lot.id)
        if mortgage is not None and balance < int(mortgage.remaining_principal):
            logger.warning(
                "Housing AI: char={} vuole vendere lot={} ma mutuo residuo {} > balance {}",
                c.id,
                target_lot.id,
                mortgage.remaining_principal,
                balance,
            )
            return None

        outcome = LotPurchaseService.sell(session, seller=c, lot=target_lot, current_dt=current_dt)
        if not outcome.ok:
            return None

        reason = "broke" if is_broke else "senior"
        logger.info(
            "Housing AI: char={} sold lot={} reason={} gain={}",
            c.id,
            target_lot.id,
            reason,
            outcome.cash_paid,
        )
        return HousingEvent(
            character_id=c.id,
            action=HousingAction.SOLD_LOT,
            lot_id=target_lot.id,
            reason=reason,
            cash_paid=outcome.cash_paid,
        )


__all__ = ["HousingEvent", "HousingReport", "RealEstateAI"]
