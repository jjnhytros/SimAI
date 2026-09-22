"""Package `simai.npc.socialization` — creazione automatica relazioni."""

from simai.npc.socialization.enums import (
    DAILY_EVAL_PROBABILITY,
    INITIAL_FRIEND_STRENGTH,
    INITIAL_PARTNER_STRENGTH,
    MAX_NEW_RELATIONS_PER_DAY,
    MIN_AGE_FOR_PARTNER,
    MIN_COMPATIBILITY_FOR_PARTNER,
    MIN_DESIRE_FOR_PARTNER,
    MIN_OPINION_BEST_FRIEND,
    MIN_OPINION_FRIEND,
    MIN_OPINION_PARTNER,
    PARTNER_PROBABILITY,
    UPGRADE_PROBABILITY,
    SocializationAction,
)
from simai.npc.socialization.service import (
    SocializationReport,
    SocializationService,
)

__all__ = [
    "DAILY_EVAL_PROBABILITY",
    "INITIAL_FRIEND_STRENGTH",
    "INITIAL_PARTNER_STRENGTH",
    "MAX_NEW_RELATIONS_PER_DAY",
    "MIN_AGE_FOR_PARTNER",
    "MIN_COMPATIBILITY_FOR_PARTNER",
    "MIN_DESIRE_FOR_PARTNER",
    "MIN_OPINION_BEST_FRIEND",
    "MIN_OPINION_FRIEND",
    "MIN_OPINION_PARTNER",
    "PARTNER_PROBABILITY",
    "UPGRADE_PROBABILITY",
    "SocializationAction",
    "SocializationReport",
    "SocializationService",
]
