"""Enum del dominio reputazione."""

from __future__ import annotations

from enum import StrEnum
from typing import Final


class GossipTopic(StrEnum):
    """Tema di un pettegolezzo."""

    ACHIEVEMENT = "ACHIEVEMENT"
    ROMANCE = "ROMANCE"
    SCANDAL = "SCANDAL"
    TABOO = "TABOO"
    CRIME = "CRIME"
    GENEROSITY = "GENEROSITY"
    INCOMPETENCE = "INCOMPETENCE"
    RUMOR = "RUMOR"


#: Range di sentiment di default per ogni topic (min, max).
TOPIC_SENTIMENTS: Final[dict[GossipTopic, tuple[float, float]]] = {
    GossipTopic.ACHIEVEMENT: (0.4, 0.9),
    GossipTopic.ROMANCE: (0.2, 0.7),
    GossipTopic.SCANDAL: (-0.9, -0.4),
    GossipTopic.TABOO: (-1.0, -0.7),
    GossipTopic.CRIME: (-1.0, -0.6),
    GossipTopic.GENEROSITY: (0.5, 0.9),
    GossipTopic.INCOMPETENCE: (-0.6, -0.2),
    GossipTopic.RUMOR: (-0.3, 0.3),
}

#: Soglia di coefficiente di relazione per considerare consanguinei.
CONSANGUINITY_THRESHOLD: Final[float] = 0.125

#: Soglia opinion sotto cui un character è considerato "nemico potenziale".
OPINION_NEGATIVE_THRESHOLD: Final[float] = -30.0

#: Soglia opinion sopra cui un character è considerato "amico".
OPINION_POSITIVE_THRESHOLD: Final[float] = 30.0


__all__ = [
    "CONSANGUINITY_THRESHOLD",
    "OPINION_NEGATIVE_THRESHOLD",
    "OPINION_POSITIVE_THRESHOLD",
    "TOPIC_SENTIMENTS",
    "GossipTopic",
]
