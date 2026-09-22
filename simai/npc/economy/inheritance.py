"""InheritanceService — distribuzione dei beni alla morte.

Priorità eredi:
  1. SPOUSE_OF (con strength >= 0.5)
  2. Figli (PARENT_OF: deceased -> child)
  3. Genitori (PARENT_OF: parent -> deceased)
  4. Fratelli (genitori condivisi)
  5. Altri parenti (BFS su relazioni, esclusi ENEMY_OF/RIVAL_OF)

Regole:
  - Cash: 50% al coniuge (se presente), resto diviso in parti uguali tra
    figli/genitori/fratelli/altri. Se no coniuge: 100% diviso equamente.
  - Locations: indivisibili, assegnate al primo erede per priorità
    (il coniuge se presente, altrimenti il figlio più vecchio).
  - Oggetti: round-robin tra gli eredi (distribuzione equa).
  - Nessun erede: beni liquidi "bruciati" (SINK), oggetti/location a NULL.

**Ledger**: i movimenti di contante sono registrati tramite
`WealthService.transfer` / `WealthService.add` (SINK). Il residuo di
arrotondamento è bruciato con un SINK esplicito per mantenere
l'invariante `Σ signed_amount == 0` nel ledger.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.core.anthalys_datetime import AnthalysDateTime
from simai.economy.ledger import JournalEntryKind
from simai.npc.economy.enums import InheritanceTier
from simai.npc.economy.models import CharacterOwnedLocation
from simai.npc.economy.service import EconomyError, WealthService
from simai.npc.models import Character
from simai.npc.relationships.enums import RelationshipKind
from simai.npc.relationships.family_tree import FamilyTreeService
from simai.npc.relationships.models import Relationship
from simai.world.models import GameObject

#: Forza minima di una relazione SPOUSE_OF per contare come coniuge erede.
MIN_SPOUSE_STRENGTH: float = 0.5

#: Quota al coniuge (se presente) del patrimonio liquido.
SPOUSE_SHARE: float = 0.5


@dataclass(slots=True)
class InheritanceReport:
    """Esito di una distribuzione di eredità."""

    deceased_id: int
    heirs: dict[int, InheritanceTier] = field(default_factory=dict)
    cash_distributed: int = 0
    locations_assigned: int = 0
    objects_assigned: int = 0
    unclaimed: bool = False


class InheritanceService:
    """Servizio stateless di distribuzione ereditaria."""

    # ------------------------------------------------------------------
    # Finding heirs
    # ------------------------------------------------------------------

    @staticmethod
    def find_heirs(session: Session, deceased_id: int) -> dict[int, InheritanceTier]:
        """Mappa `{heir_id: tier}` ordinata per priorità (SPOUSE per primo)."""
        heirs: dict[int, InheritanceTier] = {}

        # 1. Coniugi (SPOUSE_OF)
        spouses = session.scalars(
            select(Relationship).where(
                Relationship.from_id == deceased_id,
                Relationship.kind == RelationshipKind.SPOUSE_OF.value,
                Relationship.strength >= MIN_SPOUSE_STRENGTH,
            )
        ).all()
        for r in spouses:
            spouse = session.get(Character, r.to_id)
            if spouse is not None and spouse.is_alive:
                heirs[spouse.id] = InheritanceTier.SPOUSE

        # 2. Figli
        for child in FamilyTreeService.children_of(session, deceased_id):
            if child.is_alive and child.id not in heirs:
                heirs[child.id] = InheritanceTier.CHILD

        # 3. Genitori
        for parent in FamilyTreeService.parents_of(session, deceased_id):
            if parent.is_alive and parent.id not in heirs:
                heirs[parent.id] = InheritanceTier.PARENT

        # 4. Fratelli
        for sib in FamilyTreeService.siblings_of(session, deceased_id):
            if sib.is_alive and sib.id not in heirs:
                heirs[sib.id] = InheritanceTier.SIBLING

        # 5. Altri parenti (BFS su relazioni, max 3 hop)
        if not heirs:
            for other in InheritanceService._distant_relatives(session, deceased_id, max_hops=3):
                if other.is_alive and other.id not in heirs:
                    heirs[other.id] = InheritanceTier.OTHER

        return heirs

    @staticmethod
    def _distant_relatives(
        session: Session, character_id: int, *, max_hops: int
    ) -> list[Character]:
        """BFS su relazioni "positive" (esclusi rivali/nemici)."""
        excluded_kinds = {
            RelationshipKind.ENEMY_OF.value,
            RelationshipKind.RIVAL_OF.value,
            RelationshipKind.EX_PARTNER_OF.value,
        }
        visited: set[int] = {character_id}
        frontier: set[int] = {character_id}
        result: list[Character] = []
        for _ in range(max_hops):
            next_frontier: set[int] = set()
            for fid in frontier:
                rows = session.scalars(
                    select(Relationship).where(
                        Relationship.from_id == fid,
                        Relationship.kind.not_in(excluded_kinds),
                    )
                ).all()
                for r in rows:
                    if r.to_id in visited:
                        continue
                    visited.add(r.to_id)
                    other = session.get(Character, r.to_id)
                    if other is not None:
                        result.append(other)
                        next_frontier.add(r.to_id)
            if not next_frontier:
                break
            frontier = next_frontier
        return result

    # ------------------------------------------------------------------
    # Distribution
    # ------------------------------------------------------------------

    @staticmethod
    def distribute(
        session: Session,
        *,
        deceased: Character,
        current_dt: AnthalysDateTime,
    ) -> InheritanceReport:
        """Distribuisce i beni del defunto. Ritorna il report."""
        heirs = InheritanceService.find_heirs(session, deceased.id)
        report = InheritanceReport(deceased_id=deceased.id, heirs=dict(heirs))

        if not heirs:
            # Nessun erede: brucia il contante, lascia oggetti/location a NULL
            current_balance = int(deceased.athel_balance)
            if current_balance > 0:
                WealthService.add(
                    session,
                    deceased,
                    -current_balance,
                    current_dt=current_dt,
                    kind=JournalEntryKind.SINK,
                    description="Eredità non reclamata (beni dissolti)",
                    reference_type="inheritance",
                    reference_id=deceased.id,
                )
            InheritanceService._release_all_objects(session, deceased.id)
            InheritanceService._release_all_locations(session, deceased.id)
            report.unclaimed = True
            session.flush()
            logger.info(
                "Eredità di char {} non reclamata (nessun erede): {} Athel dissolti",
                deceased.id,
                current_balance,
            )
            return report

        # Ordina eredi per priorità (SPOUSE prima, poi CHILD, ...)
        ordered = sorted(heirs.items(), key=lambda kv: kv[1].priority)

        # 1. Cash (via ledger)
        cash = int(deceased.athel_balance)
        if cash > 0:
            report.cash_distributed = InheritanceService._distribute_cash(
                session,
                deceased,
                ordered,
                cash,
                current_dt=current_dt,
            )

        # 2. Locations (indivisibili: al primo erede)
        locs = InheritanceService._owned_locations(session, deceased.id)
        if locs:
            primary_heir_id = ordered[0][0]
            for owned in locs:
                owned.character_id = primary_heir_id
                report.locations_assigned += 1
            session.flush()

        # 3. Oggetti (round-robin)
        objs = list(
            session.scalars(select(GameObject).where(GameObject.owner_character_id == deceased.id))
        )
        if objs:
            heir_ids = [hid for hid, _ in ordered]
            for i, obj in enumerate(objs):
                obj.owner_character_id = heir_ids[i % len(heir_ids)]
                report.objects_assigned += 1
            session.flush()

        logger.info(
            "Eredità di char {}: {} Athel, {} locations, {} oggetti, {} eredi",
            deceased.id,
            report.cash_distributed,
            report.locations_assigned,
            report.objects_assigned,
            len(heirs),
        )
        return report

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    @staticmethod
    def _distribute_cash(
        session: Session,
        deceased: Character,
        ordered_heirs: list[tuple[int, InheritanceTier]],
        cash: int,
        *,
        current_dt: AnthalysDateTime,
    ) -> int:
        """Divide `cash` secondo priorità. Ritorna l'importo distribuito.

        Regola: se c'è un coniuge, prende `SPOUSE_SHARE` (50%).
        Resto diviso tra tutti gli altri eredi (in parti uguali).
        Se no coniuge: 100% diviso tra tutti.

        Tutti i movimenti passano da `WealthService.transfer`, che posta
        una `JournalEntry` di tipo `TRANSFER` per ogni erede. Il residuo
        di arrotondamento viene bruciato con un `SINK`.
        """
        spouse_ids = [hid for hid, tier in ordered_heirs if tier is InheritanceTier.SPOUSE]
        others_ids = [hid for hid, tier in ordered_heirs if tier is not InheritanceTier.SPOUSE]

        distributions: list[tuple[int, int]] = []  # (heir_id, share)

        if spouse_ids and others_ids:
            spouse_pool = cash * SPOUSE_SHARE
            other_pool = cash - spouse_pool
            share_each = int(spouse_pool) // len(spouse_ids)
            for hid in spouse_ids:
                distributions.append((hid, share_each))
            if other_pool > 0:
                share_each = int(other_pool) // len(others_ids)
                remainder = int(other_pool) - share_each * len(others_ids)
                for i, hid in enumerate(others_ids):
                    extra = remainder if i == 0 else 0
                    distributions.append((hid, share_each + extra))
        else:
            all_ids = [hid for hid, _ in ordered_heirs]
            share_each = cash // len(all_ids)
            remainder = cash - share_each * len(all_ids)
            for i, hid in enumerate(all_ids):
                extra = remainder if i == 0 else 0
                distributions.append((hid, share_each + extra))

        # Esegui i trasferimenti (uno per erede)
        distributed = 0
        for hid, share in distributions:
            if share <= 0:
                continue
            heir = session.get(Character, hid)
            if heir is None:
                continue
            try:
                WealthService.transfer(
                    session,
                    sender=deceased,
                    receiver=heir,
                    amount=share,
                    current_dt=current_dt,
                    description=f"Eredità di {deceased.full_name}",
                    metadata={"deceased_id": deceased.id, "heir_id": hid},
                )
            except EconomyError as exc:
                logger.warning(
                    "Eredità: transfer fallito per heir={} share={}: {}",
                    hid,
                    share,
                    exc,
                )
                continue
            distributed += share

        # Residuo di arrotondamento: brucia
        residual = int(deceased.athel_balance)
        if residual > 0:
            WealthService.add(
                session,
                deceased,
                -residual,
                current_dt=current_dt,
                kind=JournalEntryKind.SINK,
                description="Eredità: residuo di arrotondamento",
                reference_type="inheritance",
                reference_id=deceased.id,
            )

        session.flush()
        return distributed

    @staticmethod
    def _owned_locations(session: Session, character_id: int) -> list[CharacterOwnedLocation]:
        return list(
            session.scalars(
                select(CharacterOwnedLocation).where(
                    CharacterOwnedLocation.character_id == character_id
                )
            )
        )

    @staticmethod
    def _release_all_objects(session: Session, character_id: int) -> None:
        objs = session.scalars(
            select(GameObject).where(GameObject.owner_character_id == character_id)
        )
        for obj in objs:
            obj.owner_character_id = None
        session.flush()

    @staticmethod
    def _release_all_locations(session: Session, character_id: int) -> None:
        rows = session.scalars(
            select(CharacterOwnedLocation).where(
                CharacterOwnedLocation.character_id == character_id
            )
        )
        for r in rows:
            session.delete(r)
        session.flush()


__all__ = [
    "MIN_SPOUSE_STRENGTH",
    "SPOUSE_SHARE",
    "InheritanceReport",
    "InheritanceService",
]
