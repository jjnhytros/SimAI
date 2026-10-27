from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.actions.catalog import ActionDef
from simai.actions.enums import ActionKind
from simai.relationships.enums import RelationshipKind
from simai.relationships.models import Relationship
from simai.world.models import Character

STRENGTH_MIN = 0.0
STRENGTH_MAX = 100.0
SOCIALIZE_BOOST = 5.0


def clamp_strength(value: float) -> float:
    return max(STRENGTH_MIN, min(STRENGTH_MAX, value))


def relationships_of(session: Session, character_id: int) -> list[Relationship]:
    return list(
        session.scalars(
            select(Relationship)
            .where(Relationship.from_character_id == character_id)
            .order_by(Relationship.id)
        ).all()
    )


def ensure_relationship(
    session: Session,
    from_id: int,
    to_id: int,
    *,
    kind: RelationshipKind = RelationshipKind.FRIEND,
    strength: float = 50.0,
) -> Relationship | None:
    """Crea la relazione se non esiste. Ritorna None se già presente.

    Crea solo la direzione `from_id → to_id`: la simmetria è
    responsabilità del chiamante (di solito il seed).
    """
    existing = session.scalar(
        select(Relationship).where(
            Relationship.from_character_id == from_id,
            Relationship.to_character_id == to_id,
            Relationship.kind == kind,
        )
    )
    if existing is not None:
        return None
    rel = Relationship(
        from_character_id=from_id,
        to_character_id=to_id,
        kind=kind,
        strength=strength,
    )
    session.add(rel)
    return rel


_FAMILY_KINDS: frozenset[RelationshipKind] = frozenset(
    {RelationshipKind.PARENT_OF, RelationshipKind.CHILD_OF}
)


def boost_social_relationship(session: Session, actor_id: int, action: ActionDef) -> float | None:
    """Se `action` è SOCIALIZE, boost delle relazioni con personaggi
    presenti nella stessa location.

    Considera `FRIEND`, `PARENT_OF`, `CHILD_OF`. Per ogni relazione
    trovata applica `+SOCIALIZE_BOOST` bilaterale (se esiste il
    mirror). Ritorna il nuovo valore di strength della relazione più
    forte boostata, o None se nessun boost.
    """
    if action.kind != ActionKind.SOCIALIZE:
        return None

    actor = session.get(Character, actor_id)
    if actor is None:
        return None

    candidates = session.scalars(
        select(Relationship)
        .join(
            Character,
            Relationship.to_character_id == Character.id,
        )
        .where(
            Relationship.from_character_id == actor_id,
            Relationship.kind.in_((RelationshipKind.FRIEND, *_FAMILY_KINDS)),
            Character.location_id == actor.location_id,
        )
        .order_by(Relationship.strength.desc(), Relationship.id)
    ).all()
    if not candidates:
        return None

    best: Relationship | None = None
    for candidate in candidates:
        candidate.strength = clamp_strength(candidate.strength + SOCIALIZE_BOOST)
        mirror = session.scalar(
            select(Relationship).where(
                Relationship.from_character_id == candidate.to_character_id,
                Relationship.to_character_id == actor_id,
                Relationship.kind == candidate.kind,
            )
        )
        if mirror is not None:
            mirror.strength = clamp_strength(mirror.strength + SOCIALIZE_BOOST)
        if best is None or candidate.strength > best.strength:
            best = candidate
    return best.strength if best is not None else None
