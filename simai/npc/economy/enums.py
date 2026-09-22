"""Enum del dominio economico."""

from enum import StrEnum


class InheritanceTier(StrEnum):
    """Priorità di un erede nella successione materiale.

    Ordine decrescente di priorità:
      SPOUSE -> CHILD -> PARENT -> SIBLING -> OTHER
    """

    SPOUSE = "SPOUSE"
    CHILD = "CHILD"
    PARENT = "PARENT"
    SIBLING = "SIBLING"
    OTHER = "OTHER"

    @property
    def priority(self) -> int:
        """Priorità numerica (0 = massima)."""
        return _TIER_PRIORITY[self]


_TIER_PRIORITY: dict["InheritanceTier", int] = {
    InheritanceTier.SPOUSE: 0,
    InheritanceTier.CHILD: 1,
    InheritanceTier.PARENT: 2,
    InheritanceTier.SIBLING: 3,
    InheritanceTier.OTHER: 4,
}


__all__ = ["InheritanceTier"]
