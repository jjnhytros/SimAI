"""IntergenerationalService — relazioni tra generazioni.

Fattori:
  - opinion boost basato su gap età (i giovani ammirano gli anziani)
  - rispetto per ruolo (nonno/nonno)
  - trasmissione valori già in MentorshipService
"""

from __future__ import annotations

from typing import Final

from sqlalchemy.orm import Session

from simai.config.anthalys import SECONDS_PER_YEAR
from simai.core.anthalys_datetime import AnthalysDateTime
from simai.npc.models import Character

#: Bonus opinion da gap età (per decade di differenza).
OPINION_BONUS_PER_DECADE: Final[float] = 2.0

#: Cap del bonus.
MAX_OPINION_BONUS: Final[float] = 15.0

#: Soglia di gap età per considerare due character "intergenerazionali".
MIN_GAP_YEARS: Final[int] = 20


class IntergenerationalService:
    """Servizio stateless di dinamiche intergenerazionali."""

    @staticmethod
    def age_gap_years(a: Character, b: Character, current_dt: AnthalysDateTime) -> int:
        age_a = (current_dt.to_total_seconds() - a.birth_total_seconds) // SECONDS_PER_YEAR
        age_b = (current_dt.to_total_seconds() - b.birth_total_seconds) // SECONDS_PER_YEAR
        return abs(int(age_a) - int(age_b))

    @staticmethod
    def opinion_bonus(a: Character, b: Character, current_dt: AnthalysDateTime) -> float:
        """Bonus opinion basato su gap età. 0 se < MIN_GAP_YEARS."""
        gap = IntergenerationalService.age_gap_years(a, b, current_dt)
        if gap < MIN_GAP_YEARS:
            return 0.0
        decades = gap / 10.0
        bonus = decades * OPINION_BONUS_PER_DECADE
        return min(MAX_OPINION_BONUS, bonus)

    @staticmethod
    def family_role_label(session: Session, a: Character, b: Character) -> str:
        """Etichetta del ruolo familiare (per CLI)."""
        from simai.npc.relationships.kinship import relationship_name

        return relationship_name(session, a.id, b.id)

    @staticmethod
    def apply_family_opinion_boost(
        session: Session,
        *,
        current_dt: AnthalysDateTime,
    ) -> int:
        """Applica un piccolo bonus di opinion basato su ruolo familiare.

        Chiamato dal LifecycleManager nel daily work.
        Ritorna il numero di opinion aggiornate.
        """
        # Applica solo a parenti stretti (r >= 0.25)
        from sqlalchemy import select

        from simai.npc.relationships.models import Relationship
        from simai.npc.reputation import ReputationService

        count = 0
        rels = session.scalars(
            select(Relationship).where(
                Relationship.kind == "PARENT_OF",
            )
        ).all()
        for rel in rels:
            parent = session.get(Character, rel.from_id)
            child = session.get(Character, rel.to_id)
            if parent is None or child is None:
                continue
            if not parent.is_alive or not child.is_alive:
                continue
            bonus = IntergenerationalService.opinion_bonus(parent, child, current_dt)
            if bonus > 0:
                ReputationService.update_opinion(
                    session,
                    observer_id=child.id,
                    target_id=parent.id,
                    delta=bonus * 0.1,  # piccolo incremento giornaliero
                    current_dt=current_dt,
                )
                count += 1
        return count


__all__ = [
    "MAX_OPINION_BONUS",
    "MIN_GAP_YEARS",
    "OPINION_BONUS_PER_DECADE",
    "IntergenerationalService",
]
