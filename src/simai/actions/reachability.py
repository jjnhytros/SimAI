from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.actions.catalog import ActionDef, actions_for_location
from simai.actions.enums import ActionKind
from simai.needs.enums import NeedKind
from simai.world.enums import LocationKind
from simai.world.models import Location


@dataclass(frozen=True)
class ReachableMove:
    """Una location raggiungibile per soddisfare un bisogno non coperto qui."""

    target_location_key: str
    target_location_kind: LocationKind
    satisfies: NeedKind
    need_value: float
    action_kind: ActionKind


def available_moves(
    session: Session,
    *,
    current_location_id: int,
    needs: dict[NeedKind, float],
    offers_by_key: dict[tuple[str, ActionKind], int] | None = None,
) -> list[ReachableMove]:
    """Calcola le location raggiungibili che sbloccherebbero un'azione.

    Una location è una meta valida se contiene almeno un'azione il cui
    bisogno è sotto `max_need_to_start`. In 1.0.1 la distanza è uniforme:
    il costo vive nell'utility (`DISTANCE_PENALTY`), non qui.

    `offers_by_key`: mappa `(location_key, action_kind) -> stock`.
    Se passata, le azioni con `cost > 0` e stock == 0 non generano
    move. Se `None`, comportamento legacy (nessun filtro stock) per
    retrocompatibilità con i test esistenti.
    """
    other_locations = session.scalars(
        select(Location).where(Location.id != current_location_id).order_by(Location.id)
    ).all()

    moves: list[ReachableMove] = []
    for loc in other_locations:
        for action in actions_for_location(loc.kind):
            value = needs.get(action.satisfies, 100.0)
            if value >= action.max_need_to_start:
                continue
            if offers_by_key is not None and action.cost > 0:
                stock = offers_by_key.get((loc.key, action.kind))
                if stock == 0:
                    continue
            moves.append(
                ReachableMove(
                    target_location_key=loc.key,
                    target_location_kind=loc.kind,
                    satisfies=action.satisfies,
                    need_value=value,
                    action_kind=action.kind,
                )
            )
    return moves


def filter_moves_by_affordability(
    moves: list[ReachableMove],
    balance: float,
    actions_by_location_kind: dict[LocationKind, list[ActionDef]],
) -> list[ReachableMove]:
    """Tiene solo i move verso location dove l'azione target è pagabile.

    `actions_by_location_kind` deve essere la mappa completa (da
    `actions_for_location` per ogni `LocationKind`). Non facciamo
    caching qui: il chiamante può preparare la mappa una volta e
    passarla. In 1.1.0 il catalogo è minuscolo, la performance non è
    un problema.
    """
    effective = max(0.0, balance)
    result: list[ReachableMove] = []
    for move in moves:
        candidates = actions_by_location_kind.get(move.target_location_kind, [])
        matching = [
            a for a in candidates if a.kind == move.action_kind and a.satisfies == move.satisfies
        ]
        if not matching:
            continue
        if all(a.cost <= effective for a in matching):
            result.append(move)
    return result
