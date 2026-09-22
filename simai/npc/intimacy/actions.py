"""Definizioni delle azioni di intimità."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final

from simai.npc.intimacy.enums import IntimacyAction
from simai.npc.needs.enums import NeedType
from simai.npc.relationships.enums import RelationshipKind
from simai.npc.traits.enums import Trait


@dataclass(frozen=True, slots=True)
class IntimacyActionDef:
    """Definizione di un'azione di intimità.

    Attributi:
      - `level`: intensità dell'azione (0..5).
      - `min_bond`, `min_strength`: prerequisiti.
      - `allowed_kinds`: tipi di relazione ammessi.
      - `needs_effects`: delta sui bisogni (applicati a entrambi).
      - `moodlets_delta`: delta happiness per entrambi.
      - `bond_gain`, `strength_gain`: incrementi post-successo.
      - `memory_valence`, `memory_saliency`: memoria.
      - `required_traits`, `blocked_traits`: sull'iniziatore.
      - `is_digital`: se True, non richiede presenza fisica.
    """

    action: IntimacyAction
    level: int
    label: str
    min_bond: float
    min_strength: float
    allowed_kinds: frozenset[RelationshipKind]
    needs_effects: dict[NeedType, float] = field(default_factory=dict)
    moodlets_delta: float = 0.10
    bond_gain: float = 0.05
    strength_gain: float = 0.03
    memory_valence: float = 0.5
    memory_saliency: float = 0.4
    required_traits: frozenset[Trait] = frozenset()
    blocked_traits: frozenset[Trait] = frozenset()
    is_digital: bool = False

    def __post_init__(self) -> None:
        if not (0 <= self.level <= 5):
            raise ValueError(f"level deve essere in [0, 5], ricevuto {self.level}")
        if not (0.0 <= self.min_bond <= 1.0):
            raise ValueError(f"min_bond in [0, 1], ricevuto {self.min_bond}")
        if not (0.0 <= self.min_strength <= 1.0):
            raise ValueError(f"min_strength in [0, 1], ricevuto {self.min_strength}")
        if not (-1.0 <= self.memory_valence <= 1.0):
            raise ValueError(f"memory_valence in [-1, 1], ricevuto {self.memory_valence}")
        if not (0.0 <= self.memory_saliency <= 1.0):
            raise ValueError(f"memory_saliency in [0, 1], ricevuto {self.memory_saliency}")


# ---------------------------------------------------------------------------
# Insiemi di relazioni ammesse
# ---------------------------------------------------------------------------

_FRIENDSHIP_KINDS: Final[frozenset[RelationshipKind]] = frozenset(
    {
        RelationshipKind.FRIEND_OF,
        RelationshipKind.BEST_FRIEND_OF,
    }
)

_ROMANTIC_KINDS: Final[frozenset[RelationshipKind]] = frozenset(
    {
        RelationshipKind.PARTNER_OF,
        RelationshipKind.SPOUSE_OF,
    }
)

_ALLOWED_SOCIAL: Final[frozenset[RelationshipKind]] = _FRIENDSHIP_KINDS | _ROMANTIC_KINDS


# ---------------------------------------------------------------------------
# Catalogo azioni
# ---------------------------------------------------------------------------

INTIMACY_CATALOG: Final[tuple[IntimacyActionDef, ...]] = (
    # ================================================================
    # CONFIDENZA (esistenti, livello 0-2)
    # ================================================================
    IntimacyActionDef(
        action=IntimacyAction.CONFIDE,
        level=0,
        label="Confidarsi",
        min_bond=0.10,
        min_strength=0.40,
        allowed_kinds=_ALLOWED_SOCIAL,
        needs_effects={NeedType.SOCIAL: 15.0, NeedType.FUN: 5.0},
        moodlets_delta=0.08,
        bond_gain=0.04,
        strength_gain=0.02,
        memory_valence=0.3,
        memory_saliency=0.30,
    ),
    IntimacyActionDef(
        action=IntimacyAction.SHARE_MOMENT,
        level=1,
        label="Condividere un momento",
        min_bond=0.20,
        min_strength=0.45,
        allowed_kinds=_ALLOWED_SOCIAL,
        needs_effects={NeedType.SOCIAL: 20.0, NeedType.FUN: 15.0},
        moodlets_delta=0.10,
        bond_gain=0.05,
        strength_gain=0.03,
        memory_valence=0.4,
        memory_saliency=0.35,
    ),
    IntimacyActionDef(
        action=IntimacyAction.INTIMATE_TALK,
        level=2,
        label="Conversazione profonda",
        min_bond=0.35,
        min_strength=0.55,
        allowed_kinds=_ALLOWED_SOCIAL,
        needs_effects={NeedType.SOCIAL: 30.0, NeedType.FUN: 10.0},
        moodlets_delta=0.15,
        bond_gain=0.07,
        strength_gain=0.04,
        memory_valence=0.5,
        memory_saliency=0.45,
    ),
    # ================================================================
    # ROMANTICHE (esistenti, livello 3-5)
    # ================================================================
    IntimacyActionDef(
        action=IntimacyAction.ROMANTIC_GESTURE,
        level=3,
        label="Gesto romantico",
        min_bond=0.45,
        min_strength=0.60,
        allowed_kinds=_ROMANTIC_KINDS,
        needs_effects={
            NeedType.SOCIAL: 25.0,
            NeedType.FUN: 25.0,
            NeedType.COMFORT: 10.0,
        },
        moodlets_delta=0.20,
        bond_gain=0.08,
        strength_gain=0.05,
        memory_valence=0.7,
        memory_saliency=0.55,
    ),
    IntimacyActionDef(
        action=IntimacyAction.KISS,
        level=4,
        label="Bacio",
        min_bond=0.55,
        min_strength=0.65,
        allowed_kinds=_ROMANTIC_KINDS,
        needs_effects={
            NeedType.SOCIAL: 30.0,
            NeedType.FUN: 30.0,
            NeedType.COMFORT: 15.0,
        },
        moodlets_delta=0.25,
        bond_gain=0.10,
        strength_gain=0.06,
        memory_valence=0.8,
        memory_saliency=0.65,
    ),
    IntimacyActionDef(
        action=IntimacyAction.INTIMATE_ENCOUNTER,
        level=5,
        label="Incontro intimo",
        min_bond=0.70,
        min_strength=0.75,
        allowed_kinds=_ROMANTIC_KINDS,
        needs_effects={
            NeedType.SOCIAL: 40.0,
            NeedType.FUN: 40.0,
            NeedType.COMFORT: 20.0,
        },
        moodlets_delta=0.35,
        bond_gain=0.12,
        strength_gain=0.08,
        memory_valence=0.9,
        memory_saliency=0.85,
    ),
    # ================================================================
    # SOSTITUTIVE (Chunk 3.7b) — non romantiche, più facili
    # ================================================================
    IntimacyActionDef(
        action=IntimacyAction.SHARE_MEAL,
        level=1,
        label="Condividere un pasto",
        min_bond=0.15,
        min_strength=0.40,
        allowed_kinds=_ALLOWED_SOCIAL,
        needs_effects={
            NeedType.INTIMACY: 30.0,
            NeedType.HUNGER: 40.0,
            NeedType.SOCIAL: 20.0,
        },
        moodlets_delta=0.10,
        bond_gain=0.05,
        strength_gain=0.03,
        memory_valence=0.4,
        memory_saliency=0.30,
    ),
    IntimacyActionDef(
        action=IntimacyAction.HOLD_HANDS,
        level=2,
        label="Tenersi per mano",
        min_bond=0.30,
        min_strength=0.50,
        allowed_kinds=_ALLOWED_SOCIAL,
        needs_effects={
            NeedType.INTIMACY: 40.0,
            NeedType.FUN: 15.0,
            NeedType.COMFORT: 20.0,
        },
        moodlets_delta=0.15,
        bond_gain=0.07,
        strength_gain=0.04,
        memory_valence=0.6,
        memory_saliency=0.40,
    ),
    IntimacyActionDef(
        action=IntimacyAction.DEEP_TALK,
        level=2,
        label="Discorso profondo",
        min_bond=0.35,
        min_strength=0.55,
        allowed_kinds=_ALLOWED_SOCIAL,
        needs_effects={
            NeedType.INTIMACY: 50.0,
            NeedType.SOCIAL: 20.0,
            NeedType.FUN: 10.0,
        },
        moodlets_delta=0.18,
        bond_gain=0.08,
        strength_gain=0.04,
        memory_valence=0.6,
        memory_saliency=0.50,
    ),
    IntimacyActionDef(
        action=IntimacyAction.CUDDLE,
        level=3,
        label="Coccole",
        min_bond=0.45,
        min_strength=0.60,
        allowed_kinds=_ALLOWED_SOCIAL,
        needs_effects={
            NeedType.INTIMACY: 60.0,
            NeedType.FUN: 20.0,
            NeedType.COMFORT: 30.0,
        },
        moodlets_delta=0.22,
        bond_gain=0.09,
        strength_gain=0.05,
        memory_valence=0.7,
        memory_saliency=0.55,
    ),
    # ================================================================
    # DIGITALI (Chunk 3.7b) — non richiedono presenza fisica
    # ================================================================
    IntimacyActionDef(
        action=IntimacyAction.TEXT_MESSAGE,
        level=1,
        label="Scambiarsi messaggi",
        min_bond=0.10,
        min_strength=0.30,
        allowed_kinds=_ALLOWED_SOCIAL,
        needs_effects={
            NeedType.INTIMACY: 15.0,
            NeedType.SOCIAL: 20.0,
            NeedType.FUN: 10.0,
        },
        moodlets_delta=0.08,
        bond_gain=0.03,
        strength_gain=0.02,
        memory_valence=0.3,
        memory_saliency=0.25,
        is_digital=True,
    ),
    IntimacyActionDef(
        action=IntimacyAction.VIRTUAL_CALL,
        level=2,
        label="Chiamata virtuale",
        min_bond=0.20,
        min_strength=0.40,
        allowed_kinds=_ALLOWED_SOCIAL,
        needs_effects={
            NeedType.INTIMACY: 25.0,
            NeedType.SOCIAL: 30.0,
            NeedType.FUN: 15.0,
        },
        moodlets_delta=0.12,
        bond_gain=0.05,
        strength_gain=0.03,
        memory_valence=0.4,
        memory_saliency=0.35,
        is_digital=True,
    ),
)


def get_intimacy_def(action: IntimacyAction) -> IntimacyActionDef:
    """Ritorna la definizione dell'azione data.

    Solleva `KeyError` se l'azione non è nel catalogo.
    """
    for def_ in INTIMACY_CATALOG:
        if def_.action is action:
            return def_
    raise KeyError(f"IntimacyAction sconosciuta: {action}")


def get_all_kinds_covered() -> set[IntimacyAction]:
    """Set di tutti gli `IntimacyAction` presenti nel catalogo."""
    return {d.action for d in INTIMACY_CATALOG}


__all__ = [
    "INTIMACY_CATALOG",
    "IntimacyActionDef",
    "get_all_kinds_covered",
    "get_intimacy_def",
]
