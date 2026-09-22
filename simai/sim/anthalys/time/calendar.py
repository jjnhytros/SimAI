"""Estensioni di `AnthalysCalendar` per il dominio Anthalys.

Il core fornisce già `AnthalysCalendar` con conversioni, stagioni,
fasi e giorni della settimana. Qui aggiungiamo helper di alto livello
utili nei package lore-specific.
"""

from __future__ import annotations

from simai.config.anthalys import (
    DAYS_PER_MONTH,
    HOURS_PER_DAY,
    MINUTES_PER_HOUR,
)
from simai.core.anthalys_calendar import AnthalysCalendar
from simai.core.anthalys_datetime import AnthalysDateTime

_MINUTES_PER_DAY: int = HOURS_PER_DAY * MINUTES_PER_HOUR


class CalendarExt:
    """Helper di alto livello sul calendario Anthalys (non istanziabile)."""

    # ------------------------------------------------------------------
    # Aritmetica
    # ------------------------------------------------------------------

    @staticmethod
    def add_days(dt: AnthalysDateTime, days: int) -> AnthalysDateTime:
        """Aggiunge `days` giorni (interi) a `dt`."""
        return dt.add_minutes(days * _MINUTES_PER_DAY)

    @staticmethod
    def days_between(a: AnthalysDateTime, b: AnthalysDateTime) -> int:
        """Numero di giorni interi tra `a` e `b` (b - a, può essere negativo)."""
        return AnthalysCalendar.to_total_days(b) - AnthalysCalendar.to_total_days(a)

    # ------------------------------------------------------------------
    # Boundary helpers
    # ------------------------------------------------------------------

    @staticmethod
    def start_of_day(dt: AnthalysDateTime) -> AnthalysDateTime:
        """Mezzanotte (00:00:00) del giorno di `dt`."""
        return AnthalysDateTime(dt.year, dt.month, dt.day, 0, 0, 0)

    @staticmethod
    def end_of_day(dt: AnthalysDateTime) -> AnthalysDateTime:
        """Ultimo secondo del giorno di `dt` (H-1:59:59)."""
        return AnthalysDateTime(
            dt.year,
            dt.month,
            dt.day,
            HOURS_PER_DAY - 1,
            MINUTES_PER_HOUR - 1,
            59,
        )

    @staticmethod
    def start_of_month(dt: AnthalysDateTime) -> AnthalysDateTime:
        """Primo giorno del mese alle 00:00:00."""
        return AnthalysDateTime(dt.year, dt.month, 1, 0, 0, 0)

    @staticmethod
    def end_of_month(dt: AnthalysDateTime) -> AnthalysDateTime:
        """Ultimo giorno del mese alle H-1:59:59."""
        return AnthalysDateTime(
            dt.year,
            dt.month,
            DAYS_PER_MONTH,
            HOURS_PER_DAY - 1,
            MINUTES_PER_HOUR - 1,
            59,
        )

    @staticmethod
    def start_of_year(dt: AnthalysDateTime) -> AnthalysDateTime:
        """1-1 dell'anno di `dt` alle 00:00:00."""
        return AnthalysDateTime(dt.year, 1, 1, 0, 0, 0)


__all__ = ["AnthalysCalendar", "AnthalysDateTime", "CalendarExt"]
