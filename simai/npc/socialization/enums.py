"""Enum e costanti del dominio socializzazione."""

from __future__ import annotations

from enum import StrEnum
from typing import Final


class SocializationAction(StrEnum):
    """Esito di un tentativo di socializzazione."""

    BECAME_FRIEND = "BECAME_FRIEND"
    BECAME_BEST_FRIEND = "BECAME_BEST_FRIEND"
    BECAME_PARTNER = "BECAME_PARTNER"
    UPGRADED = "UPGRADED"
    NO_CHANGE = "NO_CHANGE"


#: Opinion minima per considerare di formare amicizia.
MIN_OPINION_FRIEND: Final[float] = 15.0

#: Opinion minima per best friend.
MIN_OPINION_BEST_FRIEND: Final[float] = 45.0

#: Opinion minima per partner (con desire alto).
MIN_OPINION_PARTNER: Final[float] = 25.0

#: Probabilità giornaliera di valutare un nuovo legame.
DAILY_EVAL_PROBABILITY: Final[float] = 0.20

#: Probabilità giornaliera di upgrade FRIEND -> BEST_FRIEND.
UPGRADE_PROBABILITY: Final[float] = 0.10

#: Probabilità giornaliera di FRIEND/PARTNER (dato opinion + desire + compatibility).
PARTNER_PROBABILITY: Final[float] = 0.05

#: Numero massimo di nuove relazioni create per giorno (cap globale).
MAX_NEW_RELATIONS_PER_DAY: Final[int] = 3

#: Soglia di compatibility per partner.
MIN_COMPATIBILITY_FOR_PARTNER: Final[float] = 0.55

#: Soglia di desire per partner.
MIN_DESIRE_FOR_PARTNER: Final[float] = 0.55

#: Soglia minima di età per partner.
MIN_AGE_FOR_PARTNER: Final[int] = 14

#: Strength iniziale di una nuova amicizia.
INITIAL_FRIEND_STRENGTH: Final[float] = 0.45

#: Strength iniziale di un partner.
INITIAL_PARTNER_STRENGTH: Final[float] = 0.55


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
]
