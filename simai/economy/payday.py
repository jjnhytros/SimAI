"""PaydayService — pagamento periodico degli stipendi."""

from __future__ import annotations

from dataclasses import dataclass, field

from loguru import logger
from sqlalchemy.orm import Session

from simai.core.anthalys_datetime import AnthalysDateTime
from simai.economy.jobs import JobService
from simai.economy.ledger import JournalEntryKind
from simai.npc.economy.service import WealthService
from simai.npc.models import Character
from simai.npc.skills.enums import SkillType
from simai.npc.skills.service import SkillService

#: Intervallo (in giorni Anthalys) tra due payday.
PAYDAY_INTERVAL_DAYS: int = 7


@dataclass(slots=True)
class PaydayReport:
    """Esito di un payday."""

    paid_count: int = 0
    total_paid: int = 0
    total_taxed: int = 0
    character_ids: list[int] = field(default_factory=list)


class PaydayService:
    """Servizio stateless di pagamento stipendi."""

    @staticmethod
    def is_payday(day_index: int) -> bool:
        """``True`` se `day_index` è un giorno di paga.

        Regola: ogni `PAYDAY_INTERVAL_DAYS` giorni, escluso il giorno 0
        (inizio simulazione).
        """
        if day_index <= 0:
            return False
        return day_index % PAYDAY_INTERVAL_DAYS == 0

    @staticmethod
    def process(session: Session, current_dt: AnthalysDateTime) -> PaydayReport:
        """Esegue un payday: accredita `daily_wage × 7` a tutti gli occupati.

        Per ogni character:
          - calcola `effective_wage` (base + skill scaling).
          - accredita `effective_wage × 7` via `WealthService.add`
            (ledger `JournalEntryKind.SALARY`).
          - applica income tax (10%) e la versa al CityBudget.
        """
        report = PaydayReport()
        jobs = JobService.all_active_jobs(session)
        pay_amount_per_job = PAYDAY_INTERVAL_DAYS

        for job in jobs:
            character = session.get(Character, job.character_id)
            if character is None or not character.is_alive:
                continue

            # Skill-based wage scaling
            skill_level = 0
            if job.required_skill_type:
                try:
                    st = SkillType(job.required_skill_type)
                    skill = SkillService.get_skill(session, character.id, st)
                    if skill is not None:
                        skill_level = skill.level
                except ValueError:
                    pass

            effective = job.effective_daily_wage(skill_level)
            total = effective * pay_amount_per_job

            # 1. Accredita lo stipendio via ledger
            WealthService.add(
                session,
                character,
                total,
                current_dt=current_dt,
                kind=JournalEntryKind.SALARY,
                description=f"Stipendio ({job.title})",
                reference_type="job",
                reference_id=job.id,
                metadata={
                    "job_id": job.id,
                    "days": pay_amount_per_job,
                    "base_wage": int(job.daily_wage),
                    "effective_wage": effective,
                    "skill_level": skill_level,
                },
            )

            # 2. Income tax (10% del lordo versato alla città)
            from simai.city.tax import TaxService

            tax_result = TaxService.collect_income_tax(
                session,
                character=character,
                gross_income=total,
                current_dt=current_dt,
            )
            taxed = tax_result.amount if tax_result.ok else 0
            report.total_taxed += taxed

            report.paid_count += 1
            report.total_paid += total
            report.character_ids.append(character.id)

        session.flush()
        if report.paid_count > 0:
            logger.info(
                "Payday: {} stipendi pagati, {} Athel lordi, {} Athel tasse",
                report.paid_count,
                report.total_paid,
                report.total_taxed,
            )
        return report


__all__ = ["PAYDAY_INTERVAL_DAYS", "PaydayReport", "PaydayService"]
