from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.actions.catalog import ActionDef
from simai.needs.enums import NeedKind
from simai.needs.models import Need
from simai.npc.traits import trait_decay_multiplier
from simai.world.models import Character

VALUE_MIN = 0.0
VALUE_MAX = 100.0

DECAY_PER_HOUR: dict[NeedKind, float] = {
    NeedKind.HUNGER: 4.0,
    NeedKind.THIRST: 5.0,
    NeedKind.FUN: 3.0,
    NeedKind.INTIMACY: 1.5,
}


def clamp(value: float) -> float:
    return max(VALUE_MIN, min(VALUE_MAX, value))


def decay_value(
    value: float,
    kind: NeedKind,
    elapsed_minutes: int,
    traits: list[str] | None = None,
) -> float:
    """Decadimento per `kind`, modulato dai tratti.

    `traits=None` o lista vuota: nessun modificatore. I tratti
    moltiplicano il decadimento base per il bisogno toccato
    (es. LAZY: FUN × 1.30).
    """
    if elapsed_minutes <= 0:
        return clamp(value)
    multiplier = trait_decay_multiplier(traits, kind) if traits else 1.0
    rate_per_minute = DECAY_PER_HOUR[kind] * multiplier / 60.0
    return clamp(value - rate_per_minute * elapsed_minutes)


def apply_decay(
    session: Session,
    character_id: int,
    elapsed_minutes: int,
    traits: list[str] | None = None,
) -> dict[NeedKind, float]:
    """Applica il decadimento ai bisogni del personaggio.

    Se `traits` è None, li legge dal personaggio (comodo per i test
    esistenti). Se è passato esplicitamente, usa quelli (più
    efficiente in `run_tick`, che ha già caricato il personaggio).
    """
    if traits is None:
        char = session.get(Character, character_id)
        traits = list(char.traits) if char else []
    needs = session.scalars(select(Need).where(Need.character_id == character_id)).all()
    result: dict[NeedKind, float] = {}
    for need in needs:
        need.value = decay_value(need.value, need.kind, elapsed_minutes, traits)
        result[need.kind] = need.value
    return result


def ensure_initial_needs(session: Session, character_id: int) -> int:
    """Crea i bisogni mancanti per un personaggio."""
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


def apply_effect(
    session: Session,
    character_id: int,
    action: ActionDef,
) -> float:
    """Aumenta il bisogno soddisfatto da `action`, clampato a 100."""
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


def needs_of_many(session: Session, character_ids: list[int]) -> dict[int, dict[NeedKind, float]]:
    """Bisogni di più personaggi in una query.

    Ritorna `{character_id: {kind: value}}`. Character senza bisogni
    hanno `{}`, non assenza. Lista vuota → dict vuoto, zero query.
    """
    if not character_ids:
        return {}
    needs = session.scalars(select(Need).where(Need.character_id.in_(character_ids))).all()
    result: dict[int, dict[NeedKind, float]] = {cid: {} for cid in character_ids}
    for need in needs:
        result[need.character_id][need.kind] = need.value
    return result
