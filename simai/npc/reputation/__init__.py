"""Package `simai.npc.reputation` — opinioni, gossip, taboo consanguineità."""

from simai.npc.reputation.enums import (
    CONSANGUINITY_THRESHOLD,
    OPINION_NEGATIVE_THRESHOLD,
    OPINION_POSITIVE_THRESHOLD,
    TOPIC_SENTIMENTS,
    GossipTopic,
)
from simai.npc.reputation.models import GossipEvent, Opinion
from simai.npc.reputation.service import GossipResult, ReputationService

__all__ = [
    "CONSANGUINITY_THRESHOLD",
    "OPINION_NEGATIVE_THRESHOLD",
    "OPINION_POSITIVE_THRESHOLD",
    "TOPIC_SENTIMENTS",
    "GossipEvent",
    "GossipResult",
    "GossipTopic",
    "Opinion",
    "ReputationService",
]
