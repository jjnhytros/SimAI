"""PolyamoryService — poliamorosità e partner multipli."""

from __future__ import annotations

from typing import Final

from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.npc.identity import IdentityService
from simai.npc.identity.enums import TabooReaction
from simai.npc.models import Character
from simai.npc.relationships.enums import RelationshipKind
from simai.npc.relationships.models import Relationship
from simai.npc.traits.derivation import names_to_traits
from simai.npc.traits.enums import Trait

#: Soglia di permissiveness culturale per accettare poliamoria.
PERMISSIVENESS_THRESHOLD: Final[float] = 0.60

#: Soglia di openness per accettare partner multipli.
OPENNESS_THRESHOLD: Final[float] = 0.55


class PolyamoryService:
    """Servizio stateless per poliamorosità."""

    # ------------------------------------------------------------------
    # Eligibility
    # ------------------------------------------------------------------

    @staticmethod
    def accepts_polyamory(character: Character) -> bool:
        """``True`` se il character è aperto a relazioni multiple."""
        # Cultura permissiva
        culture = IdentityService.get_culture(character)
        if culture.permissiveness >= PERMISSIVENESS_THRESHOLD:
            return True
        if culture.reaction_to_taboo is TabooReaction.SEVERE:
            return False

        # Tratti
        traits = set(names_to_traits(character.traits_json or []))
        if Trait.SEXUALLY_EXPLORATIVE in traits:
            return True

        # Sexuality aperta
        sexuality = IdentityService.get_sexuality(character)
        openness = (sexuality.attraction_to_nonbinary + sexuality.romantic_vs_sexual) / 2.0
        return openness >= OPENNESS_THRESHOLD and culture.reaction_to_taboo is TabooReaction.LENIENT

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    @staticmethod
    def current_partners(session: Session, character_id: int) -> list[Character]:
        """Tutti i partner romantici attivi del character."""
        kinds = (
            RelationshipKind.PARTNER_OF.value,
            RelationshipKind.SPOUSE_OF.value,
        )
        rows = session.scalars(
            select(Relationship).where(
                Relationship.from_id == character_id,
                Relationship.kind.in_(kinds),
            )
        ).all()
        partners: list[Character] = []
        for rel in rows:
            p = session.get(Character, rel.to_id)
            if p is not None and p.is_alive:
                partners.append(p)
        return partners

    @staticmethod
    def has_partner(session: Session, character_id: int) -> bool:
        return len(PolyamoryService.current_partners(session, character_id)) > 0

    # ------------------------------------------------------------------
    # Validazione
    # ------------------------------------------------------------------

    @staticmethod
    def can_add_partner(
        session: Session,
        *,
        actor: Character,
        target: Character,
    ) -> tuple[bool, str]:
        """Verifica se actor può aggiungere target come partner.

        Regole:
          - Se nessuno dei due ha partner, OK.
          - Se uno dei due ha già partner:
              - entrambi devono accettare la poliamoria, OPPURE
              - il nuovo partner deve accettare la situazione (RNG non qui)
        """
        actor_partners = PolyamoryService.current_partners(session, actor.id)
        target_partners = PolyamoryService.current_partners(session, target.id)

        # Caso semplice: nessuno ha partner
        if not actor_partners and not target_partners:
            return True, "ok"

        # Deve essere poliamoroso
        if not PolyamoryService.accepts_polyamory(actor):
            return False, "actor_not_polyamorous"
        if not PolyamoryService.accepts_polyamory(target):
            return False, "target_not_polyamorous"

        # Compatibilità con partner esistenti (ridotta)
        # Non implementiamo conflitti specifici in questo chunk.
        return True, "polyamorous_ok"

    @staticmethod
    def is_polyamorous_relationship(rel: Relationship) -> bool:
        """``True`` se la relazione è marcata poliamorosa."""
        md = rel.metadata_json or {}
        return bool(md.get("polyamorous", False))

    @staticmethod
    def mark_polyamorous(rel: Relationship) -> None:
        """Marca una relazione come poliamorosa."""
        md = dict(rel.metadata_json or {})
        md["polyamorous"] = True
        rel.metadata_json = md


__all__ = [
    "OPENNESS_THRESHOLD",
    "PERMISSIVENESS_THRESHOLD",
    "PolyamoryService",
]
