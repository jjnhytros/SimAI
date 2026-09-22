"""Enum del dominio relazioni."""

from enum import StrEnum


class RelationshipKind(StrEnum):
    """Tipo di relazione tra due Character.

    - `PARENT_OF`, `MENTOR_OF`: **dirette** (from -> to ha un ruolo).
      Memorizzate una sola volta.
    - Tutte le altre: **simmetriche**. Memorizzate come due righe speculari
      (from→to e to→from) per query uniformi.
    """

    # Famiglia (diretta)
    PARENT_OF = "PARENT_OF"

    # Partner (simmetriche)
    SPOUSE_OF = "SPOUSE_OF"
    PARTNER_OF = "PARTNER_OF"
    EX_PARTNER_OF = "EX_PARTNER_OF"

    # Sociali (simmetriche)
    FRIEND_OF = "FRIEND_OF"
    BEST_FRIEND_OF = "BEST_FRIEND_OF"
    ACQUAINTANCE_OF = "ACQUAINTANCE_OF"
    RIVAL_OF = "RIVAL_OF"
    ENEMY_OF = "ENEMY_OF"
    COLLEAGUE_OF = "COLLEAGUE_OF"

    # Mentorship (diretta)
    MENTOR_OF = "MENTOR_OF"

    @property
    def is_symmetric(self) -> bool:
        """``True`` se la relazione è simmetrica (memorizzata in entrambe le direzioni)."""
        return self is not RelationshipKind.PARENT_OF and self is not RelationshipKind.MENTOR_OF

    @property
    def is_family(self) -> bool:
        """``True`` se la relazione è di tipo familiare."""
        return self is RelationshipKind.PARENT_OF


#: Insiemi pre-calcolati per le query.
SYMMETRIC_KINDS: frozenset[RelationshipKind] = frozenset(
    k for k in RelationshipKind if k.is_symmetric
)
DIRECTED_KINDS: frozenset[RelationshipKind] = frozenset(
    k for k in RelationshipKind if not k.is_symmetric
)


__all__ = [
    "DIRECTED_KINDS",
    "SYMMETRIC_KINDS",
    "RelationshipKind",
]
