"""CityService — servizi pubblici + bilancio + tick giornaliero."""

from __future__ import annotations

from dataclasses import dataclass

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.city.enums import (
    DEFAULT_COVERAGE_RADIUS,
    DEFAULT_DAILY_COST,
    DEFAULT_QUALITY,
    PublicServiceType,
)
from simai.city.models import CityBudget, PublicService
from simai.core.anthalys_datetime import AnthalysDateTime


class CityError(Exception):
    """Errore di validazione città."""


@dataclass(frozen=True, slots=True)
class ServiceTickReport:
    total_expense: int
    services_paid: int
    services_unpaid: int
    budget_balance: int


class CityService:
    """Servizio stateless di gestione città."""

    # ------------------------------------------------------------------
    # Budget singleton
    # ------------------------------------------------------------------

    @staticmethod
    def get_budget(session: Session) -> CityBudget:
        """Ritorna il CityBudget, creandolo se assente."""
        budget = session.scalars(select(CityBudget)).first()
        if budget is None:
            budget = CityBudget(
                balance=0,
                total_revenue=0,
                total_expenses=0,
                last_revenue_at_total_seconds=0,
                last_expense_at_total_seconds=0,
                metadata_json={},
            )
            session.add(budget)
            session.flush()
        return budget

    @staticmethod
    def add_revenue(
        session: Session,
        *,
        amount: int,
        current_dt: AnthalysDateTime,
    ) -> int:
        """Aggiunge entrate al bilancio. Ritorna il nuovo balance."""
        if amount <= 0:
            return CityService.get_budget(session).balance
        budget = CityService.get_budget(session)
        budget.balance += amount
        budget.total_revenue += amount
        budget.last_revenue_at_total_seconds = current_dt.to_total_seconds()
        session.flush()
        return budget.balance

    @staticmethod
    def add_expense(
        session: Session,
        *,
        amount: int,
        current_dt: AnthalysDateTime,
    ) -> int:
        """Aggiunge uscite. Ritorna il nuovo balance (può andare sotto zero)."""
        if amount <= 0:
            return CityService.get_budget(session).balance
        budget = CityService.get_budget(session)
        budget.balance -= amount
        budget.total_expenses += amount
        budget.last_expense_at_total_seconds = current_dt.to_total_seconds()
        session.flush()
        return budget.balance

    # ------------------------------------------------------------------
    # Public services
    # ------------------------------------------------------------------

    @staticmethod
    def register_service(
        session: Session,
        *,
        district_id: int,
        type_: PublicServiceType,
        location_id: int | None = None,
        quality: float = DEFAULT_QUALITY,
        daily_cost: int | None = None,
        coverage_radius: int = DEFAULT_COVERAGE_RADIUS,
        staff_count: int = 0,
    ) -> PublicService:
        """Registra un servizio pubblico. Idempotente per (district, type)."""
        if not (0.0 <= quality <= 1.0):
            raise CityError(f"quality in [0, 1], ricevuto {quality}")
        if coverage_radius <= 0:
            raise CityError(f"coverage_radius > 0, ricevuto {coverage_radius}")
        cost = daily_cost if daily_cost is not None else DEFAULT_DAILY_COST.get(type_, 10)
        if cost < 0:
            raise CityError(f"daily_cost >= 0, ricevuto {cost}")

        existing = session.scalars(
            select(PublicService).where(
                PublicService.district_id == district_id,
                PublicService.type == type_.value,
            )
        ).first()
        if existing is not None:
            existing.location_id = location_id or existing.location_id
            existing.quality = quality
            existing.daily_cost = cost
            existing.coverage_radius = coverage_radius
            existing.staff_count = staff_count
            existing.is_active = True
            session.flush()
            return existing

        svc = PublicService(
            district_id=district_id,
            type=type_.value,
            location_id=location_id,
            quality=quality,
            daily_cost=cost,
            coverage_radius=coverage_radius,
            staff_count=staff_count,
            is_active=True,
            metadata_json={},
        )
        session.add(svc)
        session.flush()
        logger.info(
            "Public service registrato: district={} type={} q={:.2f} cost={}",
            district_id,
            type_.value,
            quality,
            cost,
        )
        return svc

    @staticmethod
    def all_services(session: Session) -> list[PublicService]:
        return list(
            session.scalars(
                select(PublicService)
                .where(PublicService.is_active.is_(True))
                .order_by(PublicService.district_id, PublicService.type)
            )
        )

    @staticmethod
    def services_of_district(session: Session, district_id: int) -> list[PublicService]:
        return list(
            session.scalars(
                select(PublicService).where(
                    PublicService.district_id == district_id,
                    PublicService.is_active.is_(True),
                )
            )
        )

    # ------------------------------------------------------------------
    # Daily tick: paga i costi dei servizi
    # ------------------------------------------------------------------

    @staticmethod
    def daily_tick(
        session: Session,
        *,
        current_dt: AnthalysDateTime,
    ) -> ServiceTickReport:
        """Paga i costi giornalieri di tutti i servizi attivi.

        Se il bilancio non copre i costi, i servizi non pagati degradano
        la propria `quality` (‑0.02) e vengono loggati come `unpaid`.
        """
        services = CityService.all_services(session)
        budget = CityService.get_budget(session)

        total_expense = 0
        paid = 0
        unpaid = 0

        for svc in services:
            cost = int(svc.daily_cost)
            if budget.balance >= cost:
                budget.balance -= cost
                budget.total_expenses += cost
                total_expense += cost
                paid += 1
            else:
                # Non pagato: degrada quality
                svc.quality = max(0.0, svc.quality - 0.02)
                unpaid += 1

        if total_expense > 0:
            budget.last_expense_at_total_seconds = current_dt.to_total_seconds()
        session.flush()

        if unpaid > 0:
            logger.warning(
                "City budget insufficiente: {} servizi non pagati (balance={})",
                unpaid,
                budget.balance,
            )

        return ServiceTickReport(
            total_expense=total_expense,
            services_paid=paid,
            services_unpaid=unpaid,
            budget_balance=budget.balance,
        )


__all__ = ["CityError", "CityService", "ServiceTickReport"]
