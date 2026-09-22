"""Enum del dominio identità."""

from enum import StrEnum


class TabooReaction(StrEnum):
    """Reazione a tabù culturali."""

    SEVERE = "SEVERE"
    MODERATE = "MODERATE"
    LENIENT = "LENIENT"


class CulturalTradition(StrEnum):
    """Tradizioni culturali di Anthalys (lore-fixed)."""

    ANTHAL_CORE = "ANTHAL_CORE"
    NORTH_STRICT = "NORTH_STRICT"
    SOUTH_OPEN = "SOUTH_OPEN"
    MERCHANT_COAST = "MERCHANT_COAST"


#: Range di default (permissiveness, modesty, gender_role_strict, taboo)
#: per ogni tradizione. Usati per l'inizializzazione dei nuovi character.
TRADITION_RANGES: dict[CulturalTradition, tuple[float, float, float, TabooReaction]] = {
    CulturalTradition.ANTHAL_CORE: (0.55, 0.45, 0.45, TabooReaction.MODERATE),
    CulturalTradition.NORTH_STRICT: (0.30, 0.75, 0.75, TabooReaction.SEVERE),
    CulturalTradition.SOUTH_OPEN: (0.80, 0.25, 0.30, TabooReaction.LENIENT),
    CulturalTradition.MERCHANT_COAST: (0.65, 0.40, 0.20, TabooReaction.MODERATE),
}


__all__ = ["TRADITION_RANGES", "CulturalTradition", "TabooReaction"]
