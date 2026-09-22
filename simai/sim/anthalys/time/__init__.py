"""Package `simai.sim.anthalys.time` — estensioni lore-specific Anthalys.

Contenuto:
  - `AnthalysClock`      — facade su TimeManager con dati Anthalys
  - `CalendarExt`        — helper avanzati su AnthalysCalendar
  - `HolidayRegistry`    — festività fisse e mobili
  - `MoonCycles`         — 3 lune con fasi e progressi
  - `AstroEventsEngine`  — eclissi, comete, piogge di meteore
  - `season_info`        — metadati estesi sulle stagioni
"""

from simai.sim.anthalys.time.astro import (
    ALIGNMENT_TOLERANCE,
    P_COMET_PER_DAY,
    AstroEvent,
    AstroEventsEngine,
    AstroEventType,
)
from simai.sim.anthalys.time.calendar import CalendarExt
from simai.sim.anthalys.time.clock import AnthalysClock
from simai.sim.anthalys.time.holidays import Holiday, HolidayRegistry
from simai.sim.anthalys.time.moons import Moon, MoonCycles, MoonPhase
from simai.sim.anthalys.time.seasons import (
    SeasonInfo,
    days_until_next_season,
    next_season_start,
    season_info,
)

__all__ = [
    "ALIGNMENT_TOLERANCE",
    "P_COMET_PER_DAY",
    "AnthalysClock",
    "AstroEvent",
    "AstroEventType",
    "AstroEventsEngine",
    "CalendarExt",
    "Holiday",
    "HolidayRegistry",
    "Moon",
    "MoonCycles",
    "MoonPhase",
    "SeasonInfo",
    "days_until_next_season",
    "next_season_start",
    "season_info",
]
