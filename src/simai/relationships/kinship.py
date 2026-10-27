from sqlalchemy.orm import Session

from simai.relationships.enums import RelationshipKind
from simai.relationships.family_tree import (
    children_of,
    parents_of,
    siblings_of,
)
from simai.relationships.service import relationships_of

# Coefficiente di parentela r per grado. Oltre grado 3: 0.0
# (path-based esteso in 1.8.0).
_R_BY_DEGREE: dict[int, float] = {
    1: 0.5,
    2: 0.25,
    3: 0.125,
}


def _degree(session: Session, from_id: int, to_id: int) -> int | None:
    """Grado di parentela tra due personaggi, o None se non consanguinei.

    Grado 1: genitore, figlio, fratello.
    Grado 2: nonno, nipote (di nonno), zio, nipote (di zio).
    Grado 3: cugino primo, prozio, pronipote.
    Oltre: None (0.0).
    """
    if from_id == to_id:
        return 0

    # Grado 1: genitore/figlio diretto.
    for parent in parents_of(session, from_id):
        if parent.id == to_id:
            return 1
    for child in children_of(session, from_id):
        if child.id == to_id:
            return 1
    # Grado 1: fratello.
    for sibling in siblings_of(session, from_id):
        if sibling.id == to_id:
            return 1

    # Grado 2: nonno (genitore di genitore), o nipote (figlio di
    # fratello).
    for parent in parents_of(session, from_id):
        for grandparent in parents_of(session, parent.id):
            if grandparent.id == to_id:
                return 2
    for child in children_of(session, from_id):
        for grandchild in children_of(session, child.id):
            if grandchild.id == to_id:
                return 2
    for sibling in siblings_of(session, from_id):
        for nephew in children_of(session, sibling.id):
            if nephew.id == to_id:
                return 2
    for parent in parents_of(session, from_id):
        for uncle in siblings_of(session, parent.id):
            if uncle.id == to_id:
                return 2

    # Grado 3: cugino primo (figlio di zio).
    for parent in parents_of(session, from_id):
        for uncle in siblings_of(session, parent.id):
            for cousin in children_of(session, uncle.id):
                if cousin.id == to_id:
                    return 3

    return None


def relationship_coefficient(session: Session, from_id: int, to_id: int) -> float:
    """r = 0.5^grado. Oltre grado 3: 0.0.

    Path > 3 gradi (cugini secondi, prozio, ...) restituisce 0.0.
    Documentato in `known-issues.md` §8.
    """
    degree = _degree(session, from_id, to_id)
    if degree is None or degree == 0:
        return 0.0
    return _R_BY_DEGREE.get(degree, 0.0)


def kinship_coefficient(session: Session, from_id: int, to_id: int) -> float:
    """r / 2. Convenzione semplificata (TODO §3.3)."""
    return relationship_coefficient(session, from_id, to_id) / 2.0


def relationship_name(session: Session, from_id: int, to_id: int) -> str:
    """Nome italiano neutro della relazione.

    Neutro perché `Character.gender` non esiste. "genitore" invece di
    "madre/padre", "figlio/a", "fratello/sorella", ecc.
    """
    if from_id == to_id:
        return "sé"

    # Kind diretti.
    for rel in relationships_of(session, from_id):
        if rel.to_character_id != to_id:
            continue
        if rel.kind == RelationshipKind.PARENT_OF:
            return "genitore"
        if rel.kind == RelationshipKind.CHILD_OF:
            return "figlio/a"
        if rel.kind == RelationshipKind.SIBLING_OF:
            return "fratello/sorella"
        if rel.kind == RelationshipKind.SPOUSE_OF:
            return "coniuge"
        if rel.kind == RelationshipKind.EX_PARTNER_OF:
            return "ex partner"
        if rel.kind == RelationshipKind.FRIEND:
            return "amico/a"
        if rel.kind == RelationshipKind.GRANDPARENT_OF:
            return "nonno/a"
        if rel.kind == RelationshipKind.GRANDCHILD_OF:
            return "nipote (di nonno)"
        if rel.kind == RelationshipKind.UNCLE_AUNT_OF:
            return "zio/a"
        if rel.kind == RelationshipKind.NEPHEW_NIECE_OF:
            return "nipote (di zio)"
        if rel.kind == RelationshipKind.COUSIN_OF:
            return "cugino/a"

    # Deduzione dal grado, se non c'è kind diretto.
    degree = _degree(session, from_id, to_id)
    if degree is None:
        return "sconosciuto"
    return {
        1: "consanguineo (grado 1)",
        2: "consanguineo (grado 2)",
        3: "consanguineo (grado 3)",
    }.get(degree, "sconosciuto")
