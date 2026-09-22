"""Enum e costanti del dominio personalità dinamica."""

from __future__ import annotations

from enum import StrEnum
from typing import Final

from simai.npc.ai.enums import ActionType
from simai.npc.background.enums import FormativeEventKind
from simai.npc.traits.enums import Trait


class ValueAxis(StrEnum):
    """Assi di valore (adattati da Schwartz)."""

    TRADITION = "TRADITION"  # famiglia, rituali, continuità
    BENEVOLENCE = "BENEVOLENCE"  # aiutare, empatia
    ACHIEVEMENT = "ACHIEVEMENT"  # successo, competenza
    HEDONISM = "HEDONISM"  # piacere, gratificazione
    SECURITY = "SECURITY"  # stabilità, protezione
    SELF_DIRECTION = "SELF_DIRECTION"  # autonomia, esplorazione


#: Soglia minima di strength per considerare un tratto "attivo".
ACTIVE_THRESHOLD: Final[float] = 0.30

#: Strength iniziale per un tratto già presente.
INITIAL_STRENGTH: Final[float] = 1.0

#: Strength iniziale per un tratto "candidato" (non ancora presente).
CANDIDATE_INITIAL_STRENGTH: Final[float] = 0.05

#: Strength massima.
MAX_STRENGTH: Final[float] = 1.0

#: Strength minima sotto cui il tratto è eliminato.
MIN_STRENGTH: Final[float] = 0.05

#: Decay giornaliero del trait strength (non rinforzato).
TRAIT_DECAY_PER_DAY: Final[float] = 0.008

#: Valore iniziale delle values.
INITIAL_VALUE: Final[float] = 0.50

#: Regressione giornaliera delle values verso 0.5.
VALUE_MEAN_REVERSION: Final[float] = 0.05

#: Fattore di scala per eventi su values.
EVENT_SEVERITY_SCALE: Final[float] = 1.0

#: Scala di normalizzazione per l'alignment: il massimo effetto su value
#: viene mappato a 1.0.
ALIGNMENT_SCALE: Final[float] = 0.005

#: Amplificazione del boost dovuto ai values.
VALUES_BOOST_SCALE: Final[float] = 0.60

#: Clamp del values boost (margine ammesso).
VALUES_BOOST_MIN: Final[float] = 0.70
VALUES_BOOST_MAX: Final[float] = 1.40

#: Azione -> effetti su trait strength.
ACTION_TRAIT_EFFECTS: Final[dict[ActionType, dict[Trait, float]]] = {
    ActionType.SHOWER: {Trait.ORDINATO: 0.005},
    ActionType.SOCIALIZE: {
        Trait.SOCIALE: 0.010,
        Trait.EMPATICO: 0.005,
        Trait.GENTILE: 0.005,
    },
    ActionType.RELAX: {Trait.SPENSIERATO: 0.004},
    ActionType.PRACTICE_COMBAT: {
        Trait.ATLETICO: 0.015,
        Trait.CORAGGIOSO: 0.010,
        Trait.IMPULSIVO: 0.005,
    },
    ActionType.STUDY: {
        Trait.INTELLETTUALE: 0.015,
        Trait.RIFLESSIVO: 0.010,
        Trait.CURIOSO: 0.010,
    },
    ActionType.PRACTICE_ART: {
        Trait.ARTISTICO: 0.015,
        Trait.CREATIVO: 0.010,
        Trait.SOGNATORE: 0.005,
    },
    ActionType.COOK: {Trait.PRATICO: 0.010},
    ActionType.PRACTICE_CRAFT: {
        Trait.PRATICO: 0.015,
        Trait.ORDINATO: 0.008,
    },
    ActionType.PRACTICE_TRADE: {
        Trait.AMBIZIOSO: 0.010,
        Trait.SOCIALE: 0.005,
    },
    ActionType.PRACTICE_SERVICE: {
        Trait.GENTILE: 0.010,
        Trait.GENEROSO: 0.008,
    },
    ActionType.CONSUME_ALCOHOL: {
        Trait.IMPULSIVO: 0.005,
        Trait.SPENSIERATO: 0.005,
    },
    ActionType.SMOKE: {Trait.IMPULSIVO: 0.005},
    ActionType.GAMBLE: {
        Trait.IMPULSIVO: 0.005,
        Trait.AMBIZIOSO: 0.005,
    },
    ActionType.BE_ALONE: {
        Trait.RISERVATO: 0.010,
        Trait.RIFLESSIVO: 0.005,
    },
}


def action_values_alignment(
    action_type: ActionType,
) -> dict[ValueAxis, float]:
    """Ritorna l'alignment normalizzato [0, 1] di un'azione sui 6 assi.

    Deriva da `ACTION_VALUE_EFFECTS` scalando per `ALIGNMENT_SCALE`.
    Un'azione che non sposta un asse ha alignment 0 su quell'asse.
    """
    effects = ACTION_VALUE_EFFECTS.get(action_type, {})
    result: dict[ValueAxis, float] = {}
    for axis, delta in effects.items():
        result[axis] = max(0.0, min(1.0, delta / ALIGNMENT_SCALE))
    return result


#: Azione -> effetti su values.
ACTION_VALUE_EFFECTS: Final[dict[ActionType, dict[ValueAxis, float]]] = {
    ActionType.SOCIALIZE: {ValueAxis.BENEVOLENCE: 0.0025},
    ActionType.STUDY: {
        ValueAxis.ACHIEVEMENT: 0.004,
        ValueAxis.SELF_DIRECTION: 0.0025,
    },
    ActionType.PRACTICE_ART: {ValueAxis.SELF_DIRECTION: 0.0025},
    ActionType.PRACTICE_COMBAT: {ValueAxis.SECURITY: 0.0025},
    ActionType.RELAX: {ValueAxis.HEDONISM: 0.0025},
    ActionType.GAMBLE: {ValueAxis.HEDONISM: 0.005},
    ActionType.CONSUME_ALCOHOL: {ValueAxis.HEDONISM: 0.004},
    ActionType.COOK: {
        ValueAxis.TRADITION: 0.0025,
        ValueAxis.BENEVOLENCE: 0.0025,
    },
    ActionType.PRACTICE_CRAFT: {ValueAxis.ACHIEVEMENT: 0.0025},
    ActionType.PRACTICE_TRADE: {ValueAxis.ACHIEVEMENT: 0.004},
    ActionType.PRACTICE_SERVICE: {ValueAxis.BENEVOLENCE: 0.004},
    ActionType.BE_ALONE: {ValueAxis.SELF_DIRECTION: 0.004},
    ActionType.SHOWER: {ValueAxis.SECURITY: 0.0015},
}


#: Evento formativo -> effetti su values (scalati per severity).
EVENT_VALUE_EFFECTS: Final[dict[FormativeEventKind, dict[ValueAxis, float]]] = {
    FormativeEventKind.PARENT_LOST: {
        ValueAxis.SECURITY: +0.15,
        ValueAxis.TRADITION: -0.10,
    },
    FormativeEventKind.SIBLING_BORN: {
        ValueAxis.BENEVOLENCE: +0.10,
        ValueAxis.TRADITION: +0.05,
    },
    FormativeEventKind.BULLIED: {
        ValueAxis.SECURITY: -0.10,
        ValueAxis.SELF_DIRECTION: +0.05,
    },
    FormativeEventKind.MOVED: {
        ValueAxis.SELF_DIRECTION: +0.05,
        ValueAxis.TRADITION: -0.03,
    },
    FormativeEventKind.FIRST_LOVE: {
        ValueAxis.HEDONISM: +0.10,
        ValueAxis.BENEVOLENCE: +0.05,
    },
    FormativeEventKind.MENTORSHIP: {
        ValueAxis.ACHIEVEMENT: +0.08,
        ValueAxis.TRADITION: +0.05,
        ValueAxis.SELF_DIRECTION: +0.05,
    },
    FormativeEventKind.ILLNESS: {ValueAxis.SECURITY: +0.10},
    FormativeEventKind.BETRAYAL: {
        ValueAxis.SECURITY: -0.15,
        ValueAxis.BENEVOLENCE: -0.10,
    },
    FormativeEventKind.ACHIEVEMENT: {
        ValueAxis.ACHIEVEMENT: +0.15,
        ValueAxis.SELF_DIRECTION: +0.05,
    },
    FormativeEventKind.TRAUMA: {
        ValueAxis.SECURITY: -0.20,
        ValueAxis.SELF_DIRECTION: +0.10,
    },
}


#: Evento formativo -> effetti su trait strength (scalati per severity).
EVENT_TRAIT_EFFECTS: Final[dict[FormativeEventKind, dict[Trait, float]]] = {
    FormativeEventKind.PARENT_LOST: {
        Trait.RIFLESSIVO: +0.05,
        Trait.RISERVATO: +0.05,
    },
    FormativeEventKind.BULLIED: {
        Trait.TIMIDO: +0.15,
        Trait.RISERVATO: +0.10,
        Trait.CORAGGIOSO: -0.05,
    },
    FormativeEventKind.FIRST_LOVE: {
        Trait.SPENSIERATO: +0.05,
        Trait.EMOTIONALLY_EXPRESSIVE: +0.05,
    },
    FormativeEventKind.MENTORSHIP: {
        Trait.INTELLETTUALE: +0.05,
        Trait.RIFLESSIVO: +0.05,
    },
    FormativeEventKind.BETRAYAL: {
        Trait.RISERVATO: +0.10,
        Trait.EMPATICO: -0.05,
    },
    FormativeEventKind.TRAUMA: {
        Trait.RISERVATO: +0.10,
        Trait.IMPULSIVO: +0.05,
        Trait.CORAGGIOSO: -0.10,
    },
}


__all__ = [
    "ACTION_TRAIT_EFFECTS",
    "ACTION_VALUE_EFFECTS",
    "ACTIVE_THRESHOLD",
    "ALIGNMENT_SCALE",
    "CANDIDATE_INITIAL_STRENGTH",
    "EVENT_SEVERITY_SCALE",
    "EVENT_TRAIT_EFFECTS",
    "EVENT_VALUE_EFFECTS",
    "INITIAL_STRENGTH",
    "INITIAL_VALUE",
    "MAX_STRENGTH",
    "MIN_STRENGTH",
    "TRAIT_DECAY_PER_DAY",
    "VALUES_BOOST_MAX",
    "VALUES_BOOST_MIN",
    "VALUES_BOOST_SCALE",
    "VALUE_MEAN_REVERSION",
    "ValueAxis",
    "action_values_alignment",
]
