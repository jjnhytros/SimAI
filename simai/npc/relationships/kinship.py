"""Kinship — coefficiente di relazione e nome della relazione.

Coefficiente di relazione (r):
  r(a, b) = Σ over simple paths a↔b di 0.5^(path_length)

Dove i path sono nel grafo **non diretto** parent-child (ogni persona è
collegata ai suoi genitori e ai suoi figli). I path sono "simple"
(nessun nodo ripetuto), e la lunghezza è il numero di archi.

Risultati attesi (per famiglie non consanguinee):
  - Parent-child      : 0.5
  - Siblings          : 0.5
  - Grandparent-GC    : 0.25
  - Uncle-nephew      : 0.25
  - First cousins     : 0.125
  - Second cousins    : 0.03125
"""

from __future__ import annotations

from typing import Final

from sqlalchemy.orm import Session

from simai.npc.relationships.family_tree import FamilyTreeService

#: Profondità massima (generazioni) per la ricerca dei path.
DEFAULT_MAX_GEN: Final[int] = 6

#: Numero massimo di path da enumerare (protezione anti-esplosione).
DEFAULT_MAX_PATHS: Final[int] = 5000


# ---------------------------------------------------------------------------
# Coefficiente di relazione
# ---------------------------------------------------------------------------


def _neighbors(session: Session, character_id: int) -> list[int]:
    """Adiacenti nel grafo non diretto (genitori + figli)."""
    parents = FamilyTreeService.parents_of(session, character_id)
    children = FamilyTreeService.children_of(session, character_id)
    return [p.id for p in parents] + [c.id for c in children]


def _find_simple_paths(
    session: Session,
    start_id: int,
    end_id: int,
    *,
    max_gen: int,
    max_paths: int,
) -> list[tuple[int, ...]]:
    """Enumera i path simple da `start_id` a `end_id`, max `max_gen` archi."""
    paths: list[tuple[int, ...]] = []

    def dfs(current: int, path: list[int]) -> None:
        if len(paths) >= max_paths:
            return
        if current == end_id:
            paths.append(tuple(path))
            return
        if len(path) > max_gen + 1:
            return
        for n in _neighbors(session, current):
            if n not in path:
                path.append(n)
                dfs(n, path)
                path.pop()

    dfs(start_id, [start_id])
    return paths


def relationship_coefficient(
    session: Session,
    a_id: int,
    b_id: int,
    *,
    max_gen: int = DEFAULT_MAX_GEN,
    max_paths: int = DEFAULT_MAX_PATHS,
) -> float:
    """Coefficiente di relazione r(a, b) in [0, 1].

    - `a_id == b_id`: ritorna 1.0 (self).
    - Nessun path trovato entro `max_gen`: ritorna 0.0 (non imparentati).
    - Altrimenti: `Σ 0.5^(lunghezza_path)`.
    """
    if a_id == b_id:
        return 1.0
    paths = _find_simple_paths(session, a_id, b_id, max_gen=max_gen, max_paths=max_paths)
    return sum(0.5 ** (len(p) - 1) for p in paths)


def kinship_coefficient(
    session: Session,
    a_id: int,
    b_id: int,
    *,
    max_gen: int = DEFAULT_MAX_GEN,
    max_paths: int = DEFAULT_MAX_PATHS,
) -> float:
    """Coefficiente di kinship Φ(a, b) = r(a, b) / 2 (per individui non consanguinei)."""
    return relationship_coefficient(session, a_id, b_id, max_gen=max_gen, max_paths=max_paths) / 2.0


# ---------------------------------------------------------------------------
# Nome della relazione
# ---------------------------------------------------------------------------

_ASCENDANT_NAMES: Final[dict[int, str]] = {
    1: "genitore",
    2: "nonno/a",
    3: "bisnonno/a",
    4: "trisnonno/a",
    5: "quadrisnonno/a",
}

_DESCENDANT_NAMES: Final[dict[int, str]] = {
    1: "figlio/a",
    2: "nipote (discendente)",
    3: "bisnipote",
    4: "trisnipote",
    5: "quadrisnipote",
}


def relationship_name(
    session: Session,
    a_id: int,
    b_id: int,
    *,
    max_gen: int = DEFAULT_MAX_GEN,
) -> str:
    """Nome qualitativo della relazione tra `a` e `b` (dal punto di vista di a)."""
    if a_id == b_id:
        return "self"

    anc_a = FamilyTreeService.ancestors_of(session, a_id, max_gen=max_gen)
    anc_b = FamilyTreeService.ancestors_of(session, b_id, max_gen=max_gen)

    # Aggiungi self a distanza 0 per gestire casi diretti (parent/child)
    set_a = {a_id} | set(anc_a.keys())
    set_b = {b_id} | set(anc_b.keys())

    common = set_a & set_b
    if not common:
        return "non imparentati"

    # Distanze relative
    def d(char_id: int, anc_id: int, anc_map: dict[int, int]) -> int:
        if char_id == anc_id:
            return 0
        return anc_map.get(anc_id, 10**6)

    # Trova l'antenato comune più vicino (min d_a + d_b)
    best_anc = min(common, key=lambda c: d(a_id, c, anc_a) + d(b_id, c, anc_b))
    da = d(a_id, best_anc, anc_a)
    db = d(b_id, best_anc, anc_b)

    return _name_from_distances(da, db)


def _name_from_distances(da: int, db: int) -> str:
    if da == 0 and db == 0:
        return "self"
    if da == 0:
        return _ASCENDANT_NAMES.get(db, f"antenato ({db} gen.)")
    if db == 0:
        return _DESCENDANT_NAMES.get(da, f"discendente ({da} gen.)")

    # Entrambi > 0: relazione "laterale"
    if da == 1 and db == 1:
        return "fratello/sorella"
    if da == 1 and db == 2:
        return "zio/a"
    if da == 2 and db == 1:
        return "nipote (di zio)"
    if da == 2 and db == 2:
        return "cugino/a di primo grado"
    if da == 1 and db == 3:
        return "prozio/a"
    if da == 3 and db == 1:
        return "pronipote"
    if (da == 2 and db == 3) or (da == 3 and db == 2):
        return "cugino/a di secondo grado"
    if da == 3 and db == 3:
        return "cugino/a di terzo grado"
    if da >= 4 and db >= 4:
        return f"parente lontano (d={da}+{db})"
    return f"parente (d={da}+{db})"


__all__ = [
    "DEFAULT_MAX_GEN",
    "DEFAULT_MAX_PATHS",
    "kinship_coefficient",
    "relationship_coefficient",
    "relationship_name",
]
