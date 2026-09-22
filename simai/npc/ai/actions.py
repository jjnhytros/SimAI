"""Azioni disponibili per gli NPC.

Modello:
  - Ogni azione ha `duration_ticks` e una mappa `effects` (delta totali
    sui bisogni, distribuiti uniformemente sulla durata).
  - `trains_skill`: se impostata, l'azione fa guadagnare XP alla skill.
  - `min_skill_level`: livello minimo richiesto (filtro AI).
  - `utility_skill_boost`: +X% utility per level della skill trainata.
"""

from __future__ import annotations

from dataclasses import dataclass

from simai.npc.addictions.enums import AddictionKind
from simai.npc.ai.enums import ActionType
from simai.npc.needs.enums import NeedType
from simai.npc.skills.enums import SkillType


@dataclass(frozen=True, slots=True)
class Action:
    """Azione eseguibile da un NPC."""

    type: ActionType
    label: str
    duration_ticks: int
    effects: dict[NeedType, float]
    trains_skill: SkillType | None = None
    min_skill_level: int = 0
    utility_skill_boost: float = 0.0
    addiction_kind: AddictionKind | None = None

    def __post_init__(self) -> None:
        if self.duration_ticks < 1:
            raise ValueError(f"duration_ticks deve essere >= 1, ricevuto {self.duration_ticks}")
        if self.min_skill_level < 0:
            raise ValueError(f"min_skill_level deve essere >= 0, ricevuto {self.min_skill_level}")
        if self.utility_skill_boost < 0:
            raise ValueError(
                f"utility_skill_boost deve essere >= 0, ricevuto {self.utility_skill_boost}"
            )

    @property
    def is_instant(self) -> bool:
        return self.duration_ticks == 1

    @property
    def is_training(self) -> bool:
        return self.trains_skill is not None

    def effect_per_tick(self, need: NeedType) -> float:
        return self.effects.get(need, 0.0) / self.duration_ticks

    def to_dict(self) -> dict[str, object]:
        return {
            "type": self.type.value,
            "label": self.label,
            "duration_ticks": self.duration_ticks,
            "effects": {n.value: v for n, v in self.effects.items()},
            "trains_skill": self.trains_skill.value if self.trains_skill else None,
            "min_skill_level": self.min_skill_level,
            "utility_skill_boost": self.utility_skill_boost,
            "addiction_kind": self.addiction_kind.value if self.addiction_kind else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> Action:
        from simai.utils import coerce_float, coerce_int, coerce_str

        raw_effects = data.get("effects", {})
        effects: dict[NeedType, float] = {}
        if isinstance(raw_effects, dict):
            for k, v in raw_effects.items():
                try:
                    need = NeedType(str(k))
                except ValueError:
                    continue
                try:
                    effects[need] = coerce_float(v, name=f"effects[{k}]")
                except ValueError:
                    continue

        raw_skill = data.get("trains_skill")
        trains_skill: SkillType | None = None
        if raw_skill is not None and raw_skill != "":
            try:
                trains_skill = SkillType(coerce_str(raw_skill, name="trains_skill"))
            except ValueError:
                trains_skill = None

        raw_addict = data.get("addiction_kind")
        addiction_kind: AddictionKind | None = None
        if raw_addict is not None and raw_addict != "":
            try:
                addiction_kind = AddictionKind(coerce_str(raw_addict, name="addiction_kind"))
            except ValueError:
                addiction_kind = None

        return cls(
            type=ActionType(coerce_str(data["type"], name="action.type")),
            label=coerce_str(data["label"], name="action.label"),
            duration_ticks=coerce_int(data["duration_ticks"], name="action.duration_ticks"),
            effects=effects,
            trains_skill=trains_skill,
            min_skill_level=coerce_int(
                data.get("min_skill_level", 0), name="action.min_skill_level"
            ),
            utility_skill_boost=coerce_float(
                data.get("utility_skill_boost", 0.0),
                name="action.utility_skill_boost",
            ),
            addiction_kind=addiction_kind,
        )


# ---------------------------------------------------------------------------
# Catalogo azioni seed
# ---------------------------------------------------------------------------

ACTION_CATALOG: tuple[Action, ...] = (
    # --- Bisogni base ---
    Action(
        type=ActionType.EAT,
        label="Mangiare",
        duration_ticks=10,
        effects={NeedType.HUNGER: 70.0, NeedType.FUN: 5.0},
    ),
    Action(
        type=ActionType.DRINK,
        label="Bere",
        duration_ticks=3,
        effects={NeedType.THIRST: 80.0},
    ),
    Action(
        type=ActionType.USE_TOILET,
        label="Usare il bagno",
        duration_ticks=5,
        effects={NeedType.BLADDER: 100.0, NeedType.COMFORT: 5.0},
    ),
    Action(
        type=ActionType.SLEEP,
        label="Dormire",
        duration_ticks=60,
        effects={NeedType.ENERGY: 100.0, NeedType.COMFORT: 10.0},
    ),
    Action(
        type=ActionType.NAP,
        label="Riposino",
        duration_ticks=20,
        effects={NeedType.ENERGY: 40.0},
    ),
    Action(
        type=ActionType.SHOWER,
        label="Doccia",
        duration_ticks=8,
        effects={NeedType.HYGIENE: 100.0, NeedType.COMFORT: 5.0},
    ),
    Action(
        type=ActionType.SOCIALIZE,
        label="Socializzare",
        duration_ticks=15,
        effects={NeedType.SOCIAL: 70.0, NeedType.FUN: 20.0},
        trains_skill=SkillType.SOCIALIZING,
        utility_skill_boost=0.05,
    ),
    Action(
        type=ActionType.RELAX,
        label="Rilassarsi",
        duration_ticks=12,
        effects={NeedType.FUN: 50.0, NeedType.COMFORT: 15.0},
    ),
    # --- Training actions (Chunk 3.6b) ---
    Action(
        type=ActionType.PRACTICE_COMBAT,
        label="Allenarsi al combattimento",
        duration_ticks=20,
        effects={
            NeedType.FUN: 55.0,
            NeedType.ENERGY: -15.0,
            NeedType.COMFORT: -5.0,
        },
        trains_skill=SkillType.COMBAT,
        utility_skill_boost=0.05,
    ),
    Action(
        type=ActionType.STUDY,
        label="Studiare",
        duration_ticks=15,
        effects={NeedType.FUN: 60.0, NeedType.ENERGY: -10.0},
        trains_skill=SkillType.SCHOLARSHIP,
        utility_skill_boost=0.05,
    ),
    Action(
        type=ActionType.PRACTICE_ART,
        label="Praticare arte",
        duration_ticks=15,
        effects={NeedType.FUN: 60.0, NeedType.ENERGY: -5.0},
        trains_skill=SkillType.ARTISTRY,
        utility_skill_boost=0.05,
    ),
    Action(
        type=ActionType.COOK,
        label="Cucinare",
        duration_ticks=10,
        effects={NeedType.HUNGER: 50.0, NeedType.FUN: 25.0},
        trains_skill=SkillType.COOKING,
        utility_skill_boost=0.05,
    ),
    # --- Training actions per skill dei job (Chunk 3.6d) ---
    Action(
        type=ActionType.PRACTICE_CRAFT,
        label="Praticare artigianato",
        duration_ticks=15,
        effects={NeedType.FUN: 55.0, NeedType.ENERGY: -8.0},
        trains_skill=SkillType.CRAFTING,
        utility_skill_boost=0.05,
    ),
    Action(
        type=ActionType.PRACTICE_TRADE,
        label="Esercitare il commercio",
        duration_ticks=15,
        effects={
            NeedType.FUN: 55.0,
            NeedType.SOCIAL: 10.0,
            NeedType.ENERGY: -8.0,
        },
        trains_skill=SkillType.TRADING,
        utility_skill_boost=0.05,
    ),
    Action(
        type=ActionType.PRACTICE_SERVICE,
        label="Praticare il servizio",
        duration_ticks=15,
        effects={NeedType.FUN: 55.0, NeedType.COMFORT: -5.0},
        trains_skill=SkillType.SERVICE,
        utility_skill_boost=0.05,
    ),
    # --- Addiction actions (Chunk 3.6b) ---
    Action(
        type=ActionType.CONSUME_ALCOHOL,
        label="Bere alcolici",
        duration_ticks=8,
        effects={
            NeedType.FUN: 35.0,
            NeedType.ENERGY: -10.0,
            NeedType.HUNGER: -5.0,
        },
        addiction_kind=AddictionKind.ALCOHOL,
    ),
    Action(
        type=ActionType.SMOKE,
        label="Fumare",
        duration_ticks=5,
        effects={
            NeedType.FUN: 20.0,
            NeedType.COMFORT: 10.0,
        },
        addiction_kind=AddictionKind.TOBACCO,
    ),
    Action(
        type=ActionType.GAMBLE,
        label="Giocare d'azzardo",
        duration_ticks=10,
        effects={NeedType.FUN: 30.0, NeedType.ENERGY: -5.0},
        addiction_kind=AddictionKind.GAMBLING,
    ),
    Action(
        type=ActionType.DRINK_COFFEE,
        label="Bere caffè",
        duration_ticks=3,
        effects={NeedType.ENERGY: 25.0, NeedType.FUN: 5.0},
        addiction_kind=AddictionKind.CAFFEINE,
    ),
    # --- Bisogni avanzati (Chunk 3.7a) ---
    Action(
        type=ActionType.BE_ALONE,
        label="Stare da soli",
        duration_ticks=20,
        effects={
            NeedType.SOLITUDE: 70.0,
            NeedType.FUN: 10.0,
            NeedType.COMFORT: 10.0,
        },
    ),
    Action(
        type=ActionType.SELF_CARE,
        label="Prendersi cura di sé",
        duration_ticks=10,
        effects={
            NeedType.INTIMACY: 40.0,
            NeedType.COMFORT: 20.0,
            NeedType.FUN: 15.0,
        },
    ),
)


def action_of(action_type: ActionType) -> Action:
    """Ritorna l'azione canonica del tipo dato."""
    for action in ACTION_CATALOG:
        if action.type is action_type:
            return action
    raise ValueError(f"Azione sconosciuta: {action_type!r}")


__all__ = ["ACTION_CATALOG", "Action", "action_of"]
