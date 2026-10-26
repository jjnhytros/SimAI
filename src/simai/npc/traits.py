from enum import StrEnum

from simai.actions.enums import ActionKind
from simai.needs.enums import NeedKind


class Trait(StrEnum):
    LAZY = "lazy"
    ENERGETIC = "energetic"
    SOCIAL = "social"
    SOLITARY = "solitary"
    GLUTTON = "glutton"


# Moltiplicatore del decadimento per bisogno, per tratto.
# > 1.0 = decade più veloce; < 1.0 = decade più lento.
TRAIT_DECAY_MODIFIERS: dict[Trait, dict[NeedKind, float]] = {
    Trait.LAZY: {NeedKind.FUN: 1.30},
    Trait.ENERGETIC: {NeedKind.FUN: 0.80},
    Trait.SOCIAL: {NeedKind.INTIMACY: 1.30},
    Trait.SOLITARY: {NeedKind.INTIMACY: 0.60},
    Trait.GLUTTON: {NeedKind.HUNGER: 1.30},
}

# Bonus additivo all'utility di un'azione, per tratto.
TRAIT_UTILITY_BONUS: dict[Trait, dict[ActionKind, float]] = {
    Trait.LAZY: {ActionKind.PLAY: 0.15},
    Trait.ENERGETIC: {ActionKind.PLAY: 0.10},
    Trait.SOCIAL: {ActionKind.SOCIALIZE: 0.15},
    Trait.SOLITARY: {},
    Trait.GLUTTON: {ActionKind.EAT: 0.15},
}


def trait_decay_multiplier(traits: list[str], kind: NeedKind) -> float:
    """Moltiplicatore combinato dei tratti sul decadimento.

    I moltiplicatori si moltiplicano fra loro se un personaggio ha
    più tratti che toccano lo stesso bisogno (non è il caso del seed
    attuale, ma il codice non lo presuppone).
    """
    multiplier = 1.0
    for raw in traits:
        try:
            trait = Trait(raw)
        except ValueError:
            continue
        multiplier *= TRAIT_DECAY_MODIFIERS.get(trait, {}).get(kind, 1.0)
    return multiplier


def trait_utility_bonus(traits: list[str], action: ActionKind) -> float:
    """Somma dei bonus di utility dei tratti per un'azione."""
    total = 0.0
    for raw in traits:
        try:
            trait = Trait(raw)
        except ValueError:
            continue
        total += TRAIT_UTILITY_BONUS.get(trait, {}).get(action, 0.0)
    return total


def trait_move_penalty(traits: list[str]) -> float:
    """Penalità sui move per tratti che preferiscono restare.

    SOLITARY penalizza spostarsi verso altre location per socializzare.
    Non blocca il movimento: lo rende meno appetibile rispetto ad
    azioni locali.
    """
    if Trait.SOLITARY.value in traits:
        return -0.10
    return 0.0
