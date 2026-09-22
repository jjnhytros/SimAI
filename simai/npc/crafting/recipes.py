"""Ricette di crafting (definizioni statiche, lore-fixed)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final

from simai.npc.skills.enums import SkillType


@dataclass(frozen=True, slots=True)
class Recipe:
    """Definizione di una ricetta.

    - `output_type`: codice tipo dell'output (sarà il `GameObject.type`).
    - `output_name`: nome visualizzato.
    - `output_quantity`: quanti pezzi produce per craft.
    - `inputs`: mappa `{input_type: quantity}` consumata dall'inventario.
    - `required_skill`: skill primaria usata per il craft.
    - `min_skill_level`: livello minimo per tentare.
    - `duration_ticks`: durata dell'azione (informativa, non enforced qui).
    - `base_quality`: qualità base del craft a skill 0.
    - `skill_quality_bonus`: quanto la skill contribuisce alla qualità finale.
      Formula: `quality = base_quality + skill_quality_bonus × (level / MAX_LEVEL)`
      + jitter gaussiano.
    - `base_value`: valore di mercato base dell'output (Athel), per vendita.
    """

    code: str
    output_type: str
    output_name: str
    required_skill: SkillType
    inputs: dict[str, int] = field(default_factory=dict)
    output_quantity: int = 1
    min_skill_level: int = 0
    duration_ticks: int = 10
    base_quality: float = 0.35
    skill_quality_bonus: float = 0.55
    base_value: int = 10
    description: str = ""

    def __post_init__(self) -> None:
        if not (0.0 <= self.base_quality <= 1.0):
            raise ValueError(f"base_quality in [0, 1], ricevuto {self.base_quality}")
        if not (0.0 <= self.skill_quality_bonus <= 1.0):
            raise ValueError(f"skill_quality_bonus in [0, 1], ricevuto {self.skill_quality_bonus}")
        if self.output_quantity < 1:
            raise ValueError(f"output_quantity >= 1, ricevuto {self.output_quantity}")
        for k, v in self.inputs.items():
            if v < 1:
                raise ValueError(f"input '{k}' quantity >= 1, ricevuto {v}")


# ---------------------------------------------------------------------------
# Catalogo ricette
# ---------------------------------------------------------------------------

RECIPES: Final[dict[str, Recipe]] = {
    # ---- Cibo ----
    "make_bread": Recipe(
        code="make_bread",
        output_type="bread",
        output_name="Pane",
        required_skill=SkillType.COOKING,
        inputs={"flour": 2, "water": 1},
        base_value=2,
        duration_ticks=8,
        base_quality=0.40,
        skill_quality_bonus=0.50,
        description="Impastare e cuocere il pane.",
    ),
    "make_pastry": Recipe(
        code="make_pastry",
        output_type="pastry",
        output_name="Dolce",
        required_skill=SkillType.COOKING,
        inputs={"flour": 1, "sugar": 1, "butter": 1},
        min_skill_level=3,
        base_value=6,
        duration_ticks=12,
        base_quality=0.35,
        skill_quality_bonus=0.55,
        description="Dolce da forno con zucchero e burro.",
    ),
    # ---- Metallo ----
    "make_knife": Recipe(
        code="make_knife",
        output_type="knife",
        output_name="Coltello",
        required_skill=SkillType.CRAFTING,
        inputs={"iron_ingot": 2, "wood": 1},
        min_skill_level=4,
        base_value=25,
        duration_ticks=15,
        base_quality=0.30,
        skill_quality_bonus=0.60,
        description="Coltello forgiato a mano.",
    ),
    "make_tool": Recipe(
        code="make_tool",
        output_type="tool",
        output_name="Attrezzo",
        required_skill=SkillType.CRAFTING,
        inputs={"iron_ingot": 3, "wood": 2},
        min_skill_level=5,
        base_value=30,
        duration_ticks=18,
        base_quality=0.30,
        skill_quality_bonus=0.60,
        description="Attrezzo multiuso da lavoro.",
    ),
    "make_horseshoe": Recipe(
        code="make_horseshoe",
        output_type="horseshoe",
        output_name="Ferro di cavallo",
        required_skill=SkillType.CRAFTING,
        inputs={"iron_ingot": 1},
        min_skill_level=2,
        base_value=5,
        duration_ticks=6,
        base_quality=0.40,
        skill_quality_bonus=0.50,
        description="Ferro di cavallo forgiato.",
    ),
    # ---- Tessile ----
    "make_cloth": Recipe(
        code="make_cloth",
        output_type="cloth",
        output_name="Stoffa (rotolo)",
        required_skill=SkillType.CRAFTING,
        inputs={"fiber": 3},
        min_skill_level=2,
        base_value=8,
        duration_ticks=10,
        base_quality=0.35,
        skill_quality_bonus=0.55,
        description="Tessitura di fibra in stoffa.",
    ),
    "make_rope": Recipe(
        code="make_rope",
        output_type="rope",
        output_name="Corda",
        required_skill=SkillType.CRAFTING,
        inputs={"fiber": 3},
        min_skill_level=1,
        base_value=6,
        duration_ticks=8,
        base_quality=0.40,
        skill_quality_bonus=0.45,
        description="Intreccio di corda vegetale.",
    ),
    # ---- Consumabili ----
    "make_candle": Recipe(
        code="make_candle",
        output_type="candle",
        output_name="Candela",
        required_skill=SkillType.CRAFTING,
        inputs={"wax": 1, "string": 1},
        min_skill_level=1,
        base_value=2,
        duration_ticks=5,
        base_quality=0.45,
        skill_quality_bonus=0.40,
        description="Candela di cera e stoppino.",
    ),
    "make_soap": Recipe(
        code="make_soap",
        output_type="soap",
        output_name="Sapone",
        required_skill=SkillType.CRAFTING,
        inputs={"lye": 2, "fat": 1},
        min_skill_level=3,
        base_value=5,
        duration_ticks=10,
        base_quality=0.35,
        skill_quality_bonus=0.55,
        description="Saponificazione di grasso animale.",
    ),
    # ---- Medicina ----
    "make_potion_heal": Recipe(
        code="make_potion_heal",
        output_type="potion_heal",
        output_name="Pozione curativa",
        required_skill=SkillType.MEDICINE,
        inputs={"herb": 2, "water": 1},
        min_skill_level=4,
        base_value=20,
        duration_ticks=12,
        base_quality=0.30,
        skill_quality_bonus=0.65,
        description="Estratto curativo da erbe.",
    ),
}


def get_recipe(code: str) -> Recipe | None:
    """Ritorna la ricetta con il codice dato, o ``None``."""
    return RECIPES.get(code)


def all_recipes() -> list[Recipe]:
    """Lista di tutte le ricette, ordinate per skill + codice."""
    return sorted(RECIPES.values(), key=lambda r: (r.required_skill.value, r.code))


# ---------------------------------------------------------------------------
# Risorse (materie prime)
# ---------------------------------------------------------------------------

#: Codice tipo -> nome leggibile. Usato per seed e CLI.
RESOURCE_NAMES: Final[dict[str, str]] = {
    "flour": "Farina",
    "water": "Acqua",
    "sugar": "Zucchero",
    "butter": "Burro",
    "iron_ingot": "Lingotto di ferro",
    "wood": "Legno",
    "fiber": "Fibra",
    "wax": "Cera",
    "string": "Spago",
    "lye": "Lisciva",
    "fat": "Grasso animale",
    "herb": "Erba medicinale",
}

#: Prezzo base delle risorse (acquistabili dal fornitore di quartiere).
RESOURCE_PRICES: Final[dict[str, int]] = {
    "flour": 1,
    "water": 1,
    "sugar": 2,
    "butter": 2,
    "iron_ingot": 4,
    "wood": 2,
    "fiber": 2,
    "wax": 1,
    "string": 1,
    "lye": 1,
    "fat": 2,
    "herb": 3,
}


__all__ = [
    "RECIPES",
    "RESOURCE_NAMES",
    "RESOURCE_PRICES",
    "Recipe",
    "all_recipes",
    "get_recipe",
]
