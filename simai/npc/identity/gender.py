"""Gender identity — enum + helper."""

from __future__ import annotations

from enum import StrEnum
from typing import Final

from simai.npc.identity.models import Sexuality


class GenderIdentity(StrEnum):
    """Identità di genere."""

    MAN = "man"
    WOMAN = "woman"
    NONBINARY = "nonbinary"
    GENDERFLUID = "genderfluid"
    AGENDER = "agender"


#: Valori legacy accettati (per retro-compatibilità con `Character.gender`).
_LEGACY_MAP: Final[dict[str, GenderIdentity]] = {
    "unspecified": GenderIdentity.NONBINARY,
    "man": GenderIdentity.MAN,
    "woman": GenderIdentity.WOMAN,
    "nonbinary": GenderIdentity.NONBINARY,
    "genderfluid": GenderIdentity.GENDERFLUID,
    "agender": GenderIdentity.AGENDER,
}


def parse_gender(value: str) -> GenderIdentity:
    """Parse di una stringa in `GenderIdentity`, con fallback."""
    try:
        return GenderIdentity(value)
    except ValueError:
        return _LEGACY_MAP.get(value, GenderIdentity.NONBINARY)


def is_cisgender(gender: str, sex: str) -> bool:
    """``True`` se gender e sex sono coerenti (cis)."""
    g = parse_gender(gender)
    return (sex == "male" and g is GenderIdentity.MAN) or (
        sex == "female" and g is GenderIdentity.WOMAN
    )


def is_heterosexual(sex: str, sexuality: Sexuality) -> bool:
    """``True`` se la sexuality è "etero" rispetto al sex biologico."""
    if sex == "male":
        return sexuality.attraction_to_female > sexuality.attraction_to_male
    if sex == "female":
        return sexuality.attraction_to_male > sexuality.attraction_to_female
    return False


__all__ = [
    "GenderIdentity",
    "is_cisgender",
    "is_heterosexual",
    "parse_gender",
]
