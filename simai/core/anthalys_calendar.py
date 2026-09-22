"""AnthalysCalendar — conversioni, stagioni, fasi e giorni della settimana.

Epoch arbitrario documentato per la conversione gregoriana:
    1-1-1 Anthalys 00:00:00  <->  1 gennaio 1000 d.C. 00:00:00 (UTC naive)

La conversione è **approssimata** e **lossy**:
  - 1 giorno Anthalys = 1 giorno gregoriano
  - i minuti del giorno sono rimappati linearmente:
      1680 minuti Anthalys/giorno -> 1440 minuti gregoriani/giorno
  - i secondi dentro il minuto restano identici (0..59)

Non è garantita l'invertibilità perfetta `from_gregorian(to_gregorian(x)) == x`
a causa del floor nelle rimappature.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Final

from simai.config.anthalys import (
    DAY_PHASE_BOUNDARIES,
    DAYS_PER_MONTH,
    DAYS_PER_YEAR,
    HOURS_PER_DAY,
    MINUTES_PER_HOUR,
    MONTHS,
    WEEKDAYS,
)
from simai.core.anthalys_datetime import AnthalysDateTime
from simai.core.time_enums import DayPhase, Season

# --- Epoch arbitrario documentato -----------------------------------------

GREGORIAN_EPOCH_DATETIME: Final[datetime] = datetime(1000, 1, 1, 0, 0, 0)
GREGORIAN_EPOCH_ANTHALYS: Final[AnthalysDateTime] = AnthalysDateTime(1, 1, 1)

_ANTH_MINUTES_PER_DAY: Final[int] = HOURS_PER_DAY * MINUTES_PER_HOUR
_GREG_MINUTES_PER_DAY: Final[int] = 24 * 60


class AnthalysCalendar:
    """Utility statiche per il calendario di Anthalys.

    Non è istanziabile: tutti i metodi sono `@staticmethod`.
    """

    # ------------------------------------------------------------------
    # Giorni totali / giorno dell'anno
    # ------------------------------------------------------------------

    @staticmethod
    def to_total_days(dt: AnthalysDateTime) -> int:
        """Giorni totali trascorsi da 1-1-1 Anthalys (1-1-1 -> 0)."""
        return (dt.year - 1) * DAYS_PER_YEAR + (dt.month - 1) * DAYS_PER_MONTH + (dt.day - 1)

    @staticmethod
    def day_of_year(dt: AnthalysDateTime) -> int:
        """Giorno dell'anno in [1, 432]."""
        return (dt.month - 1) * DAYS_PER_MONTH + dt.day

    @staticmethod
    def month_name(dt: AnthalysDateTime) -> str:
        """Nome del mese di Anthalys."""
        return MONTHS[dt.month - 1]

    @staticmethod
    def weekday_of(dt: AnthalysDateTime) -> str:
        """Nome del giorno della settimana (ciclo continuo di 7 giorni).

        Il ciclo NON si resetta ad ogni anno: 432 mod 7 = 5, quindi il
        giorno della settimana del 1-1 di anni consecutivi avanza di 5.
        """
        return WEEKDAYS[AnthalysCalendar.to_total_days(dt) % len(WEEKDAYS)]

    # ------------------------------------------------------------------
    # Stagioni e fasi
    # ------------------------------------------------------------------

    @staticmethod
    def season_of(dt: AnthalysDateTime) -> Season:
        """Stagione corrente (4 stagioni da 108 giorni).

        Mappatura day-of-year:
          - Inverno   : 1..99    e  424..432
          - Primavera : 100..207
          - Estate    : 208..315
          - Autunno   : 316..423
        """
        doy = AnthalysCalendar.day_of_year(dt)
        if 100 <= doy <= 207:
            return Season.SPRING
        if 208 <= doy <= 315:
            return Season.SUMMER
        if 316 <= doy <= 423:
            return Season.AUTUMN
        return Season.WINTER

    @staticmethod
    def phase_of(dt: AnthalysDateTime) -> DayPhase:
        """Fase della giornata in base all'ora (0..27)."""
        for phase_name, (start, end) in DAY_PHASE_BOUNDARIES.items():
            if start <= dt.hour < end:
                return DayPhase(phase_name)
        raise ValueError(f"Nessuna DayPhase per hour={dt.hour}")

    # ------------------------------------------------------------------
    # Conversioni gregoriane (approssimazione documentata)
    # ------------------------------------------------------------------

    @staticmethod
    def to_gregorian(dt: AnthalysDateTime) -> datetime:
        """Converte `AnthalysDateTime` in `datetime` gregoriano naive.

        Vedi docstring del modulo per i dettagli sull'approssimazione.
        """
        total_days = AnthalysCalendar.to_total_days(dt)
        anth_min_of_day = dt.hour * MINUTES_PER_HOUR + dt.minute
        greg_min_of_day = anth_min_of_day * _GREG_MINUTES_PER_DAY // _ANTH_MINUTES_PER_DAY
        greg_hour, greg_minute = divmod(greg_min_of_day, 60)
        return GREGORIAN_EPOCH_DATETIME + timedelta(
            days=total_days,
            hours=greg_hour,
            minutes=greg_minute,
            seconds=dt.second,
        )

    @staticmethod
    def from_gregorian(dt: datetime) -> AnthalysDateTime:
        """Converte un `datetime` gregoriano naive in `AnthalysDateTime`.

        Inversa *best effort* di `to_gregorian`. Non garantita l'identità
        per round-trip a causa del floor nella rimappatura dei minuti.
        """
        if dt.tzinfo is not None:
            raise ValueError("datetime con timezone non supportato: usa naive UTC")
        delta = dt - GREGORIAN_EPOCH_DATETIME
        if delta.total_seconds() < 0:
            raise ValueError("datetime precedente all'epoch gregoriano 1000-01-01 — non supportato")
        total_days = delta.days
        greg_min_of_day = dt.hour * 60 + dt.minute
        anth_min_of_day = greg_min_of_day * _ANTH_MINUTES_PER_DAY // _GREG_MINUTES_PER_DAY
        anth_hour, anth_minute = divmod(anth_min_of_day, 60)

        # Ricostruisci (year, month, day) da total_days
        year_idx, rem = divmod(total_days, DAYS_PER_YEAR)
        month_idx, day_idx = divmod(rem, DAYS_PER_MONTH)
        return AnthalysDateTime(
            year=year_idx + 1,
            month=month_idx + 1,
            day=day_idx + 1,
            hour=anth_hour,
            minute=anth_minute,
            second=dt.second,
        )
