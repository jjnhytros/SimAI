"""Package `simai.npc.reflection` — diario, riflessione, narrazione, crisi."""

from simai.npc.reflection.crisis import CrisisService, CrisisStatus
from simai.npc.reflection.enums import (
    MIN_CRISIS_DURATION_DAYS,
    NEGATIVE_STREAK_FOR_CRISIS,
    REFLECTION_INTERVAL_DAYS,
    STRESS_CRISIS_THRESHOLD,
    CrisisPhase,
    ReflectionKind,
)
from simai.npc.reflection.models import ReflectionEntry
from simai.npc.reflection.narrative import (
    LifeChapter,
    LifeNarrative,
    LifeNarrativeService,
)
from simai.npc.reflection.service import ReflectionResult, ReflectionService
from simai.npc.reflection.templates import compose_reflection

__all__ = [
    "MIN_CRISIS_DURATION_DAYS",
    "NEGATIVE_STREAK_FOR_CRISIS",
    "REFLECTION_INTERVAL_DAYS",
    "STRESS_CRISIS_THRESHOLD",
    "CrisisPhase",
    "CrisisService",
    "CrisisStatus",
    "LifeChapter",
    "LifeNarrative",
    "LifeNarrativeService",
    "ReflectionEntry",
    "ReflectionKind",
    "ReflectionResult",
    "ReflectionService",
    "compose_reflection",
]
