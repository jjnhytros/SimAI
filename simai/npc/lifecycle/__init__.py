"""Package `simai.npc.lifecycle` — aging, morte, gravidanza, famiglia."""

from simai.npc.lifecycle.aging import AgeTransition, AgingService
from simai.npc.lifecycle.death import DeathService
from simai.npc.lifecycle.enums import DeathCause, PregnancyStatus
from simai.npc.lifecycle.family_ai import (
    BASE_DAILY_PROBABILITY,
    COUPLE_KINDS,
    FAMILY_TRAITS,
    MIN_BIRTH_GAP_DAYS,
    MIN_COUPLE_STRENGTH,
    ConceptionEvaluation,
    FamilyAI,
)
from simai.npc.lifecycle.manager import LifecycleManager, LifecycleReport
from simai.npc.lifecycle.pregnancy import (
    DEFAULT_CONCEPTION_PROBABILITY,
    GESTATION_DAYS,
    MAX_FEMALE_FERTILE_AGE_YEARS,
    MAX_MALE_FERTILE_AGE_YEARS,
    MIN_FERTILE_AGE_YEARS,
    ConceptionResult,
    Pregnancy,
    PregnancyService,
)
from simai.npc.lifecycle.succession import (
    MAX_GUARDIAN_SEARCH_DEPTH,
    MINOR_AGE_YEARS,
    OrphanInfo,
    SuccessionService,
)

__all__ = [
    "BASE_DAILY_PROBABILITY",
    "COUPLE_KINDS",
    "DEFAULT_CONCEPTION_PROBABILITY",
    "FAMILY_TRAITS",
    "GESTATION_DAYS",
    "MAX_FEMALE_FERTILE_AGE_YEARS",
    "MAX_GUARDIAN_SEARCH_DEPTH",
    "MAX_MALE_FERTILE_AGE_YEARS",
    "MINOR_AGE_YEARS",
    "MIN_BIRTH_GAP_DAYS",
    "MIN_COUPLE_STRENGTH",
    "MIN_FERTILE_AGE_YEARS",
    "AgeTransition",
    "AgingService",
    "ConceptionEvaluation",
    "ConceptionResult",
    "DeathCause",
    "DeathService",
    "FamilyAI",
    "LifecycleManager",
    "LifecycleReport",
    "OrphanInfo",
    "Pregnancy",
    "PregnancyService",
    "PregnancyStatus",
    "SuccessionService",
]
