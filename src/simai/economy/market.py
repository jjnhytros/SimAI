from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.actions.catalog import ActionDef
from simai.actions.enums import ActionKind
from simai.economy.enums import TransactionKind
from simai.economy.models import ShopItem
from simai.economy.service import record_transaction
from simai.world.models import Character


@dataclass(frozen=True)
class PurchaseResult:
    success: bool
    price_paid: float = 0.0
    stock_before: int = 0
    stock_after: int = 0
    balance_after: float = 0.0
    transaction_id: int | None = None
    error: str | None = None


def offer_of(session: Session, location_key: str, action_kind: ActionKind) -> ShopItem | None:
    return session.scalar(
        select(ShopItem).where(
            ShopItem.location_key == location_key,
            ShopItem.action_kind == action_kind,
        )
    )


def stock_of(session: Session, location_key: str, action_kind: ActionKind) -> int | None:
    offer = offer_of(session, location_key, action_kind)
    return None if offer is None else offer.stock


def filter_by_stock(
    session: Session,
    actions: list[ActionDef],
    location_key: str,
) -> list[ActionDef]:
    """Tiene solo le azioni con stock disponibile.

    - Azione senza ShopItem: sempre ammessa (comportamento attuale).
    - ShopItem.stock < 0: illimitato, sempre ammessa.
    - ShopItem.stock == 0: esaurito, esclusa.
    """
    result: list[ActionDef] = []
    for a in actions:
        offer = offer_of(session, location_key, a.kind)
        if offer is None or offer.stock < 0 or offer.stock > 0:
            result.append(a)
    return result


def buy(
    session: Session,
    character: Character,
    location_key: str,
    action: ActionDef,
    *,
    tick_index: int,
) -> PurchaseResult:
    """Acquisto atomico: stock, balance, Transaction.

    NON applica l'effetto sul bisogno (lo fa il chiamante con
    `apply_effect`) e NON tocca le relazioni. Muove solo denaro e
    scorte.
    """
    offer = offer_of(session, location_key, action.kind)
    if offer is None:
        return PurchaseResult(
            success=False,
            error=f"Nessuna offerta per {action.kind.value} @ {location_key}",
        )
    if offer.stock == 0:
        return PurchaseResult(
            success=False,
            stock_before=0,
            stock_after=0,
            error=f"{action.kind.value} esaurito @ {location_key}",
        )
    if character.balance < offer.price:
        return PurchaseResult(
            success=False,
            stock_before=offer.stock,
            stock_after=offer.stock,
            balance_after=character.balance,
            error=(f"Servono {offer.price:.1f} Athel, ne hai {character.balance:.1f}"),
        )

    stock_before = offer.stock
    if offer.stock > 0:
        offer.stock -= 1
    character.balance -= offer.price

    tx = record_transaction(
        session,
        tick_index=tick_index,
        amount=offer.price,
        kind=TransactionKind.PURCHASE,
        from_character_id=character.id,
        note=f"{action.kind.value} @ {location_key}",
    )
    session.flush()

    return PurchaseResult(
        success=True,
        price_paid=offer.price,
        stock_before=stock_before,
        stock_after=offer.stock,
        balance_after=character.balance,
        transaction_id=tx.id,
    )
