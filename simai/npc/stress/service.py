"""StressService — calcola lo stress di un Character da fattori multipli."""

from __future__ import annotations

from typing import Final

from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.config.anthalys import SECONDS_PER_DAY
from simai.core.anthalys_datetime import AnthalysDateTime
from simai.npc.identity import IdentityService
from simai.npc.models import Character
from simai.npc.mood import MoodState
from simai.npc.needs.enums import NeedState, NeedType
from simai.npc.needs.needs import Needs
from simai.npc.relationships.models import Relationship
from simai.npc.stress.models import StressFactors

#: Pesi dei fattori di stress (somma = 1.0).
STRESS_WEIGHTS: Final[dict[str, float]] = {
    "critical_needs_fraction": 0.35,
    "low_mood": 0.20,
    "high_inhibition": 0.15,
    "recent_rejection": 0.10,
    "poverty": 0.10,
    "fatigue": 0.10,
}

#: Finestra (giorni) per il fattore "rifiuto recente".
REJECTION_WINDOW_DAYS: Final[int] = 3

#: Soglia di bilancio sotto cui scatta il fattore povertà.
POVERTY_THRESHOLD: Final[int] = 100


class StressService:
    """Servizio stateless di calcolo dello stress."""

    @staticmethod
    def compute(
        session: Session,
        character: Character,
        current_dt: AnthalysDateTime,
    ) -> tuple[float, StressFactors]:
        """Ritorna `(stress, factors)` con stress in [0, 1]."""
        needs = Needs.from_dict(character.needs_json or {})
        mood = MoodState.from_dict(character.mood_json or {})
        sep = IdentityService.get_sep(character)

        # Fattore 1: bisogni critici
        critical_count = sum(1 for n in NeedType if needs.state(n) is NeedState.CRITICAL)
        critical_frac = critical_count / len(list(NeedType))

        # Fattore 2: mood basso
        low_mood = max(0.0, (0.4 - mood.happiness) / 0.4)

        # Fattore 3: inibizione alta
        high_inh = max(0.0, (sep.inhibition - 0.7) / 0.3)

        # Fattore 4: rifiuto recente
        recent_rej = StressService._recent_rejection_factor(session, character.id, current_dt)

        # Fattore 5: povertà
        balance = int(character.athel_balance)
        if balance < POVERTY_THRESHOLD:
            poverty = (POVERTY_THRESHOLD - balance) / POVERTY_THRESHOLD
        else:
            poverty = 0.0

        # Fattore 6: fatica
        fatigue = max(0.0, (30.0 - needs.get(NeedType.ENERGY)) / 30.0)

        factors = StressFactors(
            critical_needs_fraction=critical_frac,
            low_mood=low_mood,
            high_inhibition=high_inh,
            recent_rejection=recent_rej,
            poverty=poverty,
            fatigue=fatigue,
        )

        stress = sum(
            STRESS_WEIGHTS.get(name, 0.0) * getattr(factors, name) for name in STRESS_WEIGHTS
        )
        return max(0.0, min(1.0, stress)), factors

    @staticmethod
    def _recent_rejection_factor(
        session: Session,
        character_id: int,
        current_dt: AnthalysDateTime,
    ) -> float:
        """1.0 se c'è stato un rifiuto negli ultimi N giorni, 0.0 altrimenti.

        Considera solo relazioni uscenti dal character.
        """
        cutoff_secs = current_dt.to_total_seconds() - REJECTION_WINDOW_DAYS * SECONDS_PER_DAY
        rows = session.scalars(
            select(Relationship).where(Relationship.from_id == character_id)
        ).all()
        for rel in rows:
            md = rel.metadata_json or {}
            last = md.get("last_rejection_at")
            if isinstance(last, (int, float)) and last >= cutoff_secs:
                return 1.0
        return 0.0


__all__ = [
    "POVERTY_THRESHOLD",
    "REJECTION_WINDOW_DAYS",
    "STRESS_WEIGHTS",
    "StressService",
]
