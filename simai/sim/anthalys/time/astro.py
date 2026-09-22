"""Eventi astronomici di Anthalys: eclissi e comete.

Design:
  - **Eclissi**: deterministiche. Si verificano quando 2+ lune sono in fase
    FULL o NEW contemporaneamente (tolleranza 0.03 sul progresso).
  - **Comete**: pseudo-casuali ma **deterministiche dal seed**. La probabilità
    per giorno è `P_COMET_PER_DAY = 1/500`. Il seed effettivo è
    `master_seed + day_of_year_total`, garantendo riproducibilità.
  - **Pioggia di meteore**: legata a un mese specifico (mese 8) e a una
    fase lunare (Luna Nuova di Cindral).
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from enum import StrEnum
from typing import Final

from simai.core.anthalys_calendar import AnthalysCalendar
from simai.core.anthalys_datetime import AnthalysDateTime
from simai.sim.anthalys.time.moons import MoonCycles, MoonPhase

#: Probabilità giornaliera di una cometa (deterministica via seed).
P_COMET_PER_DAY: Final[float] = 1.0 / 500.0

#: Tolleranza sul progresso lunare per considerare due lune "allineate".
ALIGNMENT_TOLERANCE: Final[float] = 0.03


class AstroEventType(StrEnum):
    """Tipo di evento astronomico."""

    ECLIPSE = "ECLIPSE"
    COMET = "COMET"
    METEOR_SHOWER = "METEOR_SHOWER"


@dataclass(frozen=True, slots=True)
class AstroEvent:
    """Evento astronomico avvenuto (o previsto) a una certa data."""

    type: AstroEventType
    datetime: AnthalysDateTime
    description: str


class AstroEventsEngine:
    """Motore deterministico per eventi astronomici."""

    def __init__(self, moons: MoonCycles, master_seed: int) -> None:
        self._moons = moons
        self._master_seed = master_seed

    # ------------------------------------------------------------------
    # Eclissi
    # ------------------------------------------------------------------

    def is_eclipse_day(self, dt: AnthalysDateTime) -> bool:
        """``True`` se almeno 2 lune sono in fase FULL o NEW a mezzanotte di `dt`."""
        midnight = AnthalysDateTime(dt.year, dt.month, dt.day, 0, 0, 0)
        phases = self._moons.all_phases(midnight)
        aligned_count = sum(1 for p in phases.values() if p in (MoonPhase.FULL, MoonPhase.NEW))
        # Conta anche "quasi allineate" (tolleranza)
        for moon in self._moons.moons:
            progress = self._moons.progress_of(moon, midnight)
            near_full = abs(progress - 0.5) < ALIGNMENT_TOLERANCE
            near_new = progress < ALIGNMENT_TOLERANCE or progress > 1.0 - ALIGNMENT_TOLERANCE
            if near_full or near_new:
                aligned_count = max(aligned_count, 1)
        # Serve almeno 2 lune allineate (contate come FULL/NEW "strette")
        strict_full = sum(
            1
            for moon in self._moons.moons
            if abs(self._moons.progress_of(moon, midnight) - 0.5) < ALIGNMENT_TOLERANCE
        )
        strict_new = sum(
            1
            for moon in self._moons.moons
            if self._moons.progress_of(moon, midnight) < ALIGNMENT_TOLERANCE
        )
        return (strict_full + strict_new) >= 2

    def next_eclipse(
        self, from_dt: AnthalysDateTime, *, horizon_days: int = 2000
    ) -> AstroEvent | None:
        """Prossima eclissi dopo `from_dt`, entro `horizon_days`."""
        current = AnthalysDateTime(from_dt.year, from_dt.month, from_dt.day, 0, 0, 0)
        for _ in range(horizon_days):
            current = current.add_minutes(28 * 60)
            if self.is_eclipse_day(current):
                return AstroEvent(
                    type=AstroEventType.ECLIPSE,
                    datetime=current,
                    description="Eclissi: allineamento di 2+ lune",
                )
        return None

    # ------------------------------------------------------------------
    # Comete (deterministiche via seed)
    # ------------------------------------------------------------------

    def is_comet_day(self, dt: AnthalysDateTime) -> bool:
        """``True`` se una cometa appare a mezzanotte di `dt` (deterministico)."""
        midnight = AnthalysDateTime(dt.year, dt.month, dt.day, 0, 0, 0)
        day_idx = AnthalysCalendar.to_total_days(midnight)
        rng = random.Random(self._master_seed + day_idx)
        return rng.random() < P_COMET_PER_DAY

    def next_comet(
        self, from_dt: AnthalysDateTime, *, horizon_days: int = 5000
    ) -> AstroEvent | None:
        """Prossima cometa dopo `from_dt`, entro `horizon_days`."""
        current = AnthalysDateTime(from_dt.year, from_dt.month, from_dt.day, 0, 0, 0)
        for _ in range(horizon_days):
            current = current.add_minutes(28 * 60)
            if self.is_comet_day(current):
                return AstroEvent(
                    type=AstroEventType.COMET,
                    datetime=current,
                    description="Cometa avvistata nei cieli di Anthalys",
                )
        return None

    # ------------------------------------------------------------------
    # Piogge di meteore (legate a Cindral + mese 8)
    # ------------------------------------------------------------------

    def is_meteor_shower_day(self, dt: AnthalysDateTime) -> bool:
        """Pioggia di meteore: mese 8, giorno 12, Luna Nuova di Cindral."""
        if dt.month != 8 or dt.day != 12:
            return False
        midnight = AnthalysDateTime(dt.year, dt.month, dt.day, 0, 0, 0)
        cindral = self._moons.get("Cindral")
        return self._moons.phase_of(cindral, midnight) is MoonPhase.NEW

    def next_meteor_shower(
        self, from_dt: AnthalysDateTime, *, horizon_years: int = 100
    ) -> AstroEvent | None:
        """Prossima pioggia di meteore, entro `horizon_years` anni."""
        current = AnthalysDateTime(from_dt.year, from_dt.month, from_dt.day, 0, 0, 0)
        horizon_days = horizon_years * 432
        for _ in range(horizon_days):
            current = current.add_minutes(28 * 60)
            if self.is_meteor_shower_day(current):
                return AstroEvent(
                    type=AstroEventType.METEOR_SHOWER,
                    datetime=current,
                    description="Pioggia di meteore di Cindral",
                )
        return None

    # ------------------------------------------------------------------
    # Aggregato
    # ------------------------------------------------------------------

    def next_events(
        self,
        from_dt: AnthalysDateTime,
        *,
        horizon_days: int = 2000,
    ) -> list[AstroEvent]:
        """Tutti gli eventi astronomici (eclissi + comete + meteore) nel range."""
        events: list[AstroEvent] = []
        eclipse = self.next_eclipse(from_dt, horizon_days=horizon_days)
        if eclipse is not None:
            events.append(eclipse)
        comet = self.next_comet(from_dt, horizon_days=horizon_days)
        if comet is not None:
            events.append(comet)
        meteor = self.next_meteor_shower(from_dt, horizon_years=10)
        if meteor is not None:
            events.append(meteor)
        events.sort(key=lambda e: e.datetime)
        return events


__all__ = ["AstroEvent", "AstroEventType", "AstroEventsEngine"]
