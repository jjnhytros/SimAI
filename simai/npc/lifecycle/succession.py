"""SuccessionService — orfani e tutori.

Quando entrambi i genitori di un minore muoiono, il minore è "orfano".
Il servizio cerca il parente adulto più prossimo (BFS su relazioni) e
lo registra come tutore in `character.attributes_json['guardian_id']`.

Nessuna nuova tabella: tutto in `attributes_json` per ora.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Final

from loguru import logger
from sqlalchemy.orm import Session

from simai.config.anthalys import SECONDS_PER_YEAR
from simai.core.anthalys_datetime import AnthalysDateTime
from simai.npc.lifestage_service import LifeStageService
from simai.npc.models import Character
from simai.npc.relationships.family_tree import FamilyTreeService
from simai.npc.relationships.service import relationships_of

#: Età (anni) sotto cui un Character è minorenne.
MINOR_AGE_YEARS: Final[int] = 25

#: Profondità massima della BFS per trovare un tutore.
MAX_GUARDIAN_SEARCH_DEPTH: Final[int] = 4

#: Numero massimo di nodi esplorati dalla BFS.
MAX_GUARDIAN_SEARCH_NODES: Final[int] = 500


@dataclass(frozen=True, slots=True)
class OrphanInfo:
    """Informazioni su un orfano registrato."""

    child_id: int
    guardian_id: int | None
    orphan_since_iso: str
    reason: str


class SuccessionService:
    """Registra orfani e assegna tutori. Stateless."""

    @staticmethod
    def process_deaths(
        session: Session,
        dead_ids: list[int],
        current_dt: AnthalysDateTime,
    ) -> list[OrphanInfo]:
        """Per ogni defunto, verifica i suoi figli minori.

        Se un figlio ha **tutti i genitori morti**, viene marcato orfano e
        (se possibile) gli viene assegnato un tutore.

        Ritorna la lista degli orfani **nuovi** (non già marcati).
        """
        orphans: list[OrphanInfo] = []
        seen_children: set[int] = set()

        for dead_id in dead_ids:
            children = FamilyTreeService.children_of(session, dead_id)
            for child in children:
                if child.id in seen_children:
                    continue
                seen_children.add(child.id)

                info = SuccessionService._check_orphan(session, child, current_dt)
                if info is not None:
                    orphans.append(info)

        if orphans:
            session.flush()
        return orphans

    @staticmethod
    def list_orphans(session: Session) -> list[Character]:
        """Tutti i Character con `attributes_json.orphan == True`."""
        all_chars = list(session.query(Character).all())
        return [
            c
            for c in all_chars
            if isinstance(c.attributes_json, dict) and c.attributes_json.get("orphan") is True
        ]

    @staticmethod
    def _check_orphan(
        session: Session,
        child: Character,
        current_dt: AnthalysDateTime,
    ) -> OrphanInfo | None:
        """Verifica se `child` è un nuovo orfano. Ritorna info o ``None``."""
        if not child.is_alive:
            return None

        # Già marcato?
        attrs = dict(child.attributes_json or {})
        if attrs.get("orphan") is True:
            return None

        # Minorenne?
        age_secs = LifeStageService.age_seconds_at(child.birth_total_seconds, current_dt)
        if age_secs // SECONDS_PER_YEAR >= MINOR_AGE_YEARS:
            return None

        # Genitori?
        parents = FamilyTreeService.parents_of(session, child.id)
        if not parents:
            return None
        # Almeno un genitore vivo?
        if any(p.is_alive for p in parents):
            return None

        # È orfano: cerca tutore
        guardian = SuccessionService._find_guardian(session, child.id, current_dt)
        iso = current_dt.to_iso_string()

        attrs["orphan"] = True
        attrs["orphan_since"] = iso
        attrs["guardian_id"] = guardian.id if guardian is not None else None
        child.attributes_json = attrs

        logger.info(
            "Orfano registrato: char={} guardian={} since={}",
            child.id,
            guardian.id if guardian is not None else "?",
            iso,
        )
        return OrphanInfo(
            child_id=child.id,
            guardian_id=guardian.id if guardian is not None else None,
            orphan_since_iso=iso,
            reason="both_parents_dead",
        )

    @staticmethod
    def _find_guardian(
        session: Session,
        child_id: int,
        current_dt: AnthalysDateTime,
    ) -> Character | None:
        """BFS su relazioni per trovare il parente adulto vivo più prossimo."""
        visited: set[int] = {child_id}
        frontier: deque[tuple[int, int]] = deque([(child_id, 0)])  # (id, depth)
        nodes_explored = 0

        while frontier and nodes_explored < MAX_GUARDIAN_SEARCH_NODES:
            current_id, depth = frontier.popleft()
            nodes_explored += 1

            if depth >= MAX_GUARDIAN_SEARCH_DEPTH:
                continue

            rels = relationships_of(session, current_id)
            for rel in rels:
                other_id = rel.to_id
                if other_id in visited:
                    continue
                visited.add(other_id)

                other = session.get(Character, other_id)
                if other is None or not other.is_alive:
                    continue

                age_secs = LifeStageService.age_seconds_at(other.birth_total_seconds, current_dt)
                if age_secs // SECONDS_PER_YEAR < MINOR_AGE_YEARS:
                    # Minorenne: può essere un tramite, non un tutore
                    frontier.append((other_id, depth + 1))
                    continue

                # Adulto vivo: candidato tutore
                return other

        return None


__all__ = [
    "MAX_GUARDIAN_SEARCH_DEPTH",
    "MAX_GUARDIAN_SEARCH_NODES",
    "MINOR_AGE_YEARS",
    "OrphanInfo",
    "SuccessionService",
]
