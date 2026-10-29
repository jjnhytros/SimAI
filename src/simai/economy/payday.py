from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from simai.economy.calendar import TICKS_PER_DAY
from simai.economy.enums import JobTitle, TransactionKind
from simai.economy.models import Job
from simai.economy.service import record_transaction
from simai.npc.lifestage import is_pediatric, life_stage_for
from simai.world.models import Character, Location


@dataclass(frozen=True)
class PaydayReport:
    paid: int = 0
    absent: int = 0
    absent_keys: tuple[str, ...] = field(default_factory=tuple)


def _is_end_of_shift(tick_index: int, job: Job) -> bool:
    """True se il tick corrente è l'ultimo del turno del job."""
    t_in_day = tick_index % TICKS_PER_DAY
    return t_in_day == job.schedule_end_tick - 1


def _can_be_paid(char: Character, job: Job) -> bool:
    """Regola pagamento: STUDENTE sempre pagabile, altri solo se non pediatrici."""
    if job.title == JobTitle.STUDENTE:
        return True
    return not is_pediatric(life_stage_for(char.age_years))


def process_payday(session: Session, tick_index: int) -> PaydayReport:
    """Paga chi ha finito il turno e si trova sul posto.

    Per ogni job, al tick `schedule_end_tick - 1` del giorno:
    - se il personaggio è pediatrico non-STUDENTE, il job è sospeso:
      non viene pagato, ma non finisce in `absent_keys` (non è
      un'assenza, è un divieto).
    - se è nella location del lavoro, riceve il wage;
    - altrimenti finisce in `absent_keys`.
    """
    jobs = session.query(Job).all()
    paid = 0
    absent_keys: list[str] = []
    for job in jobs:
        if job.daily_wage <= 0:
            continue
        if not _is_end_of_shift(tick_index, job):
            continue
        char = session.get(Character, job.character_id)
        if char is None:
            continue
        if not _can_be_paid(char, job):
            continue
        loc = session.get(Location, char.location_id)
        if loc is None or loc.key != job.location_key:
            absent_keys.append(char.key)
            continue
        char.balance += job.daily_wage
        record_transaction(
            session,
            tick_index=tick_index,
            amount=job.daily_wage,
            kind=TransactionKind.SALARY,
            to_character_id=char.id,
            note=f"payday {job.title.value}",
        )
        paid += 1
    return PaydayReport(
        paid=paid,
        absent=len(absent_keys),
        absent_keys=tuple(absent_keys),
    )
