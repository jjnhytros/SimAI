"""Package `simai.npc.memory` — memorie degli NPC."""

from simai.npc.memory.enums import DECAY_RATES, MIN_SALIENCY, MemoryKind
from simai.npc.memory.models import Memory
from simai.npc.memory.saliency import (
    BASE_SALIENCY,
    CRITICAL_NEED_BOOST,
    LIFECYCLE_BOOST,
    SOCIAL_EVENT_BOOST,
    STRONG_MOODLET_BOOST,
    compute_saliency,
)
from simai.npc.memory.service import MemoryService, RecallResult

__all__ = [
    "BASE_SALIENCY",
    "CRITICAL_NEED_BOOST",
    "DECAY_RATES",
    "LIFECYCLE_BOOST",
    "MIN_SALIENCY",
    "SOCIAL_EVENT_BOOST",
    "STRONG_MOODLET_BOOST",
    "Memory",
    "MemoryKind",
    "MemoryService",
    "RecallResult",
    "compute_saliency",
]
