from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.relationships.enums import RelationshipKind
from simai.relationships.models import Relationship
from simai.world.models import Character


def _characters_via(
    session: Session,
    *,
    from_ids: list[int],
    kind: RelationshipKind,
    direction: str,
) -> list[Character]:
    """Ritorna i Character raggiunti da `from_ids` con `kind`.

    `direction="out"`: Relationship.from_character_id IN from_ids
    `direction="in"`:  Relationship.to_character_id IN from_ids
    """
    if not from_ids:
        return []
    if direction == "out":
        q = (
            select(Character)
            .join(
                Relationship,
                Relationship.to_character_id == Character.id,
            )
            .where(
                Relationship.from_character_id.in_(from_ids),
                Relationship.kind == kind,
            )
        )
    else:
        q = (
            select(Character)
            .join(
                Relationship,
                Relationship.from_character_id == Character.id,
            )
            .where(
                Relationship.to_character_id.in_(from_ids),
                Relationship.kind == kind,
            )
        )
    return list(session.scalars(q.order_by(Character.id)).all())


def parents_of(session: Session, character_id: int) -> list[Character]:
    """Genitori: chi ha `CHILD_OF` verso `character_id`."""
    return _characters_via(
        session,
        from_ids=[character_id],
        kind=RelationshipKind.CHILD_OF,
        direction="out",
    )


def children_of(session: Session, character_id: int) -> list[Character]:
    """Figli: chi ha `PARENT_OF` verso `character_id`."""
    return _characters_via(
        session,
        from_ids=[character_id],
        kind=RelationshipKind.PARENT_OF,
        direction="out",
    )


def siblings_of(session: Session, character_id: int) -> list[Character]:
    """Fratelli/sorelle: figli degli stessi genitori, escluso sé."""
    parents = parents_of(session, character_id)
    if not parents:
        return []
    parent_ids = [p.id for p in parents]
    half = _characters_via(
        session,
        from_ids=parent_ids,
        kind=RelationshipKind.PARENT_OF,
        direction="out",
    )
    seen: set[int] = set()
    result: list[Character] = []
    for c in half:
        if c.id == character_id or c.id in seen:
            continue
        seen.add(c.id)
        result.append(c)
    return result


def ancestors_of(session: Session, character_id: int) -> list[Character]:
    """BFS su `PARENT_OF` all'indietro, senza duplicati, ordine stabile."""
    seen: set[int] = {character_id}
    queue: list[int] = [character_id]
    result: list[Character] = []
    while queue:
        current = queue.pop(0)
        for parent in parents_of(session, current):
            if parent.id in seen:
                continue
            seen.add(parent.id)
            result.append(parent)
            queue.append(parent.id)
    result.sort(key=lambda c: c.id)
    return result


def descendants_of(session: Session, character_id: int) -> list[Character]:
    """BFS su `PARENT_OF` in avanti, senza duplicati, ordine stabile."""
    seen: set[int] = {character_id}
    queue: list[int] = [character_id]
    result: list[Character] = []
    while queue:
        current = queue.pop(0)
        for child in children_of(session, current):
            if child.id in seen:
                continue
            seen.add(child.id)
            result.append(child)
            queue.append(child.id)
    result.sort(key=lambda c: c.id)
    return result
