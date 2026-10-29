from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.skills.enums import SkillKind
from simai.skills.models import Skill

SKILL_MIN = 0.0
SKILL_MAX = 100.0


def clamp_level(level: float) -> float:
    return max(SKILL_MIN, min(SKILL_MAX, level))


def skill_of(session: Session, character_id: int, kind: SkillKind) -> Skill | None:
    return session.scalar(
        select(Skill).where(
            Skill.character_id == character_id,
            Skill.kind == kind,
        )
    )


def skills_of(session: Session, character_id: int) -> list[Skill]:
    return list(
        session.scalars(
            select(Skill).where(Skill.character_id == character_id).order_by(Skill.kind)
        ).all()
    )


def level_of(session: Session, character_id: int, kind: SkillKind) -> float:
    """Livello della skill. 0.0 se manca (personaggio senza skill)."""
    skill = skill_of(session, character_id, kind)
    return float(skill.level) if skill is not None else 0.0


def wage_with_skill(daily_wage: float, skill_level: float) -> float:
    """Salario modulato dalla skill. +50% a livello 100.

    Il salario base è il minimo: skill 0 paga il base, skill 100
    paga +50%. Nessuna penalità per skill basse.
    """
    return float(daily_wage * (1.0 + clamp_level(skill_level) / 200.0))
