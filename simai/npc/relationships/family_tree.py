"""FamilyTreeService — query sulla struttura familiare (parent/child)."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.npc.models import Character
from simai.npc.relationships.enums import RelationshipKind
from simai.npc.relationships.models import Relationship


class FamilyTreeService:
    """Query di navigazione familiare. Stateless: usare come namespace."""

    @staticmethod
    def parents_of(session: Session, character_id: int) -> list[Character]:
        """Genitori (chi ha `PARENT_OF` verso `character_id`)."""
        stmt = (
            select(Character)
            .join(Relationship, Relationship.from_id == Character.id)
            .where(
                Relationship.to_id == character_id,
                Relationship.kind == RelationshipKind.PARENT_OF.value,
            )
            .order_by(Character.id)
        )
        return list(session.scalars(stmt))

    @staticmethod
    def children_of(session: Session, character_id: int) -> list[Character]:
        """Figli (chi ha `PARENT_OF` da `character_id`)."""
        stmt = (
            select(Character)
            .join(Relationship, Relationship.to_id == Character.id)
            .where(
                Relationship.from_id == character_id,
                Relationship.kind == RelationshipKind.PARENT_OF.value,
            )
            .order_by(Character.id)
        )
        return list(session.scalars(stmt))

    @staticmethod
    def siblings_of(session: Session, character_id: int) -> list[Character]:
        """Fratelli/sorelle: chi condivide almeno un genitore, escluso sé stesso."""
        parents = FamilyTreeService.parents_of(session, character_id)
        if not parents:
            return []
        parent_ids = [p.id for p in parents]
        stmt = (
            select(Character)
            .join(Relationship, Relationship.to_id == Character.id)
            .where(
                Relationship.from_id.in_(parent_ids),
                Relationship.kind == RelationshipKind.PARENT_OF.value,
                Character.id != character_id,
            )
            .distinct()
            .order_by(Character.id)
        )
        return list(session.scalars(stmt))

    @staticmethod
    def ancestors_of(
        session: Session,
        character_id: int,
        *,
        max_gen: int = 5,
    ) -> dict[int, int]:
        """Mappa `{ancestor_id: distanza_minima}` fino a `max_gen` generazioni.

        Non include `character_id` stesso.
        """
        if max_gen < 1:
            raise ValueError(f"max_gen deve essere >= 1, ricevuto {max_gen}")
        result: dict[int, int] = {}
        frontier: set[int] = {character_id}
        for gen in range(1, max_gen + 1):
            next_frontier: set[int] = set()
            for fid in frontier:
                for parent in FamilyTreeService.parents_of(session, fid):
                    if parent.id not in result:
                        result[parent.id] = gen
                        next_frontier.add(parent.id)
            if not next_frontier:
                break
            frontier = next_frontier
        return result

    @staticmethod
    def descendants_of(
        session: Session,
        character_id: int,
        *,
        max_gen: int = 5,
    ) -> dict[int, int]:
        """Mappa `{discendente_id: distanza_minima}` fino a `max_gen` generazioni.

        Non include `character_id` stesso.
        """
        if max_gen < 1:
            raise ValueError(f"max_gen deve essere >= 1, ricevuto {max_gen}")
        result: dict[int, int] = {}
        frontier: set[int] = {character_id}
        for gen in range(1, max_gen + 1):
            next_frontier: set[int] = set()
            for fid in frontier:
                for child in FamilyTreeService.children_of(session, fid):
                    if child.id not in result:
                        result[child.id] = gen
                        next_frontier.add(child.id)
            if not next_frontier:
                break
            frontier = next_frontier
        return result


__all__ = ["FamilyTreeService"]
