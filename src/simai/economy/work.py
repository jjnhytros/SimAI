from enum import StrEnum

from simai.economy.calendar import TICKS_PER_DAY
from simai.economy.enums import JobTitle
from simai.economy.models import Job
from simai.npc.lifestage import is_pediatric, life_stage_for

PRIORITY_WINDOW = 2
CRITICAL_HUNGER_THRESHOLD = 10.0
HOME_INTIMACY_THRESHOLD = 40.0
HOME_FUN_THRESHOLD = 40.0


class WorkState(StrEnum):
    NO_JOB = "no_job"
    BEFORE_WORK = "before_work"
    WORKING = "working"
    ON_BREAK = "on_break"
    AFTER_WORK = "after_work"


def tick_in_day(tick_index: int) -> int:
    return tick_index % TICKS_PER_DAY


def work_state_for(job: Job | None, t_in_day: int) -> WorkState:
    if job is None:
        return WorkState.NO_JOB
    if t_in_day < job.schedule_start_tick:
        return WorkState.BEFORE_WORK
    if t_in_day >= job.schedule_end_tick:
        return WorkState.AFTER_WORK
    if (
        job.break_start_tick is not None
        and job.break_end_tick is not None
        and job.break_start_tick <= t_in_day < job.break_end_tick
    ):
        return WorkState.ON_BREAK
    return WorkState.WORKING


def can_work(job: Job | None, age_years: int) -> bool:
    """True se il personaggio può svolgere questo lavoro.

    `JobTitle.STUDENTE` è esente: la paghetta non è salario.
    Per tutti gli altri job, i pediatrici (0–20 anni, `is_pediatric`)
    non possono lavorare.

    Se `job` è None, ritorna False (nessun lavoro da svolgere).
    """
    if job is None:
        return False
    if job.title == JobTitle.STUDENTE:
        return True
    return not is_pediatric(life_stage_for(age_years))


def should_prioritize_work(
    job: Job | None,
    t_in_day: int,
    hunger_value: float,
    *,
    age_years: int,
) -> bool:
    """Priorità lavoro: BEFORE_WORK entro finestra, WORKING sempre.
    ON_BREAK: nessuna priorità (l'NPC è libero). AFTER_WORK: nessuna.

    Salvaguardia: hunger < 10 → priorità decade.
    Divieto: pediatrici non-STUDENTE → priorità decade.
    """
    if not can_work(job, age_years):
        return False
    if hunger_value < CRITICAL_HUNGER_THRESHOLD:
        return False
    assert job is not None  # ridondante, ma mypy non lo sa
    state = work_state_for(job, t_in_day)
    if state == WorkState.BEFORE_WORK:
        ticks_until = job.schedule_start_tick - t_in_day
        return ticks_until <= PRIORITY_WINDOW
    return state == WorkState.WORKING


def should_prioritize_home(
    job: Job | None,
    t_in_day: int,
    home_key: str | None,
    current_key: str,
    intimacy: float,
    fun: float,
) -> bool:
    """Dopo il turno, torna a casa se ha già socializzato abbastanza.

    Evita il crollo delle relazioni: chi ha intimacy/fun bassi resta
    dove può socializzare, non torna a casa a isolarsi.

    Non controlla `can_work`: se il job è sospeso (pediatrico
    non-STUDENTE), l'NPC non ha "dopo il turno" e non torna a casa
    per quel motivo. Comportamento voluto.
    """
    if job is None or home_key is None:
        return False
    if current_key == home_key:
        return False
    state = work_state_for(job, t_in_day)
    if state != WorkState.AFTER_WORK:
        return False
    return intimacy >= HOME_INTIMACY_THRESHOLD and fun >= HOME_FUN_THRESHOLD
