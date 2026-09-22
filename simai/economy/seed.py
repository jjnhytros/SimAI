"""Seed demo per l'economia: assegnazione lavori."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.core.anthalys_datetime import AnthalysDateTime
from simai.economy.enums import JobType
from simai.economy.jobs import JobError, JobService
from simai.npc.lifestage_service import LifeStageService
from simai.npc.models import Character
from simai.npc.skills.enums import SkillType
from simai.world.enums import LocationType
from simai.world.models import Location


@dataclass(frozen=True, slots=True)
class EconomySeedResult:
    """Esito del seed economico."""

    jobs_assigned: int
    shops_found: int


def seed_demo_economy(
    session: Session,
    *,
    current_dt: AnthalysDateTime,
    max_jobs: int = 3,
) -> EconomySeedResult:
    """Assegna lavori demo a NPC adulti. Idempotente.

    Salta i character con un job attivo. Assegna a max `max_jobs` NPC
    adulti (>18 anni) senza lavoro.
    """
    # Trova i negozi (per workplace)
    shops = list(session.scalars(select(Location).where(Location.type == LocationType.SHOP.value)))
    shops_found = len(shops)
    if not shops:
        return EconomySeedResult(0, 0)

    # Trova candidati: vivi, >18 anni, senza lavoro attivo
    all_alive = list(session.scalars(select(Character).where(Character.is_alive.is_(True))))
    candidates: list[Character] = []
    for c in all_alive:
        if JobService.job_of(session, c.id) is not None:
            continue
        age_secs = LifeStageService.age_seconds_at(c.birth_total_seconds, current_dt)
        age_years = age_secs // (432 * 28 * 3600)
        if age_years >= 18:
            candidates.append(c)
    candidates.sort(key=lambda c: c.id)

    jobs_map: list[tuple[JobType, str, Location | None, SkillType, str]] = [
        (
            JobType.CRAFTSMAN,
            "Fabbro",
            shops[0] if shops else None,
            SkillType.CRAFTING,
            "Maestro Fabbro",
        ),
        (
            JobType.MERCHANT,
            "Mercante",
            shops[1] if len(shops) > 1 else None,
            SkillType.TRADING,
            "Mercante Esperto",
        ),
        (
            JobType.SERVANT,
            "Domestico",
            shops[2] if len(shops) > 2 else None,
            SkillType.SERVICE,
            "Maggiordomo",
        ),
    ]

    assigned = 0
    for i, candidate in enumerate(candidates[:max_jobs]):
        job_type, title, shop, req_skill, promoted = jobs_map[i % len(jobs_map)]
        try:
            JobService.assign(
                session,
                character=candidate,
                job_type=job_type,
                title=title,
                workplace=shop,
                current_dt=current_dt,
                required_skill_type=req_skill,
                min_skill_level=0,
                wage_skill_scale=0.05,
                promotion_skill_level=10,
                promoted_title=promoted,
            )
            assigned += 1
        except JobError:
            continue

    return EconomySeedResult(jobs_assigned=assigned, shops_found=shops_found)


__all__ = ["EconomySeedResult", "seed_demo_economy"]
