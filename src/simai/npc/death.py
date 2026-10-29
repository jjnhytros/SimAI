import random
from dataclasses import dataclass

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.economy.calendar import DAYS_PER_YEAR
from simai.npc.inheritance import InheritanceResult, distribute
from simai.world.enums import DeathCause
from simai.world.models import Character, Pregnancy

MAX_AGE_YEARS = 100
MORTALITY_BASE = 1e-5  # per anno, età 0
MORTALITY_MAX = 1.0 / 30.0  # per anno, età EXP_MAX_YEARS
EXP_MAX_YEARS = 100

DEATH_CAUSE_WEIGHTS: tuple[tuple[DeathCause, float], ...] = (
    (DeathCause.ILLNESS, 0.60),
    (DeathCause.ACCIDENT, 0.30),
    (DeathCause.VIOLENCE, 0.10),
)


@dataclass(frozen=True)
class KillResult:
    success: bool
    character_key: str
    cause: DeathCause
    inheritance: InheritanceResult | None
    error: str | None = None


def kill(
    session: Session,
    character_key: str,
    *,
    cause: DeathCause,
    tick_index: int,
) -> KillResult:
    """Rimuove il personaggio, distribuisce il balance, cancella relazioni.

    CASCADE DB su `Need`, `Moodlet`, `Job`, `Relationship`.
    `Transaction` ha `SET NULL`: restano con `from`/`to` nullo.
    """
    char = session.query(Character).filter_by(key=character_key).one_or_none()
    if char is None:
        return KillResult(
            success=False,
            character_key=character_key,
            cause=cause,
            inheritance=None,
            error=f"Personaggio non trovato: {character_key}",
        )

    # 0.1120: cancellazione esplicita gravidanze.
    # SQLite non enforce `ondelete=CASCADE` di default:
    # la FK di Pregnancy.character_id bloccherebbe il delete del
    # Character. Madre morente: la gravidanza non arriva a termine.
    # Padre morente: la gravidanza resta, ma senza partner.
    for pregnancy in session.scalars(
        select(Pregnancy).where(Pregnancy.character_id == char.id)
    ).all():
        session.delete(pregnancy)
    for pregnancy in session.scalars(
        select(Pregnancy).where(Pregnancy.partner_id == char.id)
    ).all():
        pregnancy.partner_id = None
    session.flush()

    inheritance = distribute(session, char, tick_index=tick_index)

    key = char.key
    session.delete(char)
    session.flush()
    logger.info(f"Character {key} killed ({cause.value})")

    return KillResult(
        success=True,
        character_key=key,
        cause=cause,
        inheritance=inheritance,
    )


def check_age(session: Session, tick_index: int) -> list[KillResult]:
    """Uccide i personaggi con `age_years >= MAX_AGE_YEARS`.

    Ritorna la lista dei kill eseguiti (di solito 0 o 1).
    """
    candidates = session.scalars(
        select(Character).where(Character.age_years >= MAX_AGE_YEARS)
    ).all()
    results: list[KillResult] = []
    for char in candidates:
        result = kill(
            session,
            char.key,
            cause=DeathCause.OLD_AGE,
            tick_index=tick_index,
        )
        results.append(result)
    return results


def probability_of_death(age_years: int) -> float:
    """Probabilità di morte per anno. Rampa cubica da base a max.

    A `age_years >= EXP_MAX_YEARS` ritorna 1.0 per safety, ma
    `check_probabilistic` salta chi ha >= 100 (OLD_AGE).
    """
    if age_years >= EXP_MAX_YEARS:
        return 1.0
    x: float = max(0, age_years) / EXP_MAX_YEARS
    return float(MORTALITY_BASE + (MORTALITY_MAX - MORTALITY_BASE) * (x**3))


def probability_of_death_per_day(age_years: int) -> float:
    """Conversione esatta da annuale a giornaliera.

    `daily_tick` gira una volta al giorno (tick % 28 == 0).
    """
    p_anno: float = probability_of_death(age_years)
    return float(1.0 - (1.0 - p_anno) ** (1.0 / DAYS_PER_YEAR))


def _roll_cause(rng: random.Random) -> DeathCause:
    r = rng.random()
    cum = 0.0
    for cause, w in DEATH_CAUSE_WEIGHTS:
        cum += w
        if r < cum:
            return cause
    return DeathCause.UNKNOWN


def check_probabilistic(session: Session, tick_index: int, *, master_seed: int) -> list[KillResult]:
    """Morte probabilistica per età. Deterministico via seed.

    Salta `age_years >= MAX_AGE_YEARS` (OLD_AGE, gestito da
    `check_age`). RNG isolato per char e tick.
    """
    characters = session.scalars(select(Character)).all()
    kills: list[KillResult] = []
    for char in characters:
        if char.age_years >= EXP_MAX_YEARS:
            continue
        p = probability_of_death_per_day(char.age_years)
        if p <= 0.0:
            continue
        rng = random.Random(f"simai:death:{master_seed}:{char.id}:{tick_index}")
        if rng.random() >= p:
            continue
        cause = _roll_cause(rng)
        result = kill(
            session,
            char.key,
            cause=cause,
            tick_index=tick_index,
        )
        kills.append(result)
    return kills
