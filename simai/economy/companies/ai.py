"""BusinessAI — decisioni autonome per le aziende NPC.

Regole (deterministiche, seed-based):
  1. **Assunzione**: se il saldo > `MIN_RESERVE_FOR_HIRING` e il numero di
     dipendenti è sotto `TARGET_HEADCOUNT[kind]`, tenta di assumere un
     disoccupato vivo (con probabilità `HIRE_PROBABILITY`).
  2. **Licenziamento**: se il saldo < `FIRE_THRESHOLD`, licenzia un WORKER
     non-OWNER (con probabilità `FIRE_PROBABILITY`).
  3. **Dividendo straordinario**: se il saldo supera 3× la soglia di
     dividendo, distribuisce un extra all'owner.
  4. **Scioglimento**: se il saldo è ≤ 0 per 5 giorni consecutivi, dissocia.

Tutte le probabilità sono per giorno aziendale.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Final

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.core.anthalys_datetime import AnthalysDateTime
from simai.economy.companies.enums import (
    DEFAULT_ROLE_WAGE,
    DIVIDEND_THRESHOLD,
    MIN_RESERVE_FOR_HIRING,
    CompanyKind,
    CompanyStatus,
    EmployeeRole,
)
from simai.economy.companies.models import Company, CompanyEmployee
from simai.economy.companies.service import (
    CompanyError,
    CompanyService,
)
from simai.economy.jobs import JobService
from simai.npc.models import Character

#: Headcount target per tipo di azienda (escluso l'owner).
TARGET_HEADCOUNT: Final[dict[CompanyKind, int]] = {
    CompanyKind.SHOP: 3,
    CompanyKind.WORKSHOP: 4,
    CompanyKind.FARM: 3,
    CompanyKind.SERVICE: 2,
    CompanyKind.MANUFACTURE: 5,
    CompanyKind.TAVERN: 4,
}

#: Probabilità giornaliera di assumere (se le condizioni sono soddisfatte).
HIRE_PROBABILITY: Final[float] = 0.15

#: Probabilità giornaliera di licenziare (se sotto soglia).
FIRE_PROBABILITY: Final[float] = 0.20

#: Soglia di saldo sotto cui si considera il licenziamento.
FIRE_THRESHOLD: Final[int] = 200

#: Numero di giorni consecutivi a saldo ≤ 0 prima dello scioglimento.
DAYS_TO_DISSOLVE: Final[int] = 5

#: Giorni di permanenza minima prima di poter licenziare un dipendente.
MIN_EMPLOYMENT_DAYS: Final[int] = 7


@dataclass(slots=True)
class BusinessReport:
    """Esito di un tick di BusinessAI."""

    companies_evaluated: int = 0
    hires: int = 0
    fires: int = 0
    dividends_extra: int = 0
    dissolutions: int = 0
    hire_pairs: list[tuple[int, int]] = field(default_factory=list)  # (company_id, char_id)


class BusinessAI:
    """Decisioni autonome per le aziende."""

    # ------------------------------------------------------------------
    # Tick principale
    # ------------------------------------------------------------------

    @staticmethod
    def daily_tick(
        session: Session,
        companies: list[Company],
        *,
        current_dt: AnthalysDateTime,
        rng: random.Random,
    ) -> BusinessReport:
        """Valuta ogni azienda e applica le decisioni del giorno."""
        report = BusinessReport()
        # Pool di candidati: Character vivi senza job attivo
        candidates = BusinessAI._unemployed_pool(session, companies)

        for company in companies:
            if company.status != CompanyStatus.ACTIVE.value:
                continue
            report.companies_evaluated += 1

            # 1. Licenziamento (priorità per evitare licenziare-e-assumere)
            if BusinessAI._should_consider_fire(company, rng):
                fired = BusinessAI._try_fire(session, company, current_dt=current_dt)
                if fired is not None:
                    report.fires += 1
                    candidates.append(fired)

            # 2. Assunzione
            if BusinessAI._should_consider_hire(session, company, rng):
                hired = BusinessAI._try_hire(
                    session,
                    company,
                    candidates=candidates,
                    current_dt=current_dt,
                )
                if hired is not None:
                    report.hires += 1
                    report.hire_pairs.append((company.id, hired.id))
                    candidates.remove(hired)

            # 3. Dividendo straordinario
            if int(company.athel_balance) > DIVIDEND_THRESHOLD * 3:
                extra = int((company.athel_balance - DIVIDEND_THRESHOLD) * 0.25)
                if extra > 0:
                    try:
                        CompanyService.pay_dividend(
                            session,
                            company=company,
                            amount=extra,
                            current_dt=current_dt,
                        )
                        report.dividends_extra += 1
                    except CompanyError as exc:
                        logger.warning("Extra dividend company={} fallito: {}", company.id, exc)

            # 4. Scioglimento (bilancio disperato persistente)
            if CompanyService.daily_tick.__doc__:  # placeholder silenzioso
                pass
            zero_days = int((company.metadata_json or {}).get("_zero_balance_days", 0))
            if int(company.athel_balance) <= 0:
                zero_days += 1
            else:
                zero_days = 0
            md = dict(company.metadata_json or {})
            md["_zero_balance_days"] = zero_days
            company.metadata_json = md

            if zero_days >= DAYS_TO_DISSOLVE:
                try:
                    CompanyService.dissolve(session, company=company, current_dt=current_dt)
                    report.dissolutions += 1
                except CompanyError as exc:
                    logger.warning("Dissolution company={} fallita: {}", company.id, exc)

        session.flush()
        if report.hires or report.fires or report.dissolutions:
            logger.info(
                "BusinessAI: assunzioni={} licenziamenti={} dissoluzioni={}",
                report.hires,
                report.fires,
                report.dissolutions,
            )
        return report

    # ------------------------------------------------------------------
    # Pool disoccupati
    # ------------------------------------------------------------------

    @staticmethod
    def _unemployed_pool(
        session: Session,
        companies: list[Company],
    ) -> list[Character]:
        """Character vivi, senza job attivo, non già assunti da una delle companies."""
        company_ids = {c.id for c in companies}
        employed_char_ids: set[int] = set()
        if company_ids:
            rows = session.scalars(
                select(CompanyEmployee).where(
                    CompanyEmployee.company_id.in_(company_ids),
                    CompanyEmployee.is_active.is_(True),
                )
            )
            employed_char_ids = {e.character_id for e in rows}

        chars = list(session.scalars(select(Character).where(Character.is_alive.is_(True))))
        pool: list[Character] = []
        for c in chars:
            if c.id in employed_char_ids:
                continue
            if JobService.job_of(session, c.id) is not None:
                continue
            pool.append(c)
        pool.sort(key=lambda c: c.id)
        return pool

    # ------------------------------------------------------------------
    # Hire
    # ------------------------------------------------------------------

    @staticmethod
    def _should_consider_hire(
        session: Session,
        company: Company,
        rng: random.Random,
    ) -> bool:
        if int(company.athel_balance) < MIN_RESERVE_FOR_HIRING:
            return False
        try:
            kind = CompanyKind(company.kind)
        except ValueError:
            return False
        target = TARGET_HEADCOUNT.get(kind, 3)
        current = len(CompanyService.employees_of(session, company.id, only_active=True))
        # Escludi l'owner dal conteggio
        non_owner = 0
        for emp in CompanyService.employees_of(session, company.id, only_active=True):
            if emp.role != EmployeeRole.OWNER.value:
                non_owner += 1
        del current
        if non_owner >= target:
            return False
        return rng.random() < HIRE_PROBABILITY

    @staticmethod
    def _try_hire(
        session: Session,
        company: Company,
        *,
        candidates: list[Character],
        current_dt: AnthalysDateTime,
    ) -> Character | None:
        if not candidates:
            return None
        # Scegli il candidato "migliore" (id più basso, deterministico)
        candidate = candidates[0]
        role = EmployeeRole.WORKER
        wage = DEFAULT_ROLE_WAGE.get(role, 12)
        try:
            CompanyService.hire(
                session,
                company=company,
                employee=candidate,
                role=role,
                daily_wage=wage,
                current_dt=current_dt,
            )
        except CompanyError as exc:
            logger.debug("Hire fallito per {}: {}", candidate.id, exc)
            return None
        logger.info(
            "BusinessAI: company={} ha assunto char={} ({})",
            company.id,
            candidate.id,
            role.value,
        )
        return candidate

    # ------------------------------------------------------------------
    # Fire
    # ------------------------------------------------------------------

    @staticmethod
    def _should_consider_fire(company: Company, rng: random.Random) -> bool:
        if int(company.athel_balance) >= FIRE_THRESHOLD:
            return False
        return rng.random() < FIRE_PROBABILITY

    @staticmethod
    def _try_fire(
        session: Session,
        company: Company,
        *,
        current_dt: AnthalysDateTime,
    ) -> Character | None:
        # Trova un WORKER o APPRENTICE attivo da almeno MIN_EMPLOYMENT_DAYS
        employees = CompanyService.employees_of(session, company.id, only_active=True)
        cutoff = current_dt.to_total_seconds() - MIN_EMPLOYMENT_DAYS * 24 * 28 * 3600
        candidate_emp: CompanyEmployee | None = None
        for emp in employees:
            if emp.role == EmployeeRole.OWNER.value:
                continue
            if emp.hired_at_total_seconds > cutoff:
                continue
            candidate_emp = emp
            break
        if candidate_emp is None:
            return None

        char = session.get(Character, candidate_emp.character_id)
        if char is None:
            return None
        if not CompanyService.fire(session, company=company, employee=char, current_dt=current_dt):
            return None
        logger.info(
            "BusinessAI: company={} ha licenziato char={} (balance={})",
            company.id,
            char.id,
            company.athel_balance,
        )
        return char


__all__ = [
    "DAYS_TO_DISSOLVE",
    "FIRE_PROBABILITY",
    "FIRE_THRESHOLD",
    "HIRE_PROBABILITY",
    "MIN_EMPLOYMENT_DAYS",
    "TARGET_HEADCOUNT",
    "BusinessAI",
    "BusinessReport",
]
