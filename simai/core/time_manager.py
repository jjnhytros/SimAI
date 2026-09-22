"""TimeManager — gestore del tempo di simulazione.

Non è un singleton: va istanziato e iniettato dove serve (es. `SimulationLoop`
in Chunk 1.1). Questo rispetta la regola §4 del TODO: niente global mutabili,
accesso esplicito all'attore corrente e ai servizi.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Final

from simai.core.anthalys_calendar import AnthalysCalendar
from simai.core.anthalys_datetime import AnthalysDateTime
from simai.core.time_enums import DayPhase, Season

# --- Costanti event type ----------------------------------------------------

EVENT_TICK: Final[str] = "time.tick"
EVENT_HOUR_CHANGED: Final[str] = "time.hour.changed"
EVENT_DAY_CHANGED: Final[str] = "time.day.changed"
EVENT_MONTH_CHANGED: Final[str] = "time.month.changed"
EVENT_YEAR_CHANGED: Final[str] = "time.year.changed"
EVENT_SEASON_CHANGED: Final[str] = "time.season.changed"
EVENT_PHASE_CHANGED: Final[str] = "time.phase.changed"

ListenerCallback = Callable[[AnthalysDateTime, AnthalysDateTime], None]


@dataclass(frozen=True, slots=True)
class Listener:
    """Listener registrato su TimeManager.

    `priority` più alta = eseguito prima (ordinamento decrescente).
    """

    event_type: str
    callback: ListenerCallback
    priority: int = 0


class TimeManager:
    """Gestore del tempo di simulazione Anthalys.

    Responsabilità:
      - Mantiene `current: AnthalysDateTime`
      - Avanza di `tick_minutes` minuti Anthalys per tick
      - Emette eventi (`tick`, `hour_changed`, `day_changed`, ...)
      - Supporta listener con priorità

    Non è un singleton. Creare una istanza per simulazione.
    """

    def __init__(self, start: AnthalysDateTime, tick_minutes: int = 5) -> None:
        if tick_minutes < 1:
            raise ValueError(f"tick_minutes deve essere >= 1, ricevuto {tick_minutes}")
        self._current: AnthalysDateTime = start
        self._tick_minutes: int = tick_minutes
        self._listeners: list[Listener] = []

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def current(self) -> AnthalysDateTime:
        """Data/ora corrente di simulazione."""
        return self._current

    @property
    def tick_minutes(self) -> int:
        """Minuti Anthalys per tick."""
        return self._tick_minutes

    @property
    def current_phase(self) -> DayPhase:
        """Fase giornaliera corrente."""
        return AnthalysCalendar.phase_of(self._current)

    @property
    def current_season(self) -> Season:
        """Stagione corrente."""
        return AnthalysCalendar.season_of(self._current)

    @property
    def current_weekday(self) -> str:
        """Giorno della settimana corrente."""
        return AnthalysCalendar.weekday_of(self._current)

    # ------------------------------------------------------------------
    # Listener
    # ------------------------------------------------------------------

    def register_listener(
        self,
        event_type: str,
        callback: ListenerCallback,
        priority: int = 0,
    ) -> None:
        """Registra un listener su `event_type`. Priorità più alta = eseguito prima."""
        self._listeners.append(Listener(event_type, callback, priority))

    def subscribe_to_hour_change(self, callback: ListenerCallback, priority: int = 0) -> None:
        """Shortcut per `register_listener(EVENT_HOUR_CHANGED, ...)`."""
        self.register_listener(EVENT_HOUR_CHANGED, callback, priority)

    def subscribe_to_day_change(self, callback: ListenerCallback, priority: int = 0) -> None:
        """Shortcut per `register_listener(EVENT_DAY_CHANGED, ...)`."""
        self.register_listener(EVENT_DAY_CHANGED, callback, priority)

    def subscribe_to_month_change(self, callback: ListenerCallback, priority: int = 0) -> None:
        """Shortcut per `register_listener(EVENT_MONTH_CHANGED, ...)`."""
        self.register_listener(EVENT_MONTH_CHANGED, callback, priority)

    def subscribe_to_year_change(self, callback: ListenerCallback, priority: int = 0) -> None:
        """Shortcut per `register_listener(EVENT_YEAR_CHANGED, ...)`."""
        self.register_listener(EVENT_YEAR_CHANGED, callback, priority)

    # ------------------------------------------------------------------
    # Avanzamento tempo
    # ------------------------------------------------------------------

    def advance_tick(self) -> None:
        """Avanza di `tick_minutes` minuti Anthalys."""
        self._advance_minutes(self._tick_minutes)

    def advance_ticks(self, n: int) -> None:
        """Avanza di `n * tick_minutes` minuti Anthalys."""
        if n < 0:
            raise ValueError(f"n deve essere >= 0, ricevuto {n}")
        if n == 0:
            return
        self._advance_minutes(n * self._tick_minutes)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _advance_minutes(self, minutes: int) -> None:
        old = self._current
        new = old.add_minutes(minutes)
        self._current = new
        self._emit_changes(old, new)

    def _emit_changes(self, old: AnthalysDateTime, new: AnthalysDateTime) -> None:
        events: list[str] = [EVENT_TICK]

        if (old.year, old.month, old.day, old.hour) != (
            new.year,
            new.month,
            new.day,
            new.hour,
        ):
            events.append(EVENT_HOUR_CHANGED)

        if (old.year, old.month, old.day) != (new.year, new.month, new.day):
            events.append(EVENT_DAY_CHANGED)

        if (old.year, old.month) != (new.year, new.month):
            events.append(EVENT_MONTH_CHANGED)

        if old.year != new.year:
            events.append(EVENT_YEAR_CHANGED)

        if AnthalysCalendar.season_of(old) != AnthalysCalendar.season_of(new):
            events.append(EVENT_SEASON_CHANGED)

        if AnthalysCalendar.phase_of(old) != AnthalysCalendar.phase_of(new):
            events.append(EVENT_PHASE_CHANGED)

        for event_type in events:
            matching = [lst for lst in self._listeners if lst.event_type == event_type]
            for listener in sorted(matching, key=lambda lst: -lst.priority):
                listener.callback(old, new)
