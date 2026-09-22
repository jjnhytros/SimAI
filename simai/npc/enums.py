"""Enum del dominio NPC."""

from enum import StrEnum


class Sex(StrEnum):
    """Sesso biologico del personaggio."""

    MALE = "male"
    FEMALE = "female"
    INTERSEX = "intersex"


class LifeStagePediatric(StrEnum):
    """Fasce di età pediatriche e adolescenziali (PARTE II §II.1)."""

    NEONATAL = "NEONATAL"
    INFANT = "INFANT"
    EARLY_CHILDHOOD = "EARLY_CHILDHOOD"
    MIDDLE_CHILDHOOD = "MIDDLE_CHILDHOOD"
    LATE_CHILDHOOD = "LATE_CHILDHOOD"
    PUBERTY_ADOLESCENCE = "PUBERTY_ADOLESCENCE"


class LifeStagePsychosocial(StrEnum):
    """Fasce di età psicosociali (PARTE II §II.2)."""

    PRENATAL = "PRENATAL"
    EARLY_INFANCY = "EARLY_INFANCY"
    INFANCY = "INFANCY"
    MIDDLE_INFANCY = "MIDDLE_INFANCY"
    ADOLESCENCE = "ADOLESCENCE"
    YOUTH = "YOUTH"
    ADULTHOOD = "ADULTHOOD"
    OLD_AGE = "OLD_AGE"


__all__ = ["LifeStagePediatric", "LifeStagePsychosocial", "Sex"]
