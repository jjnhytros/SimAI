"""SimulationLoop — orchestrazione del tick di simulazione.

Non è un singleton. Ogni istanza riceve le dipendenze via costruttore:

    loop = SimulationLoop(
        time_manager=TimeManager(...),
        event_bus=EventBus(),
        npc_manager=None,       # opzionale (FASE 3)
        world_manager=None,     # opzionale (FASE 4)
    )
    loop.run_for(1000)

I manager sono tipizzati con `Protocol` strutturali: nessun import coupling
verso `simai.npc` o `simai.world`, che arriveranno in fasi successive.
"""

from __future__ import annotations

import time as _time
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from loguru import logger

from simai.core.event_bus import EventBus
from simai.core.time_manager import TimeManager


@runtime_checkable
class NPCManagerLike(Protocol):
    """Protocollo strutturale per un NPC manager (FASE 3)."""

    def update_all_npcs(self) -> None: ...

    def count(self) -> int: ...


@runtime_checkable
class WorldManagerLike(Protocol):
    """Protocollo strutturale per un World manager (FASE 4)."""

    def update_environment(self) -> None: ...

    def update_state(self) -> None: ...


@dataclass(frozen=True, slots=True)
class TickReport:
    """Report di un singolo tick."""

    tick_index: int
    duration_ms: float
    time_advanced_to: str
    events_processed: int
    npcs_updated: int


class SimulationLoop:
    """Loop di simulazione headless.

    Sequenza di un tick (da TODO §1.1):
      1. ``time_manager.advance_tick()``
      2. ``world_manager.update_environment()``  (se presente)
      3. ``npc_manager.update_all_npcs()``       (se presente)
      4. ``event_bus.process_queue()``
      5. ``world_manager.update_state()``        (se presente)

    Stato interno (non persistente — la persistenza arriva in Chunk 1.2):
      - ``tick_index``  : contatore progressivo
      - ``paused``      : se True, ``tick()`` ritorna None
      - ``speed``       : metadata di velocità (non impatta il loop,
                          il pacing reale è responsabilità del chiamante)
      - ``history``     : ultimi N `TickReport` (ring buffer)
    """

    def __init__(
        self,
        time_manager: TimeManager,
        event_bus: EventBus | None = None,
        npc_manager: NPCManagerLike | None = None,
        world_manager: WorldManagerLike | None = None,
        perf_threshold_ms: float = 100.0,
        history_max: int = 1000,
    ) -> None:
        if perf_threshold_ms <= 0:
            raise ValueError(f"perf_threshold_ms deve essere > 0, ricevuto {perf_threshold_ms}")
        if history_max < 1:
            raise ValueError(f"history_max deve essere >= 1, ricevuto {history_max}")

        self._time_manager = time_manager
        self._event_bus = event_bus if event_bus is not None else EventBus()
        self._npc_manager = npc_manager
        self._world_manager = world_manager
        self._perf_threshold_ms = perf_threshold_ms
        self._history_max = history_max

        self._tick_index: int = 0
        self._paused: bool = False
        self._speed: float = 1.0
        self._history: list[TickReport] = []

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def time_manager(self) -> TimeManager:
        return self._time_manager

    @property
    def event_bus(self) -> EventBus:
        return self._event_bus

    @property
    def npc_manager(self) -> NPCManagerLike | None:
        return self._npc_manager

    @property
    def world_manager(self) -> WorldManagerLike | None:
        return self._world_manager

    @property
    def tick_index(self) -> int:
        return self._tick_index

    @property
    def paused(self) -> bool:
        return self._paused

    @property
    def speed(self) -> float:
        return self._speed

    @property
    def history(self) -> tuple[TickReport, ...]:
        """Snapshot immutabile della history dei tick."""
        return tuple(self._history)

    @property
    def last_report(self) -> TickReport | None:
        return self._history[-1] if self._history else None

    # ------------------------------------------------------------------
    # Control
    # ------------------------------------------------------------------

    def pause(self) -> None:
        """Mette in pausa il loop."""
        self._paused = True

    def resume(self) -> None:
        """Riprende il loop."""
        self._paused = False

    def set_speed(self, speed: float) -> None:
        """Imposta la velocità (metadata). Accetta solo valori > 0."""
        if speed <= 0:
            raise ValueError(f"speed deve essere > 0, ricevuto {speed}")
        self._speed = speed

    def reset(self) -> None:
        """Resetta contatore, pausa, velocità e history (non il tempo)."""
        self._tick_index = 0
        self._paused = False
        self._speed = 1.0
        self._history.clear()

    # ------------------------------------------------------------------
    # Tick
    # ------------------------------------------------------------------

    def tick(self) -> TickReport | None:
        """Esegue un singolo tick. Ritorna ``None`` se in pausa."""
        if self._paused:
            return None

        t0 = _time.perf_counter()
        self._tick_index += 1

        # 1. Tempo
        self._time_manager.advance_tick()
        now = self._time_manager.current

        # 2. Ambiente
        if self._world_manager is not None:
            self._world_manager.update_environment()

        # 3. NPC
        npcs_updated = 0
        if self._npc_manager is not None:
            self._npc_manager.update_all_npcs()
            npcs_updated = self._npc_manager.count()

        # 4. Eventi
        events_processed = self._event_bus.process_queue()

        # 5. Stato mondo
        if self._world_manager is not None:
            self._world_manager.update_state()

        duration_ms = (_time.perf_counter() - t0) * 1000.0
        if duration_ms > self._perf_threshold_ms:
            logger.warning(
                "Tick {} durato {:.2f} ms (soglia {} ms)",
                self._tick_index,
                duration_ms,
                self._perf_threshold_ms,
            )

        report = TickReport(
            tick_index=self._tick_index,
            duration_ms=duration_ms,
            time_advanced_to=str(now),
            events_processed=events_processed,
            npcs_updated=npcs_updated,
        )
        self._history.append(report)
        if len(self._history) > self._history_max:
            self._history.pop(0)
        return report

    def run_for(self, num_ticks: int) -> int:
        """Esegue fino a ``num_ticks`` tick. Ritorna il numero eseguito.

        Si interrompe prima se il loop è messo in pausa durante l'esecuzione.
        """
        if num_ticks < 0:
            raise ValueError(f"num_ticks deve essere >= 0, ricevuto {num_ticks}")
        count = 0
        for _ in range(num_ticks):
            if self._paused:
                break
            self.tick()
            count += 1
        return count
