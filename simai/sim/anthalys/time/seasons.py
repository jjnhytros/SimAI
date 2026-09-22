"""Informazioni dettagliate sulle stagioni di Anthalys.

4 stagioni da 108 giorni. L'inverno inizia il giorno 16 del mese 18
(day-of-year 424). Questo modulo fornisce metadati di alto livello:
giorno della stagione, giorni rimanenti, progresso, prossima stagione.
"""

from __future__ import annotations

from dataclasses import dataclass

from simai.config.anthalys import (
    DAYS_PER_YEAR,
    SEASON_LENGTH_DAYS,
    SEASON_START_DAY_OF_YEAR,
)
from simai.core.anthalys_calendar import AnthalysCalendar
from simai.core.anthalys_datetime import AnthalysDateTime
from simai.core.time_enums import Season

# Ordine ciclico delle stagioni (l'inverno chiude e riapre il ciclo).
_SEASON_CYCLE: tuple[Season, ...] = (
    Season.WINTER,
    Season.SPRING,
    Season.SUMMER,
    Season.AUTUMN,
)


@dataclass(frozen=True, slots=True)
class SeasonInfo:
    """Metadati dettagliati sulla stagione corrente."""

    season: Season
    day_of_season: int  # 1..108
    days_remaining: int  # 0..107
    progress: float  # 0.0 .. 1.0
    next_season: Season


def season_info(dt: AnthalysDateTime) -> SeasonInfo:
    """Calcola i metadati della stagione a `dt`."""
    season = AnthalysCalendar.season_of(dt)
    doy = AnthalysCalendar.day_of_year(dt)
    start_doy = SEASON_START_DAY_OF_YEAR[season.value]

    # Posizione del giorno nel ciclo stagionale (0..431), con offset per
    # far partire l'inverno dal suo start reale (doy 424).
    # Calcoliamo quanti giorni sono passati dall'inizio della stagione.
    if season == Season.WINTER:
        # Inverno copre 424..432 e 1..99
        if doy >= start_doy:
            day_of_season = doy - start_doy + 1
        else:
            # Siamo nella coda dell'inverno: giorni 1..99
            tail_days = DAYS_PER_YEAR - start_doy + 1  # 432 - 424 + 1 = 9
            day_of_season = tail_days + doy
    else:
        day_of_season = doy - start_doy + 1

    days_remaining = SEASON_LENGTH_DAYS - day_of_season
    progress = day_of_season / SEASON_LENGTH_DAYS

    idx = _SEASON_CYCLE.index(season)
    next_season = _SEASON_CYCLE[(idx + 1) % len(_SEASON_CYCLE)]

    return SeasonInfo(
        season=season,
        day_of_season=day_of_season,
        days_remaining=days_remaining,
        progress=progress,
        next_season=next_season,
    )


def days_until_next_season(dt: AnthalysDateTime) -> int:
    """Giorni interi mancanti all'inizio della prossima stagione."""
    info = season_info(dt)
    return info.days_remaining + 1


def next_season_start(dt: AnthalysDateTime) -> AnthalysDateTime:
    """Data/ora d'inizio della prossima stagione (00:00:00)."""
    from simai.sim.anthalys.time.calendar import CalendarExt

    info = season_info(dt)
    target_doy = SEASON_START_DAY_OF_YEAR[info.next_season.value]

    # Determina l'anno di partenza in base al doy corrente
    current_doy = AnthalysCalendar.day_of_year(dt)
    year = dt.year
    if target_doy <= current_doy:
        year += 1

    # Ricava (month, day) da day-of-year
    month = (target_doy - 1) // 24 + 1
    day = (target_doy - 1) % 24 + 1
    return CalendarExt.start_of_day(AnthalysDateTime(year, month, day))


__all__ = [
    "SeasonInfo",
    "days_until_next_season",
    "next_season_start",
    "season_info",
]
