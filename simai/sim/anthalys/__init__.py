"""Package Anthalys — estensioni lore-specific.

Contenuto:
  - `simai.sim.anthalys.time` — calendario esteso, festività, lune, astro

Tutto il codice qui è **lore-specific** e non fa parte del core.
"""

from simai.sim.anthalys.time import (
    ALIGNMENT_TOLERANCE,
    P_COMET_PER_DAY,
    AnthalysClock,
    AstroEvent,
    AstroEventsEngine,
    AstroEventType,
    CalendarExt,
    Holiday,
    HolidayRegistry,
    Moon,
    MoonCycles,
    MoonPhase,
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
