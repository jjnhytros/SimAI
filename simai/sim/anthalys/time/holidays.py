"""Festività di Anthalys: fisse e mobili.

Le festività **fisse** cadono sempre nello stesso giorno (mese, giorno).
Le festività **mobili** dipendono da regole dinamiche (fasi lunari,
ricorrenze relative a festività fisse, ecc.).

Nel seed iniziale:
  - 12 festività fisse
  - 2 festività mobili (Luna Piena del mese 3; Eclissi Festival)
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from simai.core.anthalys_datetime import AnthalysDateTime
from simai.sim.anthalys.time.moons import MoonCycles


@dataclass(frozen=True, slots=True)
class Holiday:
    """Festività di Anthalys.

    Se `month`/`day` sono valorizzati, è **fissa**.
    Se `rule` è valorizzato, è **mobile** (la regola determina il match).
    """

    name: str
    description: str
    month: int | None = None
    day: int | None = None
    rule: Callable[[AnthalysDateTime, MoonCycles], bool] | None = None

    def __post_init__(self) -> None:
        has_fixed = self.month is not None and self.day is not None
        has_rule = self.rule is not None
        if has_fixed == has_rule:
            raise ValueError(f"'{self.name}': specificare (month, day) XOR rule, non entrambi")

    @property
    def is_fixed(self) -> bool:
        return self.month is not None and self.day is not None

    @property
    def is_mobile(self) -> bool:
        return self.rule is not None

    def matches(self, dt: AnthalysDateTime, moons: MoonCycles) -> bool:
        """``True`` se la festività cade a `dt`."""
        if self.is_fixed:
            return dt.month == self.month and dt.day == self.day
        # mobile
        assert self.rule is not None  # garantito da __post_init__
        return self.rule(dt, moons)


# ---------------------------------------------------------------------------
# Regole per festività mobili
# ---------------------------------------------------------------------------


def _rule_first_full_moon_of_month_3(dt: AnthalysDateTime, moons: MoonCycles) -> bool:
    """Luna Piena di Aelith nel mese 3 (festività mobile)."""
    if dt.month != 3:
        return False
    if dt.hour != 0 or dt.minute != 0 or dt.second != 0:
        return False
    moon = moons.get("Aelith")
    progress = moons.progress_of(moon, dt)
    if not (0.4375 <= progress < 0.5625):
        return False
    # Deve essere la prima del mese
    first_full = moons.first_full_moon_of_month(dt, "Aelith")
    return first_full is not None and first_full.day == dt.day


def _rule_eclipse_festival(dt: AnthalysDateTime, moons: MoonCycles) -> bool:
    """Eclipse Festival: giorno in cui 2+ lune sono FULL (tolleranza 0.03)."""
    if dt.hour != 0 or dt.minute != 0 or dt.second != 0:
        return False
    full_count = 0
    for moon in moons.moons:
        progress = moons.progress_of(moon, dt)
        # FULL quando progress ~0.5
        if abs(progress - 0.5) < 0.03:
            full_count += 1
    return full_count >= 2


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


class HolidayRegistry:
    """Registry delle festività di Anthalys."""

    def __init__(self, holidays: list[Holiday]) -> None:
        names = [h.name for h in holidays]
        if len(names) != len(set(names)):
            raise ValueError(f"Nomi festività duplicati: {names}")
        self._holidays = tuple(holidays)
        self._moons: MoonCycles | None = None

    # ------------------------------------------------------------------
    # Costruzione
    # ------------------------------------------------------------------

    @classmethod
    def default(cls) -> HolidayRegistry:
        """Registry di default: 12 fisse + 2 mobili."""
        return cls(
            [
                Holiday("Capodanno di Anthal", "Inizio dell'anno nuovo", month=1, day=1),
                Holiday(
                    "Festa della Luce",
                    "Rinascita della luce dopo il solstizio invernale",
                    month=2,
                    day=12,
                ),
                Holiday(
                    "Giorno del Raccolto",
                    "Ringraziamento per i frutti della terra",
                    month=4,
                    day=8,
                ),
                Holiday(
                    "Festa dei Fondatori",
                    "Onore ai fondatori di Anthal",
                    month=5,
                    day=15,
                ),
                Holiday("Solstizio d'Estate", "Giorno più lungo dell'anno", month=6, day=12),
                Holiday(
                    "Festa dell'Acqua",
                    "Celebrazione dei fiumi e dei mari",
                    month=7,
                    day=4,
                ),
                Holiday("Festa dei Morti", "Ricordo degli antenati", month=9, day=20),
                Holiday(
                    "Equinozio d'Autunno",
                    "Bilanciamento tra giorno e notte",
                    month=10,
                    day=12,
                ),
                Holiday(
                    "Festa del Fuoco",
                    "Celebrazione del calore domestico",
                    month=12,
                    day=8,
                ),
                Holiday(
                    "Festa dell'Arte",
                    "Onore agli artisti e ai creatori",
                    month=14,
                    day=16,
                ),
                Holiday("Solstizio d'Inverno", "Notte più lunga dell'anno", month=16, day=8),
                Holiday(
                    "Vigilia del Nuovo Anno",
                    "Ultimo giorno dell'anno",
                    month=18,
                    day=24,
                ),
                Holiday(
                    "Luna Piena di Aelith",
                    "Prima Luna Piena del mese 3 (mobile)",
                    rule=_rule_first_full_moon_of_month_3,
                ),
                Holiday(
                    "Eclipse Festival",
                    "Giorno in cui 2+ lune sono in fase Piena (mobile)",
                    rule=_rule_eclipse_festival,
                ),
            ]
        )

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    @property
    def holidays(self) -> tuple[Holiday, ...]:
        return self._holidays

    def on_date(self, dt: AnthalysDateTime, moons: MoonCycles | None = None) -> list[Holiday]:
        """Festività che cadono esattamente a `dt`."""
        mc = moons if moons is not None else MoonCycles.default()
        return [h for h in self._holidays if h.matches(dt, mc)]

    def next_after(
        self,
        dt: AnthalysDateTime,
        moons: MoonCycles | None = None,
        *,
        max_days: int = 500,
    ) -> tuple[AnthalysDateTime, list[Holiday]] | None:
        """Prossima data (dopo `dt`) con almeno una festività, entro `max_days`."""
        mc = moons if moons is not None else MoonCycles.default()
        current = dt
        for _ in range(max_days):
            current = current.add_minutes(28 * 60)  # +1 giorno
            matches = self.on_date(current, mc)
            if matches:
                return current, matches
        return None


__all__ = ["Holiday", "HolidayRegistry"]
