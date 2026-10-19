from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.actions.catalog import ActionDef
from simai.needs.enums import NeedKind
from simai.needs.models import Need

VALUE_MIN = 0.0
VALUE_MAX = 100.0

# Quanto scende il valore in un'ora simulata.
DECAY_PER_HOUR: dict[NeedKind, float] = {
    NeedKind.HUNGER: 6.0,  # pieno -> zero in ~16h40'
    NeedKind.THIRST: 8.0,  # pieno -> zero in 12h30'
    NeedKind.FUN: 4.0,  # pieno -> zero in 25h
    NeedKind.INTIMACY: 2.0,  # pieno -> zero in 50h
}


def clamp(value: float) -> float:
    return max(VALUE_MIN, min(VALUE_MAX, value))


def decay_value(value: float, kind: NeedKind, elapsed_minutes: int) -> float:
    if elapsed_minutes <= 0:
        return clamp(value)
    rate_per_minute = DECAY_PER_HOUR[kind] / 60.0
    return clamp(value - rate_per_minute * elapsed_minutes)


def apply_decay(session: Session, character_id: int, elapsed_minutes: int) -> dict[NeedKind, float]:
    needs = session.scalars(select(Need).where(Need.character_id == character_id)).all()
    result: dict[NeedKind, float] = {}
    for need in needs:
        need.value = decay_value(need.value, need.kind, elapsed_minutes)
        result[need.kind] = need.value
    return result


def ensure_initial_needs(session: Session, character_id: int) -> int:
    """Crea i bisogni mancanti per un personaggio. Ritorna quanti creati."""
    existing = set(
        session.scalars(select(Need.kind).where(Need.character_id == character_id)).all()
    )
    created = 0
    for kind in NeedKind:
        if kind in existing:
            continue
        session.add(
            Need(
                character_id=character_id,
                kind=kind,
                value=VALUE_MAX,
            )
        )
        created += 1
    return created


def needs_of(session: Session, character_id: int) -> dict[NeedKind, float]:
    needs = session.scalars(select(Need).where(Need.character_id == character_id)).all()
    return {n.kind: n.value for n in needs}


def apply_effect(session: Session, character_id: int, action: ActionDef) -> float:
    """Aumenta il bisogno soddisfatto da `action`, clampato a 100.

    Ritorna il nuovo valore. Se il bisogno non esiste ritorna 0.0:
    non è un caso atteso in 1.0 ma va gestito senza eccezioni per non
    bloccare il tick.
    """
    need = session.scalar(
        select(Need).where(
            Need.character_id == character_id,
            Need.kind == action.satisfies,
        )
    )
    if need is None:
        return 0.0
    need.value = clamp(need.value + action.amount)
    return need.value
