"""AnthalysDateTime — data/ora immutabile del calendario di Anthalys."""

from __future__ import annotations

from dataclasses import dataclass

from simai.config.anthalys import (
    DAYS_PER_MONTH,
    DAYS_PER_YEAR,
    HOURS_PER_DAY,
    MINUTES_PER_HOUR,
    MONTHS_PER_YEAR,
    SECONDS_PER_MINUTE,
)

_SECONDS_PER_HOUR: int = MINUTES_PER_HOUR * SECONDS_PER_MINUTE
_SECONDS_PER_DAY: int = HOURS_PER_DAY * _SECONDS_PER_HOUR
_SECONDS_PER_YEAR: int = DAYS_PER_YEAR * _SECONDS_PER_DAY


@dataclass(frozen=True, slots=True, order=True)
class AnthalysDateTime:
    """Data/ora immutabile nel calendario di Anthalys.

    Campi (ordinamento cronologico naturale via `order=True`):
      - `year`   : anno Anthalys (>= 1)
      - `month`  : 1..18
      - `day`    : 1..24
      - `hour`   : 0..27
      - `minute` : 0..59
      - `second` : 0..59

    L'ordinamento `<`, `<=`, `>`, `>=` segue l'ordine cronologico dei campi
    (year, month, day, hour, minute, second), che è esattamente l'ordine
    lessicografico — quindi `@dataclass(order=True)` è sufficiente.
    """

    year: int
    month: int
    day: int
    hour: int = 0
    minute: int = 0
    second: int = 0

    def __post_init__(self) -> None:
        if self.year < 1:
            raise ValueError(f"year deve essere >= 1, ricevuto {self.year}")
        if not (1 <= self.month <= MONTHS_PER_YEAR):
            raise ValueError(f"month deve essere 1..{MONTHS_PER_YEAR}, ricevuto {self.month}")
        if not (1 <= self.day <= DAYS_PER_MONTH):
            raise ValueError(f"day deve essere 1..{DAYS_PER_MONTH}, ricevuto {self.day}")
        if not (0 <= self.hour < HOURS_PER_DAY):
            raise ValueError(f"hour deve essere 0..{HOURS_PER_DAY - 1}, ricevuto {self.hour}")
        if not (0 <= self.minute < MINUTES_PER_HOUR):
            raise ValueError(
                f"minute deve essere 0..{MINUTES_PER_HOUR - 1}, ricevuto {self.minute}"
            )
        if not (0 <= self.second < SECONDS_PER_MINUTE):
            raise ValueError(
                f"second deve essere 0..{SECONDS_PER_MINUTE - 1}, ricevuto {self.second}"
            )

    # ------------------------------------------------------------------
    # Conversioni a/da secondi totali (epoch = 1-1-1 00:00:00 Anthalys)
    # ------------------------------------------------------------------

    def to_total_seconds(self) -> int:
        """Secondi totali trascorsi da 1-1-1 00:00:00 Anthalys."""
        days = (self.year - 1) * DAYS_PER_YEAR + (self.month - 1) * DAYS_PER_MONTH + (self.day - 1)
        return (
            days * _SECONDS_PER_DAY
            + self.hour * _SECONDS_PER_HOUR
            + self.minute * SECONDS_PER_MINUTE
            + self.second
        )

    @classmethod
    def from_total_seconds(cls, total_seconds: int) -> AnthalysDateTime:
        """Costruisce un `AnthalysDateTime` da secondi totali dall'anno 1."""
        if total_seconds < 0:
            raise ValueError(f"total_seconds deve essere >= 0, ricevuto {total_seconds}")
        year_idx, rem = divmod(total_seconds, _SECONDS_PER_YEAR)
        day_idx, rem = divmod(rem, _SECONDS_PER_DAY)
        hour, rem = divmod(rem, _SECONDS_PER_HOUR)
        minute, second = divmod(rem, SECONDS_PER_MINUTE)
        month_idx, day_in_month_idx = divmod(day_idx, DAYS_PER_MONTH)
        return cls(
            year=year_idx + 1,
            month=month_idx + 1,
            day=day_in_month_idx + 1,
            hour=hour,
            minute=minute,
            second=second,
        )

    # ------------------------------------------------------------------
    # Aritmetica
    # ------------------------------------------------------------------

    def add_minutes(self, minutes: int) -> AnthalysDateTime:
        """Restituisce una nuova istanza avanzata di `minutes` minuti Anthalys."""
        if minutes == 0:
            return self
        new_total = self.to_total_seconds() + minutes * SECONDS_PER_MINUTE
        if new_total < 0:
            raise ValueError("Risultato precedente all'anno 1 — non supportato")
        return AnthalysDateTime.from_total_seconds(new_total)

    def add_seconds(self, seconds: int) -> AnthalysDateTime:
        """Restituisce una nuova istanza avanzata di `seconds` secondi Anthalys."""
        if seconds == 0:
            return self
        new_total = self.to_total_seconds() + seconds
        if new_total < 0:
            raise ValueError("Risultato precedente all'anno 1 — non supportato")
        return AnthalysDateTime.from_total_seconds(new_total)

    # ------------------------------------------------------------------
    # Serializzazione
    # ------------------------------------------------------------------

    def to_iso_string(self) -> str:
        """Formato ISO-like: `YYYY-MM-DDTHH:MM:SS` (zero-padded)."""
        return (
            f"{self.year:04d}-{self.month:02d}-{self.day:02d}"
            f"T{self.hour:02d}:{self.minute:02d}:{self.second:02d}"
        )

    @classmethod
    def from_iso_string(cls, s: str) -> AnthalysDateTime:
        """Parse di una stringa `YYYY-MM-DDTHH:MM:SS` in `AnthalysDateTime`."""
        try:
            date_part, time_part = s.split("T")
            y_s, mo_s, d_s = date_part.split("-")
            h_s, mi_s, sec_s = time_part.split(":")
            return cls(
                year=int(y_s),
                month=int(mo_s),
                day=int(d_s),
                hour=int(h_s),
                minute=int(mi_s),
                second=int(sec_s),
            )
        except (ValueError, AttributeError) as exc:
            raise ValueError(
                f"Formato ISO Anthalys non valido: {s!r} (atteso: YYYY-MM-DDTHH:MM:SS)"
            ) from exc

    def __str__(self) -> str:
        return (
            f"{self.year:04d}-{self.month:02d}-{self.day:02d} "
            f"{self.hour:02d}:{self.minute:02d}:{self.second:02d}"
        )
