from dataclasses import dataclass

from sqlalchemy.orm import Session

from simai.actions.catalog import ActionDef, actions_for_location
from simai.actions.enums import ActionKind
from simai.actions.utility import (
    filter_by_affordability,
    filter_by_need_threshold,
)
from simai.economy.enums import TransactionKind
from simai.economy.market import buy as market_buy
from simai.economy.market import filter_by_stock
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
    dell'azione qui, soglia del bisogno, denaro sufficiente, stock
    disponibile. Applica l'effetto sul bisogno, addebita il costo
    (via MarketService.buy se c'è un ShopItem, altrimenti fallback
    legacy), registra la transaction, applica boost relazionale se
    SOCIALIZE.
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
    available_by_money = filter_by_affordability(available_by_need, char.balance)
    available_now = filter_by_stock(session, available_by_money, loc.key)

    action = _find_in(available_now, action_kind)
    if action is None:
        original = _find_in(available, action_kind)
        if original is None:
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

        if original not in available_by_need:
            current = needs.get(original.satisfies, 0.0)
            return ActionResult(
                success=False,
                action=action_kind,
                character_id=char.id,
                character_key=char.key,
                location_key=loc.key,
                error=(
                    f"Azione '{action_kind.value}' non necessaria: "
                    f"{original.satisfies.value}={current:.1f} "
                    f"(soglia {original.max_need_to_start:.0f})"
                ),
            )

        if original not in available_by_money:
            return ActionResult(
                success=False,
                action=action_kind,
                character_id=char.id,
                character_key=char.key,
                location_key=loc.key,
                error=(
                    f"Azione '{action_kind.value}' costa "
                    f"{original.cost:.1f} Athel, "
                    f"ne hai {char.balance:.1f}"
                ),
            )

        return ActionResult(
            success=False,
            action=action_kind,
            character_id=char.id,
            character_key=char.key,
            location_key=loc.key,
            error=f"Azione '{action_kind.value}' esaurita in '{loc.key}'",
        )

    before = needs.get(action.satisfies)
    cost_paid = 0.0
    tick = get_state(session).tick_index

    if action.cost > 0:
        from simai.economy.market import offer_of

        if offer_of(session, loc.key, action.kind) is not None:
            purchase = market_buy(
                session,
                char,
                loc.key,
                action,
                tick_index=tick,
            )
            if not purchase.success:
                return ActionResult(
                    success=False,
                    action=action_kind,
                    character_id=char.id,
                    character_key=char.key,
                    location_key=loc.key,
                    error=purchase.error or "Acquisto fallito",
                )
            cost_paid = purchase.price_paid
        else:
            # Fallback legacy: nessun ShopItem, ma ActionDef.cost > 0.
            char.balance -= action.cost
            cost_paid = action.cost
            record_transaction(
                session,
                tick_index=tick,
                amount=action.cost,
                kind=TransactionKind.PURCHASE,
                from_character_id=char.id,
                note=f"{action.kind.value} @ {loc.key}",
            )

    after = apply_effect(session, char.id, action)
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
