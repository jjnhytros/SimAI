"""RelationshipService — CRUD su `Relationship`."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.npc.models import Character
from simai.npc.relationships.enums import RelationshipKind
from simai.npc.relationships.models import Relationship


class RelationshipError(Exception):
    """Errore di validazione su una relazione."""


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------


def create_relationship(
    session: Session,
    *,
    from_id: int,
    to_id: int,
    kind: RelationshipKind,
    strength: float = 0.5,
    since_total_seconds: int | None = None,
    metadata: dict[str, Any] | None = None,
) -> list[Relationship]:
    """Crea una relazione. Per le simmetriche, crea 2 righe speculari.

    Ritorna la lista delle righe create (1 o 2).
    Solleva `RelationshipError` se:
      - `from_id == to_id`
      - una delle due `Character` non esiste
      - la relazione esiste già
    """
    if from_id == to_id:
        raise RelationshipError("Una relazione richiede due character distinti")
    if not (0.0 <= strength <= 1.0):
        raise RelationshipError(f"strength deve essere in [0, 1], ricevuto {strength}")

    # Verifica esistenza
    for cid, label in ((from_id, "from_id"), (to_id, "to_id")):
        if session.get(Character, cid) is None:
            raise RelationshipError(f"{label}={cid} non esiste")

    # Duplicato?
    existing = session.scalars(
        select(Relationship).where(
            Relationship.from_id == from_id,
            Relationship.to_id == to_id,
            Relationship.kind == kind.value,
        )
    ).first()
    if existing is not None:
        raise RelationshipError(f"Relazione {kind.value} {from_id}->{to_id} già esistente")

    md = dict(metadata or {})
    created: list[Relationship] = []

    fwd = Relationship(
        from_id=from_id,
        to_id=to_id,
        kind=kind.value,
        strength=strength,
        since_total_seconds=since_total_seconds,
        metadata_json=md,
    )
    session.add(fwd)
    created.append(fwd)

    if kind.is_symmetric:
        rev = Relationship(
            from_id=to_id,
            to_id=from_id,
            kind=kind.value,
            strength=strength,
            since_total_seconds=since_total_seconds,
            metadata_json=dict(md),
        )
        session.add(rev)
        created.append(rev)

    session.flush()
    return created


def delete_relationship(
    session: Session,
    *,
    from_id: int,
    to_id: int,
    kind: RelationshipKind,
) -> int:
    """Elimina una relazione (entrambe le direzioni se simmetrica).

    Ritorna il numero di righe eliminate (0 se non trovata).
    """
    deleted = 0
    rows = list(
        session.scalars(
            select(Relationship).where(
                Relationship.from_id == from_id,
                Relationship.to_id == to_id,
                Relationship.kind == kind.value,
            )
        )
    )
    for r in rows:
        session.delete(r)
        deleted += 1
    if kind.is_symmetric:
        reverse_rows = list(
            session.scalars(
                select(Relationship).where(
                    Relationship.from_id == to_id,
                    Relationship.to_id == from_id,
                    Relationship.kind == kind.value,
                )
            )
        )
        for r in reverse_rows:
            session.delete(r)
            deleted += 1
    session.flush()
    return deleted


# ---------------------------------------------------------------------------
# Query
# ---------------------------------------------------------------------------


def relationships_of(
    session: Session,
    character_id: int,
    *,
    kind: RelationshipKind | None = None,
) -> list[Relationship]:
    """Tutte le relazioni uscenti da `character_id` (eventualmente filtrate)."""
    stmt = select(Relationship).where(Relationship.from_id == character_id)
    if kind is not None:
        stmt = stmt.where(Relationship.kind == kind.value)
    stmt = stmt.order_by(Relationship.kind, Relationship.to_id)
    return list(session.scalars(stmt))


def related_characters(
    session: Session,
    character_id: int,
    *,
    kind: RelationshipKind | None = None,
) -> list[Character]:
    """Character collegati a `character_id` da relazioni uscenti."""
    rels = relationships_of(session, character_id, kind=kind)
    if not rels:
        return []
    ids = [r.to_id for r in rels]
    chars = list(session.scalars(select(Character).where(Character.id.in_(ids))))
    by_id = {c.id: c for c in chars}
    return [by_id[r.to_id] for r in rels if r.to_id in by_id]


def relationship_exists(
    session: Session,
    *,
    from_id: int,
    to_id: int,
    kind: RelationshipKind,
) -> bool:
    """``True`` se la relazione esiste in direzione `from→to`."""
    row = session.scalars(
        select(Relationship).where(
            Relationship.from_id == from_id,
            Relationship.to_id == to_id,
            Relationship.kind == kind.value,
        )
    ).first()
    return row is not None


__all__ = [
    "RelationshipError",
    "create_relationship",
    "delete_relationship",
    "related_characters",
    "relationship_exists",
    "relationships_of",
]
