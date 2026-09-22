"""AddictionService — iniziazione, uso, craving, withdrawal, decay."""

from __future__ import annotations

import random
from dataclasses import dataclass

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.config.anthalys import SECONDS_PER_DAY
from simai.core.anthalys_datetime import AnthalysDateTime
from simai.npc.addictions.enums import (
    CRAVING_THRESHOLD_MILD,
    CRAVING_THRESHOLD_STRONG,
    CRAVING_THRESHOLD_WITHDRAWAL,
    DAYS_FOR_MILD_CRAVING,
    DAYS_FOR_STRONG_CRAVING,
    DAYS_FOR_WITHDRAWAL,
    DECAY_GRACE_DAYS,
    DECAY_RATE_PER_DAY,
    DEPENDENCE_PER_USE,
    INITIAL_DEPENDENCE,
    INITIATION_PROBABILITY,
    MAX_DEPENDENCE,
    MIN_DEPENDENCE,
    TOLERANCE_PER_USE,
    AddictionKind,
)
from simai.npc.addictions.models import Addiction


@dataclass(frozen=True, slots=True)
class UseResult:
    """Esito di un uso di sostanza."""

    kind: AddictionKind
    initiated: bool  # nuova addiction creata
    dependence_after: float
    craving_factor: float  # 0 se non addicted


@dataclass(frozen=True, slots=True)
class DailyTickResult:
    """Esito di un daily tick su una addiction."""

    kind: AddictionKind
    craving_level: str  # "NONE" | "MILD" | "STRONG" | "WITHDRAWAL"
    moodlet_delta: float  # 0 se nessun moodlet
    decayed: bool  # dependence diminuita
    removed: bool  # addiction rimossa


class AddictionService:
    """Servizio stateless per vizi e dipendenze."""

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    @staticmethod
    def get(
        session: Session,
        character_id: int,
        kind: AddictionKind,
    ) -> Addiction | None:
        return session.scalars(
            select(Addiction).where(
                Addiction.character_id == character_id,
                Addiction.kind == kind.value,
            )
        ).first()

    @staticmethod
    def all_of(session: Session, character_id: int) -> list[Addiction]:
        return list(
            session.scalars(
                select(Addiction)
                .where(Addiction.character_id == character_id)
                .order_by(Addiction.kind)
            )
        )

    # ------------------------------------------------------------------
    # Iniziazione / uso
    # ------------------------------------------------------------------

    @staticmethod
    def use(
        session: Session,
        *,
        character_id: int,
        kind: AddictionKind,
        current_dt: AnthalysDateTime,
        rng: random.Random,
    ) -> UseResult:
        """Registra un uso. Crea l'addiction se non esiste (con probabilità)."""
        existing = AddictionService.get(session, character_id, kind)
        now_secs = current_dt.to_total_seconds()

        if existing is None:
            # Tiro per l'iniziazione
            prob = INITIATION_PROBABILITY.get(kind, 0.05)
            if rng.random() < prob:
                dep = INITIAL_DEPENDENCE.get(kind, 10.0)
                addiction = Addiction(
                    character_id=character_id,
                    kind=kind.value,
                    dependence_level=dep,
                    tolerance=0.0,
                    last_use_total_seconds=now_secs,
                    started_at_total_seconds=now_secs,
                )
                session.add(addiction)
                session.flush()
                logger.info(
                    "Addiction iniziata: char={} kind={} dep={:.1f}",
                    character_id,
                    kind.value,
                    dep,
                )
                return UseResult(
                    kind=kind,
                    initiated=True,
                    dependence_after=dep,
                    craving_factor=0.0,
                )
            # Uso occasionale senza dipendenza
            return UseResult(
                kind=kind,
                initiated=False,
                dependence_after=0.0,
                craving_factor=0.0,
            )

        # Incremento
        dep_delta = DEPENDENCE_PER_USE.get(kind, 2.0)
        existing.dependence_level = min(MAX_DEPENDENCE, existing.dependence_level + dep_delta)
        existing.tolerance = min(MAX_DEPENDENCE, existing.tolerance + TOLERANCE_PER_USE)
        existing.last_use_total_seconds = now_secs
        session.flush()
        return UseResult(
            kind=kind,
            initiated=False,
            dependence_after=existing.dependence_level,
            craving_factor=0.0,  # appena usato, nessun craving
        )

    # ------------------------------------------------------------------
    # Craving
    # ------------------------------------------------------------------

    @staticmethod
    def craving_factor(
        addiction: Addiction,
        *,
        current_secs: int,
    ) -> float:
        """Ritorna un fattore di craving in [0, 1].

        0 = nessun craving, 1 = craving massimo.
        Il fattore è `dependence / MAX × min(days_since, 5) / 5`, clampato.
        """
        days_since = max(0.0, (current_secs - addiction.last_use_total_seconds) / SECONDS_PER_DAY)
        dep_norm = addiction.dependence_level / MAX_DEPENDENCE
        time_norm = min(days_since, 5.0) / 5.0
        return min(1.0, dep_norm * time_norm * 2.0)

    # ------------------------------------------------------------------
    # Daily tick
    # ------------------------------------------------------------------

    @staticmethod
    def daily_tick(
        session: Session,
        addiction: Addiction,
        *,
        current_dt: AnthalysDateTime,
    ) -> DailyTickResult:
        """Applica craving/withdrawal/decay in un giorno.

        Non applica moodlet: ritorna solo il delta che il chiamante userà
        per creare il moodlet.
        """
        current_secs = current_dt.to_total_seconds()
        days_since = (current_secs - addiction.last_use_total_seconds) / SECONDS_PER_DAY
        dep = addiction.dependence_level

        # Livello di craving
        level = "NONE"
        delta = 0.0
        if dep >= CRAVING_THRESHOLD_WITHDRAWAL and days_since >= DAYS_FOR_WITHDRAWAL:
            level = "WITHDRAWAL"
            delta = _withdrawal_delta(dep)
        elif dep >= CRAVING_THRESHOLD_STRONG and days_since >= DAYS_FOR_STRONG_CRAVING:
            level = "STRONG"
            delta = _strong_delta(dep)
        elif dep >= CRAVING_THRESHOLD_MILD and days_since >= DAYS_FOR_MILD_CRAVING:
            level = "MILD"
            delta = _mild_delta(dep)

        # Decay
        decayed = False
        removed = False
        if days_since >= DECAY_GRACE_DAYS:
            addiction.dependence_level = max(0.0, addiction.dependence_level - DECAY_RATE_PER_DAY)
            decayed = True
            if addiction.dependence_level < MIN_DEPENDENCE:
                session.delete(addiction)
                removed = True
                logger.info(
                    "Addiction rimossa per inattività: char={} kind={}",
                    addiction.character_id,
                    addiction.kind,
                )
        session.flush()

        return DailyTickResult(
            kind=addiction.type,
            craving_level=level,
            moodlet_delta=delta,
            decayed=decayed,
            removed=removed,
        )

    # ------------------------------------------------------------------
    # Helpers di alto livello
    # ------------------------------------------------------------------

    @staticmethod
    def start_addiction(
        session: Session,
        *,
        character_id: int,
        kind: AddictionKind,
        current_dt: AnthalysDateTime,
        initial_dependence: float | None = None,
    ) -> Addiction:
        """Crea forzatamente una addiction (dev tool / CLI)."""
        existing = AddictionService.get(session, character_id, kind)
        if existing is not None:
            return existing
        dep = (
            initial_dependence
            if initial_dependence is not None
            else (INITIAL_DEPENDENCE.get(kind, 10.0))
        )
        if dep <= 0 or dep > MAX_DEPENDENCE:
            raise ValueError(f"dependence deve essere in (0, {MAX_DEPENDENCE}], ricevuto {dep}")
        now_secs = current_dt.to_total_seconds()
        addiction = Addiction(
            character_id=character_id,
            kind=kind.value,
            dependence_level=dep,
            tolerance=0.0,
            last_use_total_seconds=now_secs,
            started_at_total_seconds=now_secs,
        )
        session.add(addiction)
        session.flush()
        return addiction


# ---------------------------------------------------------------------------
# Delta helpers (scala con dependence)
# ---------------------------------------------------------------------------


def _mild_delta(dep: float) -> float:
    from simai.npc.addictions.enums import MOODLET_MILD_DELTA

    return MOODLET_MILD_DELTA * (dep / CRAVING_THRESHOLD_STRONG)


def _strong_delta(dep: float) -> float:
    from simai.npc.addictions.enums import MOODLET_STRONG_DELTA

    return MOODLET_STRONG_DELTA * (dep / CRAVING_THRESHOLD_WITHDRAWAL)


def _withdrawal_delta(dep: float) -> float:
    from simai.npc.addictions.enums import MOODLET_WITHDRAWAL_DELTA

    return MOODLET_WITHDRAWAL_DELTA * (dep / MAX_DEPENDENCE)


__all__ = ["AddictionService", "DailyTickResult", "UseResult"]
