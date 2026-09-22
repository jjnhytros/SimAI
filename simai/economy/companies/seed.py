"""Seed demo per aziende NPC."""

from __future__ import annotations

from dataclasses import dataclass

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.config.anthalys import SECONDS_PER_YEAR
from simai.core.anthalys_datetime import AnthalysDateTime
from simai.economy.companies.enums import (
    CompanyKind,
    EmployeeRole,
)
from simai.economy.companies.models import Company
from simai.economy.companies.service import CompanyError, CompanyService
from simai.economy.jobs import JobService
from simai.npc.lifestage_service import LifeStageService
from simai.npc.models import Character
from simai.world.enums import LocationType
from simai.world.models import Location


@dataclass(frozen=True, slots=True)
class CompanySeedResult:
    """Esito del seed aziende."""

    companies_created: int
    employees_hired: int
    adults_found: int = 0
    reason: str = ""


#: Template di aziende demo.
#: `(kind, name, target_roles)` — ruoli da assumere DOPO l'owner.
_COMPANY_TEMPLATES: list[tuple[CompanyKind, str, list[tuple[EmployeeRole, int]]]] = [
    (
        CompanyKind.WORKSHOP,
        "Fucina del Martello",
        [(EmployeeRole.WORKER, 2), (EmployeeRole.APPRENTICE, 1)],
    ),
    (
        CompanyKind.SHOP,
        "Emporio della Piazza",
        [(EmployeeRole.WORKER, 1), (EmployeeRole.MANAGER, 1)],
    ),
    (
        CompanyKind.TAVERN,
        "Locanda del Cinghiale",
        [(EmployeeRole.WORKER, 2)],
    ),
]


def _pick_adult(
    adults: list[Character],
    used: set[int],
    *,
    prefer_no_job: bool,
    session: Session,
) -> Character | None:
    """Sceglie un adulto non usato. Prima cerca senza job, poi fallback."""
    # Pass 1: prefer senza job attivo
    if prefer_no_job:
        for c in adults:
            if c.id in used:
                continue
            if JobService.job_of(session, c.id) is None:
                return c
    # Pass 2: qualsiasi adulto non usato (con o senza job)
    for c in adults:
        if c.id not in used:
            return c
    return None


def seed_demo_companies(
    session: Session,
    *,
    current_dt: AnthalysDateTime,
) -> CompanySeedResult:
    """Crea aziende demo con owner e dipendenti. Idempotente.

    Regole:
      - Serve almeno 1 adulto vivo.
      - Il seed tenta di creare fino a `len(_COMPANY_TEMPLATES)` aziende,
        fermandosi prima se finiscono gli adulti disponibili.
      - Owner/employee: preferenza per character senza `Job` attivo, ma
        fallback su quelli che ne hanno uno (una persona può benissimo
        avere un lavoro dipendente e gestire una propria azienda).
    """
    existing = session.scalars(select(Company)).first()
    if existing is not None:
        logger.debug("Seed aziende: già presenti, skip")
        return CompanySeedResult(0, 0, reason="already_seeded")

    # Trova tutti i vivi
    chars = list(session.scalars(select(Character).where(Character.is_alive.is_(True))))
    adults: list[Character] = []
    for c in chars:
        age_secs = LifeStageService.age_seconds_at(c.birth_total_seconds, current_dt)
        age_years = age_secs // SECONDS_PER_YEAR
        if age_years >= 18:
            adults.append(c)
    adults.sort(key=lambda c: c.id)

    if not adults:
        logger.warning("Seed aziende: nessun adulto vivo trovato")
        return CompanySeedResult(0, 0, adults_found=0, reason="no_adults")

    # Trova location commerciali
    shops = list(session.scalars(select(Location).where(Location.type == LocationType.SHOP.value)))

    used: set[int] = set()
    created = 0
    hired = 0

    for idx, (kind, name, roles) in enumerate(_COMPANY_TEMPLATES):
        owner = _pick_adult(adults, used, prefer_no_job=True, session=session)
        if owner is None:
            logger.info("Seed aziende: esauriti gli adulti dopo {} aziende", created)
            break
        used.add(owner.id)

        location = shops[idx % len(shops)] if shops else None
        try:
            company = CompanyService.create(
                session,
                owner=owner,
                name=name,
                kind=kind,
                location_id=location.id if location else None,
                current_dt=current_dt,
            )
        except CompanyError as exc:
            logger.warning("Seed azienda {!r} fallita: {}", name, exc)
            used.discard(owner.id)
            continue
        created += 1
        logger.info(
            "Seed azienda {!r} creata (id={}, owner={})",
            name,
            company.id,
            owner.id,
        )

        # Dipendenti: prima senza job, fallback su con job
        for role, count in roles:
            for _ in range(count):
                candidate = _pick_adult(adults, used, prefer_no_job=True, session=session)
                if candidate is None:
                    break
                used.add(candidate.id)
                try:
                    CompanyService.hire(
                        session,
                        company=company,
                        employee=candidate,
                        role=role,
                        current_dt=current_dt,
                    )
                    hired += 1
                except CompanyError as exc:
                    logger.debug(
                        "Hire fallito in seed company={} char={}: {}",
                        company.id,
                        candidate.id,
                        exc,
                    )
                    continue

    logger.info(
        "Seed aziende: {} create, {} dipendenti assunti (pool={})",
        created,
        hired,
        len(adults),
    )
    return CompanySeedResult(
        companies_created=created,
        employees_hired=hired,
        adults_found=len(adults),
        reason="ok" if created > 0 else "no_candidates",
    )


__all__ = ["CompanySeedResult", "seed_demo_companies"]
