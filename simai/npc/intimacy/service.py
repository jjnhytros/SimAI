"""IntimacyService — esegue azioni di intimità con consenso attivo."""

from __future__ import annotations

import random
from dataclasses import dataclass

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.core.anthalys_datetime import AnthalysDateTime
from simai.npc.identity import IdentityService
from simai.npc.identity.enums import TabooReaction
from simai.npc.intimacy.actions import IntimacyActionDef, get_intimacy_def
from simai.npc.intimacy.consent import ConsentResult, ConsentService
from simai.npc.intimacy.enums import IntimacyAction, IntimacyOutcome
from simai.npc.memory.enums import MemoryKind
from simai.npc.memory.service import MemoryService
from simai.npc.models import Character
from simai.npc.mood import Moodlet, MoodState
from simai.npc.needs.needs import Needs
from simai.npc.relationships.enums import RelationshipKind
from simai.npc.relationships.models import Relationship

#: Durata (tick) del moodlet di rifiuto.
REJECTION_MOODLET_DURATION: int = 100

#: Delta happiness del moodlet di rifiuto (sull'iniziatore).
REJECTION_MOODLET_DELTA: float = -0.15

#: Penalità di bond/strength dopo un rifiuto.
REJECTION_BOND_PENALTY: float = 0.02
REJECTION_STRENGTH_PENALTY: float = 0.01

#: Durata (tick) del moodlet post-successo.
SUCCESS_MOODLET_DURATION: int = 60


@dataclass(frozen=True, slots=True)
class IntimacyResult:
    """Esito di un'azione di intimità."""

    outcome: IntimacyOutcome
    action: IntimacyAction
    reason: str = ""
    memory_id: int | None = None
    consent: ConsentResult | None = None


class IntimacyService:
    """Servizio stateless di intimità (con consenso)."""

    # ------------------------------------------------------------------
    # Bond helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _bond_of(rel: Relationship) -> float:
        md = rel.metadata_json or {}
        try:
            return float(md.get("bond", 0.0))
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _set_bond(rel: Relationship, value: float) -> None:
        value = max(0.0, min(1.0, value))
        md = dict(rel.metadata_json or {})
        md["bond"] = value
        rel.metadata_json = md

    @staticmethod
    def _find_relationship(session: Session, a_id: int, b_id: int) -> Relationship | None:
        kinds = [
            k.value
            for k in (
                RelationshipKind.FRIEND_OF,
                RelationshipKind.BEST_FRIEND_OF,
                RelationshipKind.PARTNER_OF,
                RelationshipKind.SPOUSE_OF,
            )
        ]
        return session.scalars(
            select(Relationship).where(
                Relationship.from_id == a_id,
                Relationship.to_id == b_id,
                Relationship.kind.in_(kinds),
            )
        ).first()

    # ------------------------------------------------------------------
    # Preconditions
    # ------------------------------------------------------------------

    @staticmethod
    def can_perform(
        session: Session,
        initiator: Character,
        partner: Character,
        action: IntimacyAction,
    ) -> tuple[bool, str, Relationship | None, IntimacyActionDef | None]:
        """Verifica precondizioni (non consenso). Ritorna `(ok, reason, rel, def)`."""
        if initiator.id == partner.id:
            return False, "self", None, None
        if not initiator.is_alive or not partner.is_alive:
            return False, "not_alive", None, None

        try:
            def_ = get_intimacy_def(action)
        except KeyError:
            return False, "unknown_action", None, None

        rel = IntimacyService._find_relationship(session, initiator.id, partner.id)
        if rel is None:
            return False, "no_relationship", None, def_

        kind = RelationshipKind(rel.kind)
        if kind not in def_.allowed_kinds:
            return False, f"wrong_kind ({kind.value})", rel, def_
        # Consanguineità (Chunk 3.9a) — blocca azioni level >= 3
        if def_.level >= 3:
            from simai.npc.reputation import ReputationService

            if ReputationService.is_consanguineous(session, initiator.id, partner.id):
                # Verifica cultura: SEVERE -> blocco totale
                cult = IdentityService.get_culture(initiator)
                if cult.reaction_to_taboo is TabooReaction.SEVERE:
                    return False, "consanguinity_taboo", rel, def_

        if rel.strength < def_.min_strength:
            return False, f"strength_too_low ({rel.strength:.2f})", rel, def_

        bond = IntimacyService._bond_of(rel)
        if bond < def_.min_bond:
            return False, f"bond_too_low ({bond:.2f})", rel, def_

        initiator_traits = set(initiator.traits_json or [])
        for t in def_.blocked_traits:
            if t.value in initiator_traits:
                return False, f"trait_blocked ({t.value})", rel, def_

        return True, "ok", rel, def_

    # ------------------------------------------------------------------
    # Perform
    # ------------------------------------------------------------------

    @staticmethod
    def perform(
        session: Session,
        *,
        initiator: Character,
        partner: Character,
        action: IntimacyAction,
        current_dt: AnthalysDateTime,
        rng: random.Random,
        force: bool = False,
    ) -> IntimacyResult:
        """Esegue l'azione. Se `force=True`, salta il consenso (test)."""
        ok, reason, rel, def_ = IntimacyService.can_perform(session, initiator, partner, action)
        if not ok or rel is None or def_ is None:
            return IntimacyResult(
                outcome=IntimacyOutcome.NOT_ELIGIBLE,
                action=action,
                reason=reason,
            )

        # --- Consenso ---
        consent: ConsentResult | None = None
        if not force:
            consent = ConsentService.check(
                session,
                initiator=initiator,
                partner=partner,
                action_def=def_,
                rel=rel,
                current_dt=current_dt,
                rng=rng,
            )
            if not consent.accepted:
                IntimacyService._apply_rejection(
                    session,
                    initiator=initiator,
                    partner=partner,
                    rel=rel,
                    def_=def_,
                    current_dt=current_dt,
                )
                session.flush()
                return IntimacyResult(
                    outcome=IntimacyOutcome.REJECTED,
                    action=action,
                    reason=f"consent_denied (w={consent.willingness:.2f})",
                    consent=consent,
                )

        # --- Effetti positivi ---
        IntimacyService._apply_success(
            session,
            initiator=initiator,
            partner=partner,
            rel=rel,
            def_=def_,
            current_dt=current_dt,
        )
        session.flush()
        return IntimacyResult(
            outcome=IntimacyOutcome.SUCCESS,
            action=action,
            reason="ok",
            memory_id=None,  # popolato sotto
            consent=consent,
        )

    # ------------------------------------------------------------------
    # Effects
    # ------------------------------------------------------------------

    @staticmethod
    def _apply_success(
        session: Session,
        *,
        initiator: Character,
        partner: Character,
        rel: Relationship,
        def_: IntimacyActionDef,
        current_dt: AnthalysDateTime,
    ) -> None:
        """Applica gli effetti positivi di un'azione riuscita."""
        # 1. Needs (entrambi)
        for character in (initiator, partner):
            needs = (
                Needs.from_dict(character.needs_json) if character.needs_json else Needs.default()
            )
            for need, delta in def_.needs_effects.items():
                needs = needs.with_delta(need, delta)
            character.needs_json = needs.to_dict()

        # 2. Moodlets (entrambi)
        moodlet_name = f"Intimità ({def_.label})"
        for character in (initiator, partner):
            mood = MoodState.from_dict(character.mood_json or {})
            moodlet = Moodlet(
                name=moodlet_name,
                remaining_ticks=SUCCESS_MOODLET_DURATION,
                happiness_delta=def_.moodlets_delta,
                source=f"intimacy_{def_.action.value.lower()}",
            )
            new_mood = mood.tick(Needs.from_dict(character.needs_json or {}), (moodlet,))
            character.mood_json = new_mood.to_dict()

        # 3. Relazione: bond + strength
        new_bond = min(1.0, IntimacyService._bond_of(rel) + def_.bond_gain)
        IntimacyService._set_bond(rel, new_bond)
        rel.strength = min(1.0, rel.strength + def_.strength_gain)
        ConsentService.record_action(rel, action_def=def_, current_dt=current_dt)

        # 4. Reverse
        reverse = session.scalars(
            select(Relationship).where(
                Relationship.from_id == partner.id,
                Relationship.to_id == initiator.id,
                Relationship.kind == rel.kind,
            )
        ).first()
        if reverse is not None:
            IntimacyService._set_bond(reverse, new_bond)
            reverse.strength = rel.strength
            ConsentService.record_action(reverse, action_def=def_, current_dt=current_dt)

        # 5. Memoria (entrambi)
        text = f"{initiator.full_name} e {partner.full_name}: {def_.label}"
        MemoryService.record(
            session,
            owner_id=initiator.id,
            kind=MemoryKind.EMOTIONAL,
            text=text,
            current_dt=current_dt,
            valence=def_.memory_valence,
            saliency=def_.memory_saliency,
            participants=[partner.id],
            tags=["intimacy", def_.action.value.lower()],
            social_event=True,
        )
        MemoryService.record(
            session,
            owner_id=partner.id,
            kind=MemoryKind.EMOTIONAL,
            text=text,
            current_dt=current_dt,
            valence=def_.memory_valence,
            saliency=def_.memory_saliency,
            participants=[initiator.id],
            tags=["intimacy", def_.action.value.lower()],
            social_event=True,
        )

        # 6. Desire satisfied
        from simai.npc.desire import DesireService

        DesireService.mark_satisfied(initiator, current_dt)
        DesireService.mark_satisfied(partner, current_dt)

        # 7. Boredom reduction (azione "nuova" o "fresca")
        from simai.npc.relationships.boredom import BoredomService

        BoredomService.register_action(
            rel,
            action_value=def_.action.value,
            current_dt=current_dt,
        )
        if reverse is not None:
            BoredomService.register_action(
                reverse,
                action_value=def_.action.value,
                current_dt=current_dt,
            )

        # 8. Connection gain (Chunk 3.9c)
        from simai.npc.relationships.connection import ConnectionService

        ConnectionService.register_action(rel, action_def=def_)
        if reverse is not None:
            ConnectionService.register_action(reverse, action_def=def_)

        # 9. Social awareness (Chunk 3.12)
        from simai.npc.social_awareness import SocialAwarenessService

        rng_aware = __import__("random").Random(
            hash((initiator.id, partner.id, current_dt.to_total_seconds())) & 0xFFFFFFFF
        )
        SocialAwarenessService.record_interaction(
            initiator,
            partner,
            action_level=def_.level,
            rng=rng_aware,
        )
        SocialAwarenessService.record_interaction(
            partner,
            initiator,
            action_level=def_.level,
            rng=rng_aware,
        )

    @staticmethod
    def _apply_rejection(
        session: Session,
        *,
        initiator: Character,
        partner: Character,
        rel: Relationship,
        def_: IntimacyActionDef,
        current_dt: AnthalysDateTime,
    ) -> None:
        """Applica gli effetti negativi di un rifiuto."""
        # 1. Moodlet negativo sull'iniziatore
        mood = MoodState.from_dict(initiator.mood_json or {})
        moodlet = Moodlet(
            name="Rifiutato",
            remaining_ticks=REJECTION_MOODLET_DURATION,
            happiness_delta=REJECTION_MOODLET_DELTA,
            source=f"rejection_{def_.action.value.lower()}",
        )
        new_mood = mood.tick(Needs.from_dict(initiator.needs_json or {}), (moodlet,))
        initiator.mood_json = new_mood.to_dict()

        # 2. Penalità relazione (entrambe le direzioni)
        new_bond = max(0.0, IntimacyService._bond_of(rel) - REJECTION_BOND_PENALTY)
        IntimacyService._set_bond(rel, new_bond)
        rel.strength = max(0.0, rel.strength - REJECTION_STRENGTH_PENALTY)
        ConsentService.record_rejection(rel, current_dt=current_dt)

        reverse = session.scalars(
            select(Relationship).where(
                Relationship.from_id == partner.id,
                Relationship.to_id == initiator.id,
                Relationship.kind == rel.kind,
            )
        ).first()
        if reverse is not None:
            IntimacyService._set_bond(reverse, new_bond)
            reverse.strength = rel.strength
            ConsentService.record_rejection(reverse, current_dt=current_dt)

        # 3. Memoria negativa (solo iniziatore)
        MemoryService.record(
            session,
            owner_id=initiator.id,
            kind=MemoryKind.EMOTIONAL,
            text=f"Rifiuto da {partner.full_name}: {def_.label}",
            current_dt=current_dt,
            valence=-0.6,
            saliency=0.5,
            participants=[partner.id],
            tags=["intimacy", "rejection", def_.action.value.lower()],
            social_event=True,
        )

        logger.info(
            "Intimacy rifiutata: initiator={} partner={} action={}",
            initiator.id,
            partner.id,
            def_.action.value,
        )


__all__ = [
    "REJECTION_BOND_PENALTY",
    "REJECTION_MOODLET_DELTA",
    "REJECTION_MOODLET_DURATION",
    "REJECTION_STRENGTH_PENALTY",
    "SUCCESS_MOODLET_DURATION",
    "IntimacyResult",
    "IntimacyService",
]
