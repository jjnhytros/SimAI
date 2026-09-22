"""Lune di Anthalys: definizioni, fasi, cicli.

Tre lune con periodi orbitali distinti:
  - Aelith  : 27 giorni (la più veloce, "luna del raccolto")
  - Brumar  : 41 giorni (media, "luna del freddo")
  - Cindral : 89 giorni (lenta, "luna del destino")

La fase è calcolata in modo deterministico:
    progress = ((days_since_epoch + phase_offset * period) % period) / period

`progress = 0.0` -> Luna Nuova, `progress = 0.5` -> Luna Piena.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from simai.core.anthalys_calendar import AnthalysCalendar
from simai.core.anthalys_datetime import AnthalysDateTime


class MoonPhase(StrEnum):
    """Fasi lunari (8 fasi canoniche)."""

    NEW = "NEW"
    WAXING_CRESCENT = "WAXING_CRESCENT"
    FIRST_QUARTER = "FIRST_QUARTER"
    WAXING_GIBBOUS = "WAXING_GIBBOUS"
    FULL = "FULL"
    WANING_GIBBOUS = "WANING_GIBBOUS"
    LAST_QUARTER = "LAST_QUARTER"
    WANING_CRESCENT = "WANING_CRESCENT"


_PHASE_ORDER: tuple[MoonPhase, ...] = (
    MoonPhase.NEW,
    MoonPhase.WAXING_CRESCENT,
    MoonPhase.FIRST_QUARTER,
    MoonPhase.WAXING_GIBBOUS,
    MoonPhase.FULL,
    MoonPhase.WANING_GIBBOUS,
    MoonPhase.LAST_QUARTER,
    MoonPhase.WANING_CRESCENT,
)


@dataclass(frozen=True, slots=True)
class Moon:
    """Definizione di una luna di Anthalys."""

    name: str
    orbital_period_days: int
    phase_offset: float  # 0.0 - 1.0, offset iniziale al giorno 0

    def __post_init__(self) -> None:
        if self.orbital_period_days <= 0:
            raise ValueError(
                f"orbital_period_days deve essere > 0, ricevuto {self.orbital_period_days}"
            )
        if not (0.0 <= self.phase_offset < 1.0):
            raise ValueError(f"phase_offset deve essere in [0, 1), ricevuto {self.phase_offset}")


class MoonCycles:
    """Calcola le fasi lunari per un insieme di lune."""

    def __init__(self, moons: list[Moon]) -> None:
        if not moons:
            raise ValueError("Almeno una luna deve essere definita")
        names = [m.name for m in moons]
        if len(names) != len(set(names)):
            raise ValueError(f"Nomi luna duplicati: {names}")
        self._moons = tuple(moons)
        self._by_name: dict[str, Moon] = {m.name: m for m in moons}

    # ------------------------------------------------------------------
    # Costruzione
    # ------------------------------------------------------------------

    @classmethod
    def default(cls) -> MoonCycles:
        """Cicli lunari di default (3 lune lore-fixed)."""
        return cls(
            [
                Moon(name="Aelith", orbital_period_days=27, phase_offset=0.0),
                Moon(name="Brumar", orbital_period_days=41, phase_offset=0.35),
                Moon(name="Cindral", orbital_period_days=89, phase_offset=0.72),
            ]
        )

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    @property
    def moons(self) -> tuple[Moon, ...]:
        return self._moons

    def get(self, name: str) -> Moon:
        """Ritorna la luna con il nome dato. Solleva `KeyError` se assente."""
        try:
            return self._by_name[name]
        except KeyError as exc:
            raise KeyError(f"Luna sconosciuta: {name!r}") from exc

    def progress_of(self, moon: Moon, dt: AnthalysDateTime) -> float:
        """Progresso di fase in [0, 1). 0.0 = Luna Nuova, 0.5 = Luna Piena."""
        days = AnthalysCalendar.to_total_days(dt)
        period = moon.orbital_period_days
        offset = moon.phase_offset * period
        return ((days + offset) % period) / period

    def phase_of(self, moon: Moon, dt: AnthalysDateTime) -> MoonPhase:
        """Fase canonica della luna a `dt`."""
        progress = self.progress_of(moon, dt)
        idx = int(progress * 8) % 8
        return _PHASE_ORDER[idx]

    def all_progress(self, dt: AnthalysDateTime) -> dict[str, float]:
        """Progresso di tutte le lune a `dt`."""
        return {m.name: self.progress_of(m, dt) for m in self._moons}

    def all_phases(self, dt: AnthalysDateTime) -> dict[str, MoonPhase]:
        """Fase di tutte le lune a `dt`."""
        return {m.name: self.phase_of(m, dt) for m in self._moons}

    def first_full_moon_of_month(
        self, dt: AnthalysDateTime, moon_name: str = "Aelith"
    ) -> AnthalysDateTime | None:
        """Prima Luna Piena di `moon_name` nel mese di `dt`, o ``None``.

        Itera dal giorno 1 del mese fino a DAYS_PER_MONTH.
        """
        moon = self.get(moon_name)
        # Scansiona i giorni del mese per trovare il primo FULL
        for day in range(1, 25):
            try:
                candidate = AnthalysDateTime(dt.year, dt.month, day, 0, 0, 0)
            except ValueError:
                break
            # Range di FULL: progress in [0.4375, 0.5625)
            progress = self.progress_of(moon, candidate)
            if 0.4375 <= progress < 0.5625:
                return candidate
        return None


__all__ = ["Moon", "MoonCycles", "MoonPhase"]
