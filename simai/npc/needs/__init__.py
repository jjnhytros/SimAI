"""Package `simai.npc.needs` — bisogni e loro decadimento."""

from simai.npc.needs.enums import NeedState, NeedType
from simai.npc.needs.needs import DEFAULT_NEED_VALUE, Needs
from simai.npc.needs.processor import (
    DEFAULT_DECAY_RATES,
    NeedsProcessor,
    NeedTransition,
)
from simai.npc.needs.thresholds import (
    CRITICAL_THRESHOLD,
    HIGH_THRESHOLD,
    LOW_THRESHOLD,
    MAX_NEED_VALUE,
    MIN_NEED_VALUE,
    state_of,
)

__all__ = [
    "CRITICAL_THRESHOLD",
    "DEFAULT_DECAY_RATES",
    "DEFAULT_NEED_VALUE",
    "HIGH_THRESHOLD",
    "LOW_THRESHOLD",
    "MAX_NEED_VALUE",
    "MIN_NEED_VALUE",
    "NeedState",
    "NeedTransition",
    "NeedType",
    "Needs",
    "NeedsProcessor",
    "state_of",
]
