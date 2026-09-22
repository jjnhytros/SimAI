"""Package `simai.npc.intimacy` — azioni di intimità e consenso."""

from simai.npc.intimacy.actions import (
    INTIMACY_CATALOG,
    IntimacyActionDef,
    get_intimacy_def,
)
from simai.npc.intimacy.consent import (
    BASE_WILLINGNESS,
    NOVELTY_PENALTY,
    NOVELTY_WINDOW_TICKS,
    REJECTION_COOLDOWN_TICKS,
    REJECTION_PENALTY,
    TRAIT_WILLINGNESS_MODIFIERS,
    ConsentResult,
    ConsentService,
)
from simai.npc.intimacy.enums import IntimacyAction, IntimacyOutcome
from simai.npc.intimacy.service import IntimacyResult, IntimacyService

__all__ = [
    "BASE_WILLINGNESS",
    "INTIMACY_CATALOG",
    "NOVELTY_PENALTY",
    "NOVELTY_WINDOW_TICKS",
    "REJECTION_COOLDOWN_TICKS",
    "REJECTION_PENALTY",
    "TRAIT_WILLINGNESS_MODIFIERS",
    "ConsentResult",
    "ConsentService",
    "IntimacyAction",
    "IntimacyActionDef",
    "IntimacyOutcome",
    "IntimacyResult",
    "IntimacyService",
    "get_intimacy_def",
]
