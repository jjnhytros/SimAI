"""Enum e costanti del dominio abilità (skills)."""

from __future__ import annotations

from enum import StrEnum
from typing import Final


class SkillType(StrEnum):
    """Tipi di abilità disponibili.

    Professionali (10) — mappano 1:1 ai JobType.
    Generali (2) — cross-cutting, usate da azioni multiple.
    """

    # Professionali
    FARMING = "FARMING"
    CRAFTING = "CRAFTING"
    TRADING = "TRADING"
    TEACHING = "TEACHING"
    MEDICINE = "MEDICINE"
    COMBAT = "COMBAT"
    SERVICE = "SERVICE"
    ARTISTRY = "ARTISTRY"
    SCHOLARSHIP = "SCHOLARSHIP"
    LABOR = "LABOR"

    # Generali
    COOKING = "COOKING"
    SOCIALIZING = "SOCIALIZING"


#: Livello massimo raggiungibile.
MAX_SKILL_LEVEL: Final[int] = 20

#: Ritmo base di apprendimento (XP per tick di pratica, prima di talent/penalty).
XP_PER_TICK: Final[float] = 1.0

#: XP per salire dal livello L a L+1: `XP_BASE + XP_STEP * L`.
#: Totale per maxare (0→20): 115.000 XP.
#:
#: Stima: un NPC che pratica ~5% dei tick in 10 anni (1.45M tick)
#: accumula ~72.500 tick × 0.7 XP medi ≈ 50.000 XP -> livello 12-13.
XP_BASE: Final[int] = 1000
XP_STEP: Final[int] = 500

#: Penalità di apprendimento: `1.0 - (level/MAX) * 0.8`. A lvl 20 = 0.2.
LEVEL_PENALTY_MAX: Final[float] = 0.8

#: Giorni di inattività prima che il decay inizi.
DECAY_GRACE_DAYS: Final[int] = 60

#: Livelli persi per giorno di inattività (dopo la grazia).
DECAY_RATE_PER_DAY: Final[float] = 0.05

#: Talent di default per NPC creati prima dell'integrazione genetica (3.6c).
DEFAULT_TALENT: Final[float] = 1.0


#: Mapping skill -> famiglia genetica (per derivazione del talent, 3.6c).
#: I valori sono stringhe di `TraitFamily` (evita import ciclico).
SKILL_TALENT_FAMILY: Final[dict[SkillType, str]] = {
    SkillType.FARMING: "PHYSICAL",
    SkillType.CRAFTING: "CREATIVE",
    SkillType.TRADING: "SOCIAL",
    SkillType.TEACHING: "SOCIAL",
    SkillType.MEDICINE: "MENTAL",
    SkillType.COMBAT: "PHYSICAL",
    SkillType.SERVICE: "SOCIAL",
    SkillType.ARTISTRY: "CREATIVE",
    SkillType.SCHOLARSHIP: "MENTAL",
    SkillType.LABOR: "PHYSICAL",
    SkillType.COOKING: "CREATIVE",
    SkillType.SOCIALIZING: "SOCIAL",
}


__all__ = [
    "DECAY_GRACE_DAYS",
    "DECAY_RATE_PER_DAY",
    "DEFAULT_TALENT",
    "LEVEL_PENALTY_MAX",
    "MAX_SKILL_LEVEL",
    "SKILL_TALENT_FAMILY",
    "XP_BASE",
    "XP_PER_TICK",
    "XP_STEP",
    "SkillType",
]
