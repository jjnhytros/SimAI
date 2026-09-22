"""Definizioni dei tratti: famiglia, soglia, modificatori di utility.

`TRAIT_DEFS` è il punto unico di verità per le proprietà di ogni tratto.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final

from simai.npc.ai.enums import ActionType
from simai.npc.traits.enums import Aspiration, Trait, TraitCategory, TraitFamily


@dataclass(frozen=True, slots=True)
class TraitDef:
    """Definizione di un tratto."""

    trait: Trait
    category: TraitCategory
    family: TraitFamily
    min_score: float  # soglia sulla famiglia genetica per attivazione
    utility_modifiers: dict[ActionType, float] = field(default_factory=dict)
    description: str = ""

    def __post_init__(self) -> None:
        if not (0.0 <= self.min_score <= 1.0):
            raise ValueError(f"min_score deve essere in [0, 1], ricevuto {self.min_score}")
        for action, mod in self.utility_modifiers.items():
            if not (-1.0 <= mod <= 1.0):
                raise ValueError(
                    f"Modifier fuori range [-1, 1] per {self.trait.value}/{action.value}: {mod}"
                )


# ---------------------------------------------------------------------------
# Catalogo tratti
# ---------------------------------------------------------------------------

TRAIT_DEFS: Final[dict[Trait, TraitDef]] = {
    # --- SOCIAL ---
    Trait.GENTILE: TraitDef(
        trait=Trait.GENTILE,
        category=TraitCategory.SOCIAL,
        family=TraitFamily.SOCIAL,
        min_score=0.50,
        utility_modifiers={ActionType.SOCIALIZE: 0.20},
        description="Portato alla gentilezza e all'ascolto.",
    ),
    Trait.EMPATICO: TraitDef(
        trait=Trait.EMPATICO,
        category=TraitCategory.SOCIAL,
        family=TraitFamily.SOCIAL,
        min_score=0.58,
        utility_modifiers={ActionType.SOCIALIZE: 0.25},
        description="Sintonizzato sulle emozioni altrui.",
    ),
    Trait.SOCIALE: TraitDef(
        trait=Trait.SOCIALE,
        category=TraitCategory.SOCIAL,
        family=TraitFamily.SOCIAL,
        min_score=0.55,
        utility_modifiers={ActionType.SOCIALIZE: 0.35},
        description="Ama la compagnia e le interazioni.",
    ),
    Trait.GENEROSO: TraitDef(
        trait=Trait.GENEROSO,
        category=TraitCategory.SOCIAL,
        family=TraitFamily.SOCIAL,
        min_score=0.60,
        utility_modifiers={ActionType.SOCIALIZE: 0.15},
        description="Dona volentieri tempo e risorse.",
    ),
    Trait.LEALE: TraitDef(
        trait=Trait.LEALE,
        category=TraitCategory.SOCIAL,
        family=TraitFamily.SOCIAL,
        min_score=0.52,
        utility_modifiers={ActionType.SOCIALIZE: 0.15},
        description="Fedele agli impegni e alle persone care.",
    ),
    Trait.RISERVATO: TraitDef(
        trait=Trait.RISERVATO,
        category=TraitCategory.SOCIAL,
        family=TraitFamily.SOCIAL,
        min_score=0.62,
        utility_modifiers={ActionType.SOCIALIZE: -0.25, ActionType.RELAX: 0.15},
        description="Preferisce la solitudine alla compagnia.",
    ),
    # --- MENTAL ---
    Trait.INTELLETTUALE: TraitDef(
        trait=Trait.INTELLETTUALE,
        category=TraitCategory.MENTAL,
        family=TraitFamily.MENTAL,
        min_score=0.55,
        utility_modifiers={
            ActionType.RELAX: 0.20,
            ActionType.STUDY: 0.50,
        },
        description="Ama studiare e approfondire.",
    ),
    Trait.CURIOSO: TraitDef(
        trait=Trait.CURIOSO,
        category=TraitCategory.MENTAL,
        family=TraitFamily.MENTAL,
        min_score=0.48,
        utility_modifiers={ActionType.SOCIALIZE: 0.15, ActionType.RELAX: 0.10},
        description="Spinto a esplorare e capire.",
    ),
    Trait.RIFLESSIVO: TraitDef(
        trait=Trait.RIFLESSIVO,
        category=TraitCategory.MENTAL,
        family=TraitFamily.MENTAL,
        min_score=0.55,
        utility_modifiers={ActionType.RELAX: 0.20, ActionType.NAP: 0.10},
        description="Pensa a lungo prima di agire.",
    ),
    Trait.ORDINATO: TraitDef(
        trait=Trait.ORDINATO,
        category=TraitCategory.LIFESTYLE,
        family=TraitFamily.MENTAL,
        min_score=0.55,
        utility_modifiers={ActionType.SHOWER: 0.25},
        description="Tiene tutto in ordine.",
    ),
    Trait.SOGNATORE: TraitDef(
        trait=Trait.SOGNATORE,
        category=TraitCategory.MENTAL,
        family=TraitFamily.MENTAL,
        min_score=0.62,
        utility_modifiers={ActionType.RELAX: 0.25, ActionType.NAP: 0.10},
        description="Vive con la testa tra le nuvole.",
    ),
    Trait.TIMIDO: TraitDef(
        trait=Trait.TIMIDO,
        category=TraitCategory.SOCIAL,
        family=TraitFamily.MENTAL,
        min_score=0.58,
        utility_modifiers={ActionType.SOCIALIZE: -0.30},
        description="A disagio nelle interazioni nuove.",
    ),
    # --- PHYSICAL ---
    Trait.ATLETICO: TraitDef(
        trait=Trait.ATLETICO,
        category=TraitCategory.PHYSICAL,
        family=TraitFamily.PHYSICAL,
        min_score=0.52,
        utility_modifiers={
            ActionType.RELAX: 0.20,
            ActionType.PRACTICE_COMBAT: 0.50,
        },
        description="In forma, ama muoversi.",
    ),
    Trait.CORAGGIOSO: TraitDef(
        trait=Trait.CORAGGIOSO,
        category=TraitCategory.PERSONALITY,
        family=TraitFamily.PHYSICAL,
        min_score=0.58,
        utility_modifiers={ActionType.SOCIALIZE: 0.10},
        description="Affronta il pericolo senza esitare.",
    ),
    Trait.IMPULSIVO: TraitDef(
        trait=Trait.IMPULSIVO,
        category=TraitCategory.PERSONALITY,
        family=TraitFamily.PHYSICAL,
        min_score=0.60,
        utility_modifiers={ActionType.SOCIALIZE: 0.15, ActionType.RELAX: -0.10},
        description="Agisce d'istinto.",
    ),
    Trait.RIBELLE: TraitDef(
        trait=Trait.RIBELLE,
        category=TraitCategory.PERSONALITY,
        family=TraitFamily.PHYSICAL,
        min_score=0.65,
        utility_modifiers={ActionType.SOCIALIZE: 0.10},
        description="Rifiuta le regole imposte.",
    ),
    # --- CREATIVE ---
    Trait.ARTISTICO: TraitDef(
        trait=Trait.ARTISTICO,
        category=TraitCategory.PERSONALITY,
        family=TraitFamily.CREATIVE,
        min_score=0.55,
        utility_modifiers={
            ActionType.RELAX: 0.30,
            ActionType.PRACTICE_ART: 0.60,
        },
        description="Esprime sé stesso con l'arte.",
    ),
    Trait.CREATIVO: TraitDef(
        trait=Trait.CREATIVO,
        category=TraitCategory.PERSONALITY,
        family=TraitFamily.CREATIVE,
        min_score=0.50,
        utility_modifiers={ActionType.RELAX: 0.25, ActionType.SOCIALIZE: 0.10},
        description="Trova soluzioni originali.",
    ),
    Trait.SPENSIERATO: TraitDef(
        trait=Trait.SPENSIERATO,
        category=TraitCategory.PERSONALITY,
        family=TraitFamily.CREATIVE,
        min_score=0.58,
        utility_modifiers={ActionType.SOCIALIZE: 0.20, ActionType.RELAX: 0.10},
        description="Vive senza troppe preoccupazioni.",
    ),
    # --- PRACTICAL ---
    Trait.PRATICO: TraitDef(
        trait=Trait.PRATICO,
        category=TraitCategory.LIFESTYLE,
        family=TraitFamily.PRACTICAL,
        min_score=0.50,
        utility_modifiers={ActionType.RELAX: -0.10},
        description="Concreto e orientato al fare.",
    ),
    Trait.AMBIZIOSO: TraitDef(
        trait=Trait.AMBIZIOSO,
        category=TraitCategory.PERSONALITY,
        family=TraitFamily.PRACTICAL,
        min_score=0.58,
        utility_modifiers={ActionType.SOCIALIZE: 0.20, ActionType.RELAX: -0.15},
        description="Punta in alto, sempre.",
    ),
    Trait.PRUDENTE: TraitDef(
        trait=Trait.PRUDENTE,
        category=TraitCategory.PERSONALITY,
        family=TraitFamily.PRACTICAL,
        min_score=0.55,
        utility_modifiers={ActionType.NAP: 0.10},
        description="Valuta i rischi prima di agire.",
    ),
    Trait.TESTARDO: TraitDef(
        trait=Trait.TESTARDO,
        category=TraitCategory.PERSONALITY,
        family=TraitFamily.PRACTICAL,
        min_score=0.58,
        utility_modifiers={},
        description="Non cambia idea facilmente.",
    ),
    Trait.OTTIMISTA: TraitDef(
        trait=Trait.OTTIMISTA,
        category=TraitCategory.PERSONALITY,
        family=TraitFamily.PRACTICAL,
        min_score=0.52,
        utility_modifiers={ActionType.SOCIALIZE: 0.15, ActionType.RELAX: 0.10},
        description="Vede il bicchiere mezzo pieno.",
    ),
    Trait.PESSIMISTA: TraitDef(
        trait=Trait.PESSIMISTA,
        category=TraitCategory.PERSONALITY,
        family=TraitFamily.PRACTICAL,
        min_score=0.60,
        utility_modifiers={ActionType.SOCIALIZE: -0.10, ActionType.RELAX: 0.05},
        description="Tende a vedere il lato negativo.",
    ),
    Trait.SEXUALLY_EXPLORATIVE: TraitDef(
        trait=Trait.SEXUALLY_EXPLORATIVE,
        category=TraitCategory.SOCIAL,
        family=TraitFamily.CREATIVE,
        min_score=0.65,
        utility_modifiers={ActionType.SOCIALIZE: 0.15},
        description="Aperto all'esplorazione relazionale.",
    ),
    Trait.EMOTIONALLY_EXPRESSIVE: TraitDef(
        trait=Trait.EMOTIONALLY_EXPRESSIVE,
        category=TraitCategory.SOCIAL,
        family=TraitFamily.SOCIAL,
        min_score=0.60,
        utility_modifiers={ActionType.SOCIALIZE: 0.15},
        description="Esprime apertamente le proprie emozioni.",
    ),
}


# ---------------------------------------------------------------------------
# Aspirazioni
# ---------------------------------------------------------------------------

#: Pesi dei tratti verso ogni aspirazione. `argmax` determina l'aspirazione.
ASPIRATION_WEIGHTS: Final[dict[Aspiration, dict[Trait, float]]] = {
    Aspiration.FAMILY: {
        Trait.GENTILE: 1.0,
        Trait.EMPATICO: 1.0,
        Trait.LEALE: 1.2,
        Trait.GENEROSO: 0.8,
    },
    Aspiration.CAREER: {
        Trait.AMBIZIOSO: 1.5,
        Trait.PRATICO: 0.8,
        Trait.INTELLETTUALE: 0.6,
    },
    Aspiration.KNOWLEDGE: {
        Trait.INTELLETTUALE: 1.5,
        Trait.CURIOSO: 1.0,
        Trait.RIFLESSIVO: 0.8,
    },
    Aspiration.CREATIVITY: {
        Trait.ARTISTICO: 1.5,
        Trait.CREATIVO: 1.2,
        Trait.SOGNATORE: 0.8,
    },
    Aspiration.FAME: {
        Trait.SOCIALE: 1.0,
        Trait.AMBIZIOSO: 0.8,
        Trait.CORAGGIOSO: 0.6,
        Trait.SPENSIERATO: 0.6,
    },
    Aspiration.WEALTH: {
        Trait.PRATICO: 1.2,
        Trait.AMBIZIOSO: 1.0,
        Trait.PRUDENTE: 0.6,
    },
    Aspiration.LOVE: {
        Trait.EMPATICO: 1.2,
        Trait.GENTILE: 1.0,
        Trait.LEALE: 0.8,
        Trait.SPENSIERATO: 0.6,
    },
    Aspiration.FITNESS: {
        Trait.ATLETICO: 2.0,
        Trait.CORAGGIOSO: 0.6,
    },
}


__all__ = ["ASPIRATION_WEIGHTS", "TRAIT_DEFS", "TraitDef"]
