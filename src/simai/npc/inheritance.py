from dataclasses import dataclass

from sqlalchemy.orm import Session

from simai.economy.enums import TransactionKind
from simai.economy.service import record_transaction
from simai.relationships.enums import RelationshipKind
from simai.relationships.family_tree import children_of, parents_of, siblings_of
from simai.relationships.service import relationships_of
from simai.world.models import Character

SPOUSE_SHARE = 0.50


@dataclass(frozen=True)
class InheritanceResult:
    tier: str
    total: float
    allocations: dict[str, float]
    to_world: float
    transaction_ids: tuple[int, ...]


def _spouse_of(session: Session, character_id: int) -> Character | None:
    for rel in relationships_of(session, character_id):
        if rel.kind != RelationshipKind.SPOUSE_OF:
            continue
        target = session.get(Character, rel.to_character_id)
        if target is not None:
            return target
    return None


def _heirs_for_tier(session: Session, character_id: int) -> tuple[str, list[Character]]:
    spouse = _spouse_of(session, character_id)
    if spouse is not None:
        return "spouse", [spouse]
    children = children_of(session, character_id)
    if children:
        return "child", children
    parents = parents_of(session, character_id)
    if parents:
        return "parent", parents
    siblings = siblings_of(session, character_id)
    if siblings:
        return "sibling", siblings
    return "other", []


def distribute(
    session: Session,
    deceased: Character,
    *,
    tick_index: int,
) -> InheritanceResult:
    """Distribuisce il balance del defunto.

    Ordine: SPOUSE (50%) > CHILD (resto equo) > PARENT > SIBLING >
    OTHER (world). Se il tier è SPOUSE, il 50% va al coniuge e il
    restante 50% ai figli (se ci sono); altrimenti tutto al tier.
    """
    if deceased.balance <= 0:
        return InheritanceResult(
            tier="none",
            total=0.0,
            allocations={},
            to_world=0.0,
            transaction_ids=(),
        )

    total = float(deceased.balance)
    allocations: dict[str, float] = {}
    transaction_ids: list[int] = []
    remaining = total

    tier, heirs = _heirs_for_tier(session, deceased.id)

    if tier == "spouse":
        spouse = heirs[0]
        share = total * SPOUSE_SHARE
        allocations[spouse.key] = share
        remaining -= share
        children = children_of(session, deceased.id)
        if children and remaining > 0:
            per_child = remaining / len(children)
            for child in children:
                allocations[child.key] = allocations.get(child.key, 0.0) + per_child
            remaining = 0.0
        elif remaining > 0:
            allocations[spouse.key] += remaining
            remaining = 0.0
    elif heirs:
        per_heir = total / len(heirs)
        for heir in heirs:
            allocations[heir.key] = per_heir
        remaining = 0.0

    to_world = remaining

    for key, amount in allocations.items():
        heir = session.query(Character).filter_by(key=key).one()
        heir.balance += amount
        tx = record_transaction(
            session,
            tick_index=tick_index,
            amount=amount,
            kind=TransactionKind.OTHER,
            from_character_id=None,
            to_character_id=heir.id,
            note=f"succession from {deceased.key}",
        )
        session.flush()
        transaction_ids.append(tx.id)

    if to_world > 0:
        tx = record_transaction(
            session,
            tick_index=tick_index,
            amount=to_world,
            kind=TransactionKind.OTHER,
            from_character_id=None,
            to_character_id=None,
            note=f"succession no heir for {deceased.key}",
        )
        session.flush()
        transaction_ids.append(tx.id)

    deceased.balance = 0.0

    return InheritanceResult(
        tier=tier,
        total=total,
        allocations=allocations,
        to_world=to_world,
        transaction_ids=tuple(transaction_ids),
    )
