"""PopulationStatsService — contatori demografici e censimenti."""

from __future__ import annotations

from dataclasses import dataclass, field

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from simai.core.anthalys_datetime import AnthalysDateTime
from simai.npc.enums import LifeStagePediatric, LifeStagePsychosocial, Sex
from simai.npc.models import Character
from simai.npc.stats.models import PopulationCensus


def _month_boundaries(year: int, month: int) -> tuple[int, int]:
    """`(start_total_seconds, next_start_total_seconds)` del mese dato."""
    start = AnthalysDateTime(year, month, 1, 0, 0, 0).to_total_seconds()
    if month == 18:
        next_start = AnthalysDateTime(year + 1, 1, 1, 0, 0, 0).to_total_seconds()
    else:
        next_start = AnthalysDateTime(year, month + 1, 1, 0, 0, 0).to_total_seconds()
    return start, next_start


@dataclass(slots=True)
class LiveStats:
    """Statistiche correnti della popolazione (senza persistenza)."""

    total_alive: int = 0
    total_dead: int = 0
    total_male: int = 0
    total_female: int = 0
    total_intersex: int = 0
    births_current_month: int = 0
    deaths_current_month: int = 0
    pediatric_breakdown: dict[str, int] = field(default_factory=dict)
    psychosocial_breakdown: dict[str, int] = field(default_factory=dict)


class PopulationStatsService:
    """Servizio stateless di statistiche popolazione."""

    @staticmethod
    def live_stats(session: Session, current_dt: AnthalysDateTime) -> LiveStats:
        """Calcola le statistiche correnti (query dirette su `Character`)."""
        stats = LiveStats()

        # Totali per stato
        stats.total_alive = int(
            session.scalar(
                select(func.count()).select_from(Character).where(Character.is_alive.is_(True))
            )
            or 0
        )
        stats.total_dead = int(
            session.scalar(
                select(func.count()).select_from(Character).where(Character.is_alive.is_(False))
            )
            or 0
        )

        # Vivi per sesso
        for sex, attr in (
            (Sex.MALE, "total_male"),
            (Sex.FEMALE, "total_female"),
            (Sex.INTERSEX, "total_intersex"),
        ):
            count = int(
                session.scalar(
                    select(func.count())
                    .select_from(Character)
                    .where(
                        Character.is_alive.is_(True),
                        Character.sex == sex.value,
                    )
                )
                or 0
            )
            setattr(stats, attr, count)

        # Nascite/morti del mese corrente
        start, next_start = _month_boundaries(current_dt.year, current_dt.month)
        stats.births_current_month = int(
            session.scalar(
                select(func.count())
                .select_from(Character)
                .where(
                    Character.birth_total_seconds >= start,
                    Character.birth_total_seconds < next_start,
                )
            )
            or 0
        )
        stats.deaths_current_month = int(
            session.scalar(
                select(func.count())
                .select_from(Character)
                .where(
                    Character.death_total_seconds.is_not(None),
                    Character.death_total_seconds >= start,
                    Character.death_total_seconds < next_start,
                )
            )
            or 0
        )

        # Breakdown per fasce (solo vivi)
        ped_counts = {stage.value: 0 for stage in LifeStagePediatric}
        psy_counts = {stage.value: 0 for stage in LifeStagePsychosocial}
        rows = session.execute(
            select(
                Character.life_stage_pediatric,
                Character.life_stage_psychosocial,
                func.count(),
            )
            .where(Character.is_alive.is_(True))
            .group_by(
                Character.life_stage_pediatric,
                Character.life_stage_psychosocial,
            )
        ).all()
        for ped, psy, count in rows:
            ped_counts[str(ped)] = ped_counts.get(str(ped), 0) + int(count)
            psy_counts[str(psy)] = psy_counts.get(str(psy), 0) + int(count)

        stats.pediatric_breakdown = ped_counts
        stats.psychosocial_breakdown = psy_counts
        return stats

    @staticmethod
    def snapshot(session: Session, current_dt: AnthalysDateTime) -> PopulationCensus:
        """Crea (o aggiorna) il census del mese di `current_dt`.

        Upsert su `(year, month)`.
        """
        live = PopulationStatsService.live_stats(session, current_dt)
        now_secs = current_dt.to_total_seconds()

        existing = session.scalars(
            select(PopulationCensus).where(
                PopulationCensus.year == current_dt.year,
                PopulationCensus.month == current_dt.month,
            )
        ).first()

        if existing is not None:
            existing.total_alive = live.total_alive
            existing.total_male = live.total_male
            existing.total_female = live.total_female
            existing.total_intersex = live.total_intersex
            existing.births_this_month = live.births_current_month
            existing.deaths_this_month = live.deaths_current_month
            existing.pediatric_breakdown_json = live.pediatric_breakdown
            existing.psychosocial_breakdown_json = live.psychosocial_breakdown
            existing.recorded_at_total_seconds = now_secs
            session.flush()
            return existing

        census = PopulationCensus(
            year=current_dt.year,
            month=current_dt.month,
            total_alive=live.total_alive,
            total_male=live.total_male,
            total_female=live.total_female,
            total_intersex=live.total_intersex,
            births_this_month=live.births_current_month,
            deaths_this_month=live.deaths_current_month,
            pediatric_breakdown_json=live.pediatric_breakdown,
            psychosocial_breakdown_json=live.psychosocial_breakdown,
            recorded_at_total_seconds=now_secs,
        )
        session.add(census)
        session.flush()
        logger.info(
            "Census {}: alive={} births={} deaths={}",
            f"{current_dt.year}-{current_dt.month:02d}",
            census.total_alive,
            census.births_this_month,
            census.deaths_this_month,
        )
        return census

    @staticmethod
    def census_history(
        session: Session,
        *,
        year: int | None = None,
        limit: int | None = None,
    ) -> list[PopulationCensus]:
        """Storico dei censimenti, ordinato per (year, month) decrescente."""
        stmt = select(PopulationCensus).order_by(
            PopulationCensus.year.desc(), PopulationCensus.month.desc()
        )
        if year is not None:
            stmt = stmt.where(PopulationCensus.year == year)
        if limit is not None:
            stmt = stmt.limit(limit)
        return list(session.scalars(stmt))


__all__ = ["LiveStats", "PopulationStatsService"]
