from enum import StrEnum

from simai.economy.calendar import TICKS_PER_DAY
from simai.economy.models import Job

PRIORITY_WINDOW = 2
CRITICAL_HUNGER_THRESHOLD = 10.0


class WorkState(StrEnum):
    NO_JOB = "no_job"
    BEFORE_WORK = "before_work"
    WORKING = "working"
    AFTER_WORK = "after_work"


def tick_in_day(tick_index: int) -> int:
    return tick_index % TICKS_PER_DAY


def work_state_for(job: Job | None, t_in_day: int) -> WorkState:
    if job is None:
        return WorkState.NO_JOB
    if t_in_day < job.schedule_start_tick:
        return WorkState.BEFORE_WORK
    if t_in_day < job.schedule_end_tick:
        return WorkState.WORKING
    return WorkState.AFTER_WORK


def should_prioritize_work(
    job: Job | None,
    t_in_day: int,
    hunger_value: float,
) -> bool:
    """La priorità lavoro copre tutto il turno, non solo l'inizio.

    - BEFORE_WORK: priorità solo entro `PRIORITY_WINDOW` tick.
    - WORKING: priorità sempre. L'NPC resta al lavoro.
    - AFTER_WORK: nessuna priorità.

    Salvaguardia: hunger < 10 → priorità decade. Meglio perdere un
    turno che morire di fame. Un NPC che lascia il posto durante il
    turno non prende lo stipendio.
    """
    if job is None:
        return False
    if hunger_value < CRITICAL_HUNGER_THRESHOLD:
        return False
    state = work_state_for(job, t_in_day)
    if state == WorkState.BEFORE_WORK:
        ticks_until = job.schedule_start_tick - t_in_day
        return ticks_until <= PRIORITY_WINDOW
    return state == WorkState.WORKING
