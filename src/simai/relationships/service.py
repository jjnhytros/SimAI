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


def boost_social_relationship(session: Session, actor_id: int, action: ActionDef) -> float | None:
    """Se `action` è SOCIALIZE, boost della relazione più forte con un
    personaggio presente nella stessa location.

    Ritorna il nuovo valore di strength (lato attore) o None se
    nessun boost è avvenuto (azione non SOCIALIZE, o nessun FRIEND
    presente localmente).
    """
    if action.kind != ActionKind.SOCIALIZE:
        return None

    actor = session.get(Character, actor_id)
    if actor is None:
        return None

    candidate = session.scalar(
        select(Relationship)
        .join(
            Character,
            Relationship.to_character_id == Character.id,
        )
        .where(
            Relationship.from_character_id == actor_id,
            Relationship.kind == RelationshipKind.FRIEND,
            Character.location_id == actor.location_id,
        )
        .order_by(Relationship.strength.desc(), Relationship.id)
    )
    if candidate is None:
        return None

    candidate.strength = clamp_strength(candidate.strength + SOCIALIZE_BOOST)

    mirror = session.scalar(
        select(Relationship).where(
            Relationship.from_character_id == candidate.to_character_id,
            Relationship.to_character_id == actor_id,
            Relationship.kind == RelationshipKind.FRIEND,
        )
    )
    if mirror is not None:
        mirror.strength = clamp_strength(mirror.strength + SOCIALIZE_BOOST)

    return candidate.strength
