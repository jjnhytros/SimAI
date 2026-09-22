"""Core simulation engine di SimAI (range migrazioni 5000-5099).

Conterrà:
  - `AnthalysDateTime`, `AnthalysCalendar` — primitive tempo Anthalys
  - `TimeManager` — gestore del tempo simulazione
  - `EventBus` — bus di eventi di dominio
  - `LODLevel`, `lod_from_distance` — level of detail
  - `SimulationLoop`, `TickReport` — orchestrazione tick
  - `SaveManager` (Chunk 1.2)
  - `Location`, `GameObject` (Chunk 1.3)
"""

from simai.core.anthalys_calendar import AnthalysCalendar
from simai.core.anthalys_datetime import AnthalysDateTime
from simai.core.event_bus import (
    WILDCARD,
    Event,
    EventBus,
    EventCallback,
    EventPayload,
    Subscriber,
)
from simai.core.lod import (
    FULL_DISTANCE_THRESHOLD,
    REDUCED_DISTANCE_THRESHOLD,
    LODLevel,
    lod_from_distance,
)
from simai.core.save_manager import (
    FILE_FORMAT_VERSION,
    MAGIC,
    SaveError,
    SaveFormatError,
    SaveInfo,
    SaveManager,
    SaveNotFoundError,
    SimulationState,
)
from simai.core.simulation_loop import (
    NPCManagerLike,
    SimulationLoop,
    TickReport,
    WorldManagerLike,
)
from simai.core.time_enums import DayPhase, Season
from simai.core.time_manager import (
    EVENT_DAY_CHANGED,
    EVENT_HOUR_CHANGED,
    EVENT_MONTH_CHANGED,
    EVENT_PHASE_CHANGED,
    EVENT_SEASON_CHANGED,
    EVENT_TICK,
    EVENT_YEAR_CHANGED,
    TimeManager,
)

__all__ = [
    "EVENT_DAY_CHANGED",
    "EVENT_HOUR_CHANGED",
    "EVENT_MONTH_CHANGED",
    "EVENT_PHASE_CHANGED",
    "EVENT_SEASON_CHANGED",
    "EVENT_TICK",
    "EVENT_YEAR_CHANGED",
    "FILE_FORMAT_VERSION",
    "FULL_DISTANCE_THRESHOLD",
    "MAGIC",
    "REDUCED_DISTANCE_THRESHOLD",
    "WILDCARD",
    "AnthalysCalendar",
    "AnthalysDateTime",
    "DayPhase",
    "Event",
    "EventBus",
    "EventCallback",
    "EventPayload",
    "LODLevel",
    "NPCManagerLike",
    "SaveError",
    "SaveFormatError",
    "SaveInfo",
    "SaveManager",
    "SaveNotFoundError",
    "Season",
    "SimulationLoop",
    "SimulationState",
    "Subscriber",
    "TickReport",
    "TimeManager",
    "WorldManagerLike",
    "lod_from_distance",
]
