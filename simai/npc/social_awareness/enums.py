"""Enum e costanti del dominio consapevolezza sociale."""

from __future__ import annotations

from enum import StrEnum
from typing import Final

from simai.npc.traits.enums import Trait


class TraitVisibility(StrEnum):
    """Visibilità sociale di un tratto."""

    VISIBLE = "VISIBLE"  # ovvio, si scopre in poche interazioni
    MODERATE = "MODERATE"  # richiede diverse interazioni
    HIDDEN = "HIDDEN"  # difficile da scoprire


#: Mapping tratto -> visibilità.
TRAIT_VISIBILITY: Final[dict[Trait, TraitVisibility]] = {
    # VISIBLE
    Trait.SOCIALE: TraitVisibility.VISIBLE,
    Trait.TIMIDO: TraitVisibility.VISIBLE,
    Trait.ATLETICO: TraitVisibility.VISIBLE,
    Trait.SPENSIERATO: TraitVisibility.VISIBLE,
    Trait.EMOTIONALLY_EXPRESSIVE: TraitVisibility.VISIBLE,
    # MODERATE
    Trait.GENTILE: TraitVisibility.MODERATE,
    Trait.EMPATICO: TraitVisibility.MODERATE,
    Trait.CORAGGIOSO: TraitVisibility.MODERATE,
    Trait.IMPULSIVO: TraitVisibility.MODERATE,
    Trait.RIBELLE: TraitVisibility.MODERATE,
    Trait.PRATICO: TraitVisibility.MODERATE,
    Trait.OTTIMISTA: TraitVisibility.MODERATE,
    Trait.PESSIMISTA: TraitVisibility.MODERATE,
    # HIDDEN
    Trait.GENEROSO: TraitVisibility.HIDDEN,
    Trait.LEALE: TraitVisibility.HIDDEN,
    Trait.RISERVATO: TraitVisibility.HIDDEN,
    Trait.INTELLETTUALE: TraitVisibility.HIDDEN,
    Trait.CURIOSO: TraitVisibility.HIDDEN,
    Trait.RIFLESSIVO: TraitVisibility.HIDDEN,
    Trait.ORDINATO: TraitVisibility.HIDDEN,
    Trait.SOGNATORE: TraitVisibility.HIDDEN,
    Trait.ARTISTICO: TraitVisibility.HIDDEN,
    Trait.CREATIVO: TraitVisibility.HIDDEN,
    Trait.AMBIZIOSO: TraitVisibility.HIDDEN,
    Trait.PRUDENTE: TraitVisibility.HIDDEN,
    Trait.TESTARDO: TraitVisibility.HIDDEN,
    Trait.SEXUALLY_EXPLORATIVE: TraitVisibility.HIDDEN,
}

#: Probabilità base di scoperta per interazione, per visibilità.
DISCOVERY_PROBABILITY: Final[dict[TraitVisibility, float]] = {
    TraitVisibility.VISIBLE: 0.60,
    TraitVisibility.MODERATE: 0.25,
    TraitVisibility.HIDDEN: 0.08,
}

#: Incremento di confidence a scoperta riuscita.
CONFIDENCE_INCREMENT: Final[float] = 0.20

#: Confidence iniziale per parenti stretti (genitori/figli/fratelli).
FAMILY_INITIAL_CONFIDENCE: Final[float] = 0.50

#: Soglia oltre cui un tratto è considerato "conosciuto".
KNOWN_THRESHOLD: Final[float] = 1.0

#: Soglia minima per "esporre" un tratto parzialmente in CLI.
PARTIAL_THRESHOLD: Final[float] = 0.30

#: Intensità di scoperta per livello di azione.
INTENSITY_BY_LEVEL: Final[dict[int, float]] = {
    0: 0.20,
    1: 0.35,
    2: 0.55,
    3: 0.75,
    4: 0.90,
    5: 1.00,
}

#: Awareness culturale iniziale verso la propria tradizione.
OWN_CULTURE_AWARENESS: Final[float] = 1.0

#: Awareness culturale iniziale verso altre tradizioni.
OTHER_CULTURE_AWARENESS: Final[float] = 0.10

#: Incremento awareness per interazione con membro di altra cultura.
CULTURAL_LEARN_INCREMENT: Final[float] = 0.05

#: Cap awareness.
MAX_CULTURAL_AWARENESS: Final[float] = 1.0


__all__ = [
    "CONFIDENCE_INCREMENT",
    "CULTURAL_LEARN_INCREMENT",
    "DISCOVERY_PROBABILITY",
    "FAMILY_INITIAL_CONFIDENCE",
    "INTENSITY_BY_LEVEL",
    "KNOWN_THRESHOLD",
    "MAX_CULTURAL_AWARENESS",
    "OTHER_CULTURE_AWARENESS",
    "OWN_CULTURE_AWARENESS",
    "PARTIAL_THRESHOLD",
    "TRAIT_VISIBILITY",
    "TraitVisibility",
]
