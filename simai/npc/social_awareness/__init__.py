"""Package `simai.npc.social_awareness` — scoperta tratti + awareness culturale."""

from simai.npc.social_awareness.enums import (
    CONFIDENCE_INCREMENT,
    CULTURAL_LEARN_INCREMENT,
    DISCOVERY_PROBABILITY,
    FAMILY_INITIAL_CONFIDENCE,
    INTENSITY_BY_LEVEL,
    KNOWN_THRESHOLD,
    MAX_CULTURAL_AWARENESS,
    OTHER_CULTURE_AWARENESS,
    OWN_CULTURE_AWARENESS,
    PARTIAL_THRESHOLD,
    TRAIT_VISIBILITY,
    TraitVisibility,
)
from simai.npc.social_awareness.service import (
    SocialAwarenessService,
    TraitDiscoveryResult,
)

__all__ = [
    "CONFIDENCE_INCREMENT",
    "CULTURAL_LEARN_INCREMENT",
    "DISCOVERY_PROBABILITY",
    "FAMILY_INITIAL_CONFIDENCE",
    "INTENSITY_BY_LEVEL",
    "KNOWN_THRESHOLD",
    "MAX_CULTURAL_AWARENESS",
    "OTHER_CULTURE_AWARENESS",
    "OWN_CULTURE_AWARENESS",
    "PARTIAL_THRESHOLD",
    "TRAIT_VISIBILITY",
    "SocialAwarenessService",
    "TraitDiscoveryResult",
    "TraitVisibility",
]
