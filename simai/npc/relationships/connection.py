"""ConnectionService — intesa cumulativa su una relazione.

L'intesa cresce con azioni di intimità di successo e decade nel tempo.
È memorizzata in `Relationship.metadata_json["connection"]`.
"""

from __future__ import annotations

from typing import Final

from simai.npc.intimacy.actions import IntimacyActionDef
from simai.npc.relationships.models import Relationship

#: Valore iniziale di connection.
INITIAL_CONNECTION: Final[float] = 0.10

#: Decremento giornaliero (decay).
DAILY_DECAY: Final[float] = 0.003

#: Gain base per azione di successo.
BASE_GAIN: Final[float] = 0.010

#: Gain extra per livello dell'azione: `+ 0.008 × level`.
GAIN_PER_LEVEL: Final[float] = 0.008

#: Cap massimo.
MAX_CONNECTION: Final[float] = 1.0

#: Connection minima per "partner consolidato".
PARTNER_CONSOLIDATED_THRESHOLD: Final[float] = 0.60


class ConnectionService:
    """Servizio stateless di gestione dell'intesa."""

    @staticmethod
    def get(rel: Relationship) -> float:
        md = rel.metadata_json or {}
        try:
            return max(0.0, min(1.0, float(md.get("connection", INITIAL_CONNECTION))))
        except (TypeError, ValueError):
            return INITIAL_CONNECTION

    @staticmethod
    def set(rel: Relationship, value: float) -> None:
        md = dict(rel.metadata_json or {})
        md["connection"] = max(0.0, min(MAX_CONNECTION, value))
        rel.metadata_json = md

    @staticmethod
    def register_action(
        rel: Relationship,
        *,
        action_def: IntimacyActionDef,
    ) -> float:
        """Registra un'azione riuscita. Ritorna la nuova connection."""
        current = ConnectionService.get(rel)
        gain = BASE_GAIN + GAIN_PER_LEVEL * action_def.level
        new = min(MAX_CONNECTION, current + gain)
        ConnectionService.set(rel, new)
        return new

    @staticmethod
    def tick_daily(rel: Relationship) -> float:
        """Applica un giorno di decay. Ritorna la nuova connection."""
        current = ConnectionService.get(rel)
        new = max(0.0, current - DAILY_DECAY)
        ConnectionService.set(rel, new)
        return new

    @staticmethod
    def label(value: float) -> str:
        if value >= PARTNER_CONSOLIDATED_THRESHOLD:
            return "consolidata"
        if value >= 0.40:
            return "in crescita"
        if value >= 0.20:
            return "emergente"
        return "iniziale"


__all__ = [
    "BASE_GAIN",
    "DAILY_DECAY",
    "GAIN_PER_LEVEL",
    "INITIAL_CONNECTION",
    "MAX_CONNECTION",
    "PARTNER_CONSOLIDATED_THRESHOLD",
    "ConnectionService",
]
