from dataclasses import dataclass

from sqlalchemy.orm import Session

from simai.actions.catalog import ActionDef, actions_for_location
from simai.actions.enums import ActionKind
from simai.actions.utility import (
    filter_by_affordability,
    filter_by_need_threshold,
)
from simai.economy.enums import TransactionKind
from simai.economy.service import record_transaction
from simai.needs.enums import NeedKind
from simai.needs.service import apply_effect, needs_of
from simai.relationships.service import boost_social_relationship
from simai.sim.state import get_state
from simai.world.models import Character, Location


@dataclass(frozen=True)
class ActionResult:
    success: bool
    action: ActionKind
    character_id: int
    character_key: str
    location_key: str
    need_kind: NeedKind | None = None
    need_before: float | None = None
    need_after: float | None = None
    relationship_strength_after: float | None = None
    cost_paid: float = 0.0
    balance_after: float | None = None
    error: str | None = None


def _find_in(actions: list[ActionDef], action_kind: ActionKind) -> ActionDef | None:
    for a in actions:
        if a.kind == action_kind:
            return a
    return None


def do_action(session: Session, character_key: str, action_kind: ActionKind) -> ActionResult:
    """Esegue un'azione specifica per un personaggio.

    Valida, nell'ordine: personaggio, location, disponibilità
    dell'azione qui, soglia del bisogno, denaro sufficiente. Applica
    l'effetto sul bisogno, addebita il costo, registra la transaction,
    applica boost relazionale se SOCIALIZE. Non avanza il tempo.
    """
    char = session.query(Character).filter_by(key=character_key).one_or_none()
    if char is None:
        return ActionResult(
            success=False,
            action=action_kind,
            character_id=0,
            character_key=character_key,
            location_key="",
            error=f"Personaggio non trovato: {character_key}",
        )

    loc = session.get(Location, char.location_id)
    if loc is None:
        return ActionResult(
            success=False,
            action=action_kind,
            character_id=char.id,
            character_key=char.key,
            location_key="",
            error=f"Location non valida per {char.key}",
        )

    needs = needs_of(session, char.id)
    available = actions_for_location(loc.kind)
    available_by_need = filter_by_need_threshold(available, needs)
    available_now = filter_by_affordability(available_by_need, char.balance)

    action = _find_in(available_now, action_kind)
    if action is None:
        original_need = _find_in(available, action_kind)
        if original_need is None:
            names = [a.kind.value for a in available]
            return ActionResult(
                success=False,
                action=action_kind,
                character_id=char.id,
                character_key=char.key,
                location_key=loc.key,
                error=(
                    f"Azione '{action_kind.value}' non disponibile in "
                    f"'{loc.key}'. Disponibili: "
                    f"{', '.join(names) or 'nessuna'}."
                ),
            )

        if original_need not in available_by_need:
            current = needs.get(original_need.satisfies, 0.0)
            return ActionResult(
                success=False,
                action=action_kind,
                character_id=char.id,
                character_key=char.key,
                location_key=loc.key,
                error=(
                    f"Azione '{action_kind.value}' non necessaria: "
                    f"{original_need.satisfies.value}={current:.1f} "
                    f"(soglia {original_need.max_need_to_start:.0f})"
                ),
            )
        return ActionResult(
            success=False,
            action=action_kind,
            character_id=char.id,
            character_key=char.key,
            location_key=loc.key,
            error=(
                f"Azione '{action_kind.value}' costa "
                f"{original_need.cost:.1f} Athel, "
                f"ne hai {char.balance:.1f}"
            ),
        )

    before = needs.get(action.satisfies)
    after = apply_effect(session, char.id, action)

    cost_paid = 0.0
    if action.cost > 0:
        char.balance -= action.cost
        cost_paid = action.cost
        tick = get_state(session).tick_index
        record_transaction(
            session,
            tick_index=tick,
            amount=action.cost,
            kind=TransactionKind.PURCHASE,
            from_character_id=char.id,
            note=f"{action.kind.value} @ {loc.key}",
        )

    rel_after = boost_social_relationship(session, char.id, action)

    return ActionResult(
        success=True,
        action=action_kind,
        character_id=char.id,
        character_key=char.key,
        location_key=loc.key,
        need_kind=action.satisfies,
        need_before=before,
        need_after=after,
        relationship_strength_after=rel_after,
        cost_paid=cost_paid,
        balance_after=char.balance,
    )
