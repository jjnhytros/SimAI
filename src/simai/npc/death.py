from dataclasses import dataclass

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.npc.inheritance import InheritanceResult, distribute
from simai.world.enums import DeathCause
from simai.world.models import Character

MAX_AGE_YEARS = 100


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
