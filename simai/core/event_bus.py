"""EventBus — bus di eventi centralizzato per SimAI.

Differenza rispetto ai listener di `TimeManager`:
  - `TimeManager` ha listener dedicati al dominio temporale
    (`time.tick`, `time.hour.changed`, ...) — altamente specializzati.
  - `EventBus` è per eventi di dominio generici emessi da qualsiasi package
    (NPC, World, Economy, ...) e processati in coda ad ogni tick.

Design:
  - `emit(event_type, **payload)` accoda (non esegue subito).
  - `emit_now(event_type, **payload)` esegue subito (bypassa la coda).
  - `subscribe(event_type, callback, priority)` registra un subscriber.
  - `process_queue()` svuota la coda eseguendo i subscriber in ordine di priorità.
  - Supporto wildcard: `subscribe(WILDCARD, ...)` riceve tutti gli eventi.
  - Single-thread by design (regola §V.3 del TODO).
  - Gli eventi emessi durante `process_queue()` vengono accodati e processati
    nello stesso giro (cascata). Questo è intenzionale: consente pattern di
    reazione a catena controllati.
"""

from __future__ import annotations

from collections import deque
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from typing import Any, Final

WILDCARD: Final[str] = "*"

EventPayload = dict[str, Any]
EventCallback = Callable[[str, EventPayload], None]


@dataclass(frozen=True, slots=True)
class Event:
    """Evento accodato nel bus."""

    type: str
    payload: EventPayload


@dataclass(frozen=True, slots=True)
class Subscriber:
    """Subscriber registrato su un `event_type` (o wildcard)."""

    event_type: str
    callback: EventCallback
    priority: int = 0


class EventBus:
    """Bus di eventi con coda e priorità. Single-thread.

    Non è un singleton. Creare una istanza per simulazione e iniettarla
    dove serve (tipicamente in `SimulationLoop`).
    """

    def __init__(self) -> None:
        self._queue: deque[Event] = deque()
        self._subscribers: list[Subscriber] = []
        self._stats_emitted: int = 0
        self._stats_processed: int = 0

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def queue_size(self) -> int:
        """Numero di eventi attualmente in coda."""
        return len(self._queue)

    @property
    def stats_emitted(self) -> int:
        """Totale eventi emessi (accodati o immediati)."""
        return self._stats_emitted

    @property
    def stats_processed(self) -> int:
        """Totale eventi processati dalla coda."""
        return self._stats_processed

    @property
    def subscriber_count(self) -> int:
        """Numero di subscriber registrati."""
        return len(self._subscribers)

    # ------------------------------------------------------------------
    # Subscribe / Unsubscribe
    # ------------------------------------------------------------------

    def subscribe(
        self,
        event_type: str,
        callback: EventCallback,
        priority: int = 0,
    ) -> None:
        """Registra un subscriber.

        `event_type` può essere `WILDCARD` (``"*"``) per ricevere tutti gli eventi.
        Priorità più alta = eseguito prima. A parità di priorità vince
        l'ordine di registrazione (stable sort).
        """
        self._subscribers.append(Subscriber(event_type, callback, priority))

    def unsubscribe(self, callback: EventCallback) -> int:
        """Rimuove tutte le sottoscrizioni per la callback data.

        Ritorna il numero di sottoscrizioni rimosse.
        """
        before = len(self._subscribers)
        self._subscribers = [s for s in self._subscribers if s.callback is not callback]
        return before - len(self._subscribers)

    # ------------------------------------------------------------------
    # Emit
    # ------------------------------------------------------------------

    def emit(self, event_type: str, **payload: Any) -> None:
        """Accoda un evento (non esegue subito)."""
        self._queue.append(Event(event_type, payload))
        self._stats_emitted += 1

    def emit_now(self, event_type: str, **payload: Any) -> None:
        """Emette ed esegue subito (bypassa la coda)."""
        self._stats_emitted += 1
        self._dispatch(Event(event_type, payload))

    # ------------------------------------------------------------------
    # Process
    # ------------------------------------------------------------------

    def process_queue(self, max_events: int | None = None) -> int:
        """Processa la coda in ordine FIFO. Ritorna il numero di eventi processati.

        `max_events` limita quanti eventi processare (utile per test o per
        prevenire loop infiniti da cascate patologiche).
        """
        processed = 0
        while self._queue:
            if max_events is not None and processed >= max_events:
                break
            event = self._queue.popleft()
            self._dispatch(event)
            processed += 1
            self._stats_processed += 1
        return processed

    def clear(self) -> int:
        """Svuota la coda senza processare. Ritorna il numero di eventi scartati."""
        dropped = len(self._queue)
        self._queue.clear()
        return dropped

    # ------------------------------------------------------------------
    # Iteration (debug)
    # ------------------------------------------------------------------

    def __iter__(self) -> Iterator[Event]:
        """Itera la coda (snapshot)."""
        return iter(list(self._queue))

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _dispatch(self, event: Event) -> None:
        matches: list[Subscriber] = [
            s for s in self._subscribers if s.event_type == event.type or s.event_type == WILDCARD
        ]
        for sub in sorted(matches, key=lambda s: -s.priority):
            sub.callback(event.type, event.payload)
