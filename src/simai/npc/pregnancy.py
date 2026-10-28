import random
from dataclasses import dataclass

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.needs.service import ensure_initial_needs
from simai.relationships.enums import RelationshipKind
from simai.relationships.family_tree import children_of
from simai.relationships.service import ensure_relationship
from simai.world.models import Character, Pregnancy

PREGNANCY_DAYS = 300
TWINS_IDENTICAL_PROB = 0.015
TWINS_FRATERNAL_PROB = 0.30


@dataclass(frozen=True)
class ConceiveResult:
    success: bool
    pregnancy_id: int | None = None
    due_at_tick: int | None = None
    error: str | None = None


@dataclass(frozen=True)
class DeliverResult:
    success: bool
    pregnancy_id: int | None = None
    children_keys: tuple[str, ...] = ()
    error: str | None = None


def roll_twins(rng: random.Random) -> tuple[int, bool]:
    """Ritorna `(numero_figli, identici)`.

    - 68.5%: 1 figlio
    - 1.5%: 2 gemelli identici
    - 30%: 2 gemelli fraterni

    `identical` è calcolato ma non usato in 1.8.0: i `traits` dei
    nuovi nati sono `[]` per tutti (nessuna genetica).
    """
    r = rng.random()
    if r < TWINS_IDENTICAL_PROB:
        return 2, True
    if r < TWINS_IDENTICAL_PROB + TWINS_FRATERNAL_PROB:
        return 2, False
    return 1, False


def conceive(
    session: Session,
    character_key: str,
    partner_key: str,
    *,
    tick_index: int,
    master_seed: int,
) -> ConceiveResult:
    """Crea una gravidanza. Valida età >= 18, partner esistente,
    nessuna gravidanza già in corso."""
    parent = session.query(Character).filter_by(key=character_key).one_or_none()
    if parent is None:
        return ConceiveResult(success=False, error=f"Personaggio non trovato: {character_key}")
    partner = session.query(Character).filter_by(key=partner_key).one_or_none()
    if partner is None:
        return ConceiveResult(success=False, error=f"Partner non trovato: {partner_key}")
    if parent.age_years < 18:
        return ConceiveResult(
            success=False,
            error=f"{character_key} ha {parent.age_years} anni, minimo 18",
        )
    existing = session.scalar(select(Pregnancy).where(Pregnancy.character_id == parent.id))
    if existing is not None:
        return ConceiveResult(
            success=False,
            error=f"{character_key} ha già una gravidanza in corso",
        )

    due = tick_index + PREGNANCY_DAYS * 28
    pregnancy = Pregnancy(
        character_id=parent.id,
        partner_id=partner.id,
        conceived_at_tick=tick_index,
        due_at_tick=due,
    )
    session.add(pregnancy)
    session.flush()
    return ConceiveResult(
        success=True,
        pregnancy_id=pregnancy.id,
        due_at_tick=due,
    )


def _next_child_index(session: Session, parent_id: int) -> int:
    """Contatore per la key: `_child_1`, `_child_2`, ..."""
    existing = children_of(session, parent_id)
    return len(existing) + 1


def deliver(
    session: Session,
    pregnancy: Pregnancy,
    *,
    master_seed: int,
) -> DeliverResult:
    """Crea 1 o 2 `Character`, `Need`, `PARENT_OF`/`CHILD_OF`.
    Rimuove la `Pregnancy`. Nessuna `Transaction`.
    """
    parent = session.get(Character, pregnancy.character_id)
    if parent is None:
        return DeliverResult(
            success=False,
            pregnancy_id=pregnancy.id,
            error=f"Genitore {pregnancy.character_id} non trovato",
        )
    partner = (
        session.get(Character, pregnancy.partner_id) if pregnancy.partner_id is not None else None
    )

    rng = random.Random(f"simai:{master_seed}:{parent.id}:{pregnancy.conceived_at_tick}:birth")
    n_children, _identical = roll_twins(rng)

    start = _next_child_index(session, parent.id)
    keys: list[str] = []
    for i in range(n_children):
        child_key = f"{parent.key}_child_{start + i}"
        child = Character(
            key=child_key,
            name=f"Figlio di {parent.name}",
            age_years=0,
            age_days=0,
            is_player=False,
            balance=0.0,
            location_id=parent.location_id,
            home_location_id=parent.home_location_id,
            traits=[],
        )
        session.add(child)
        session.flush()
        ensure_initial_needs(session, child.id)

        ensure_relationship(
            session,
            parent.id,
            child.id,
            kind=RelationshipKind.PARENT_OF,
            strength=80.0,
        )
        ensure_relationship(
            session,
            child.id,
            parent.id,
            kind=RelationshipKind.CHILD_OF,
            strength=80.0,
        )
        if partner is not None:
            ensure_relationship(
                session,
                partner.id,
                child.id,
                kind=RelationshipKind.PARENT_OF,
                strength=80.0,
            )
            ensure_relationship(
                session,
                child.id,
                partner.id,
                kind=RelationshipKind.CHILD_OF,
                strength=80.0,
            )
        keys.append(child_key)

    session.delete(pregnancy)
    session.flush()
    logger.info(f"Pregnancy {pregnancy.id} delivered: {keys}")
    return DeliverResult(
        success=True,
        pregnancy_id=pregnancy.id,
        children_keys=tuple(keys),
    )


def due_pregnancies(session: Session, tick_index: int) -> list[Pregnancy]:
    return list(session.scalars(select(Pregnancy).where(Pregnancy.due_at_tick <= tick_index)).all())
