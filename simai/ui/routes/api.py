"""Route API JSON (per D3, htmx, Chart.js)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.npc.models import Character
from simai.npc.relationships.enums import RelationshipKind
from simai.npc.relationships.models import Relationship
from simai.ui.deps import get_db

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/npcs/{character_id}/tree.json")
def npc_tree_json(
    character_id: int,
    session: Session = Depends(get_db),
) -> dict[str, Any]:
    """Albero genealogico (3 generazioni) come nodi + link per D3.

    Include: nonni, genitori, target, figli, nipoti.
    """
    target = session.get(Character, character_id)
    if target is None:
        raise HTTPException(status_code=404, detail=f"NPC {character_id} non trovato")

    # BFS a profondità 3 in entrambe le direzioni
    visited: dict[int, int] = {target.id: 0}  # id -> depth
    frontier: set[int] = {target.id}
    for _ in range(3):
        next_frontier: set[int] = set()
        for cid in frontier:
            for direction in ("from", "to"):
                if direction == "from":
                    stmt = select(Relationship).where(
                        Relationship.from_id == cid,
                        Relationship.kind == RelationshipKind.PARENT_OF.value,
                    )
                else:
                    stmt = select(Relationship).where(
                        Relationship.to_id == cid,
                        Relationship.kind == RelationshipKind.PARENT_OF.value,
                    )
                for r in session.scalars(stmt):
                    other = r.to_id if direction == "from" else r.from_id
                    if other not in visited:
                        visited[other] = visited[cid] + 1
                        next_frontier.add(other)
        if not next_frontier:
            break
        frontier = next_frontier

    # Nodi
    nodes: list[dict[str, Any]] = []
    for cid, depth in visited.items():
        c = session.get(Character, cid)
        if c is None:
            continue
        nodes.append(
            {
                "id": cid,
                "name": c.full_name,
                "sex": c.sex,
                "alive": c.is_alive,
                "birth_iso": c.birth_iso,
                "depth": depth,
                "is_target": cid == character_id,
            }
        )

    # Link (solo padre-figlio, evitiamo duplicati simmetrici)
    links: list[dict[str, Any]] = []
    ids_in_tree = set(visited.keys())
    parent_edges = session.scalars(
        select(Relationship).where(Relationship.kind == RelationshipKind.PARENT_OF.value)
    )
    for r in parent_edges:
        if r.from_id in ids_in_tree and r.to_id in ids_in_tree:
            links.append({"source": r.from_id, "target": r.to_id})

    return {"nodes": nodes, "links": links}


@router.get("/stats/population.json")
def population_stats_json(
    session: Session = Depends(get_db),
) -> dict[str, Any]:
    """Statistiche popolazione (per chart)."""
    from sqlalchemy import func

    alive = int(
        session.scalar(
            select(func.count()).select_from(Character).where(Character.is_alive.is_(True))
        )
        or 0
    )
    dead = int(
        session.scalar(
            select(func.count()).select_from(Character).where(Character.is_alive.is_(False))
        )
        or 0
    )
    rows = session.execute(
        select(Character.sex, func.count())
        .where(Character.is_alive.is_(True))
        .group_by(Character.sex)
    ).all()
    by_sex: dict[str, int] = {str(sex): int(count) for sex, count in rows}
    return {"alive": alive, "dead": dead, "by_sex": by_sex}
