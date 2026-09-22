"""Package `simai.npc.background` — eventi formativi del passato."""

from simai.npc.background.enums import (
    BULLY_TIMID_THRESHOLD,
    MAX_FORMATIVE_AGE_YEARS,
    MAX_SEED_EVENTS,
    MEMORY_THRESHOLD,
    SEVERITY_RANGES,
    FormativeEventKind,
)
from simai.npc.background.models import FormativeEvent
from simai.npc.background.service import BackgroundService, SeedEvent

__all__ = [
    "BULLY_TIMID_THRESHOLD",
    "MAX_FORMATIVE_AGE_YEARS",
    "MAX_SEED_EVENTS",
    "MEMORY_THRESHOLD",
    "SEVERITY_RANGES",
    "BackgroundService",
    "FormativeEvent",
    "FormativeEventKind",
    "SeedEvent",
]
