"""JobService — assunzione, licenziamento, query impieghi."""

from __future__ import annotations

from dataclasses import dataclass

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.core.anthalys_datetime import AnthalysDateTime
from simai.economy.enums import DEFAULT_WAGES, JobType
from simai.economy.models import Job
from simai.npc.models import Character
from simai.npc.skills.enums import SkillType
from simai.npc.skills.service import SkillService
from simai.world.models import Location


class JobError(Exception):
    """Errore su operazioni di impiego."""


@dataclass(frozen=True, slots=True)
class JobAssignment:
    """Esito di un'assegnazione di lavoro."""

    job_id: int
    character_id: int
    job_type: JobType
    daily_wage: int
    workplace_id: int | None


class JobService:
    """Servizio stateless di gestione impieghi."""

    @staticmethod
    def job_of(session: Session, character_id: int) -> Job | None:
        """Ritorna il Job attivo del character, o ``None``."""
        return session.scalars(
            select(Job).where(
                Job.character_id == character_id,
                Job.is_active.is_(True),
            )
        ).first()

    @staticmethod
    def assign(
        session: Session,
        *,
        character: Character,
        job_type: JobType,
        title: str,
        workplace: Location | None = None,
        daily_wage: int | None = None,
        current_dt: AnthalysDateTime,
        required_skill_type: SkillType | None = None,
        min_skill_level: int = 0,
        wage_skill_scale: float = 0.05,
        promotion_skill_level: int = 10,
        promoted_title: str | None = None,
    ) -> Job:
        """Assegna un lavoro.

        Se `required_skill_type` è valorizzato, verifica che il character
        abbia il livello minimo. Altrimenti solleva `JobError`.

        Il wage è scalato: `effective = daily_wage * (1 + wage_skill_scale * skill_level)`.
        """
        if not character.is_alive:
            raise JobError(f"Character {character.id} non è vivo")

        existing = JobService.job_of(session, character.id)
        if existing is not None:
            raise JobError(f"Character {character.id} ha già un lavoro attivo ({existing.title})")

        if daily_wage is None:
            daily_wage = DEFAULT_WAGES.get(job_type, 5)
        if daily_wage <= 0:
            raise JobError(f"daily_wage deve essere > 0, ricevuto {daily_wage}")
        if min_skill_level < 0:
            raise JobError(f"min_skill_level deve essere >= 0, ricevuto {min_skill_level}")
        if wage_skill_scale < 0:
            raise JobError(f"wage_skill_scale deve essere >= 0, ricevuto {wage_skill_scale}")

        # Verifica skill
        if required_skill_type is not None and min_skill_level > 0:
            skill = SkillService.get_skill(session, character.id, required_skill_type)
            current_level = skill.level if skill is not None else 0
            if current_level < min_skill_level:
                raise JobError(
                    f"Character {character.id} non ha "
                    f"{required_skill_type.value} >= {min_skill_level} "
                    f"(attuale: {current_level})"
                )

        job = Job(
            character_id=character.id,
            workplace_id=workplace.id if workplace is not None else None,
            job_type=job_type.value,
            title=title,
            daily_wage=daily_wage,
            since_total_seconds=current_dt.to_total_seconds(),
            is_active=True,
            required_skill_type=(required_skill_type.value if required_skill_type else None),
            min_skill_level=min_skill_level,
            wage_skill_scale=wage_skill_scale,
            promotion_skill_level=promotion_skill_level,
            promoted_title=promoted_title,
            metadata_json={},
        )
        session.add(job)
        session.flush()
        logger.info(
            "Job assegnato: char={} type={} wage={}/day skill_req={} promotion_at={}",
            character.id,
            job_type.value,
            daily_wage,
            required_skill_type.value if required_skill_type else "—",
            promotion_skill_level,
        )
        return job

    @staticmethod
    def quit(session: Session, character_id: int) -> bool:
        """Disattiva il job del character. Ritorna True se c'era."""
        job = JobService.job_of(session, character_id)
        if job is None:
            return False
        job.is_active = False
        session.flush()
        return True

    @staticmethod
    def all_active_jobs(session: Session) -> list[Job]:
        """Tutti i Job attivi."""
        return list(session.scalars(select(Job).where(Job.is_active.is_(True))))


__all__ = ["JobAssignment", "JobError", "JobService"]
