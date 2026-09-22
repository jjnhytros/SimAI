"""Package `simai.npc.skills` — abilità degli NPC.

Contenuto:
  - `SkillType` — 12 tipi (10 professionali + 2 generali)
  - `Skill` — modello SQLAlchemy
  - `SkillService` — learning, progress, decay
  - `SkillDecay`, `LevelUpResult` — dataclass di risultato
"""

from simai.npc.skills.enums import (
    DECAY_GRACE_DAYS,
    DECAY_RATE_PER_DAY,
    DEFAULT_TALENT,
    LEVEL_PENALTY_MAX,
    MAX_SKILL_LEVEL,
    SKILL_TALENT_FAMILY,
    XP_BASE,
    XP_PER_TICK,
    XP_STEP,
    SkillType,
)
from simai.npc.skills.models import Skill
from simai.npc.skills.service import LevelUpResult, SkillDecay, SkillService
from simai.npc.skills.talent import (
    TALENT_MAX,
    TALENT_MIN,
    talent_for_skill,
    talent_map_for_genome,
)

__all__ = [
    "DECAY_GRACE_DAYS",
    "DECAY_RATE_PER_DAY",
    "DEFAULT_TALENT",
    "LEVEL_PENALTY_MAX",
    "MAX_SKILL_LEVEL",
    "SKILL_TALENT_FAMILY",
    "TALENT_MAX",
    "TALENT_MIN",
    "XP_BASE",
    "XP_PER_TICK",
    "XP_STEP",
    "LevelUpResult",
    "Skill",
    "SkillDecay",
    "SkillService",
    "SkillType",
    "talent_for_skill",
    "talent_map_for_genome",
]
