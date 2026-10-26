from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.actions.enums import ActionKind
from simai.economy.models import ShopItem

SHOP_ITEM_SPECS: list[dict[str, Any]] = [
    {
        "location_key": "caffe",
        "action_kind": ActionKind.EAT,
        "price": 3.0,
        "stock": -1,
    },
    {
        "location_key": "caffe",
        "action_kind": ActionKind.DRINK,
        "price": 2.0,
        "stock": -1,
    },
    {
        "location_key": "caffe",
        "action_kind": ActionKind.PLAY,
        "price": 4.0,
        "stock": -1,
    },
    {
        "location_key": "piazza",
        "action_kind": ActionKind.EAT,
        "price": 2.0,
        "stock": -1,
    },
]


def seed_demo_economy(session: Session) -> dict[str, int]:
    """Crea i ShopItem del Quartiere delle Muse se mancanti.

    Idempotente: chiavi già presenti non vengono toccate.
    """
    created = 0
    for spec in SHOP_ITEM_SPECS:
        existing = session.scalar(
            select(ShopItem).where(
                ShopItem.location_key == spec["location_key"],
                ShopItem.action_kind == spec["action_kind"],
            )
        )
        if existing is not None:
            continue
        session.add(ShopItem(**spec))
        created += 1
    session.flush()
    return {"shop_items_created": created}


def restock_all(session: Session) -> int:
    """Riporta lo stock ai valori dello spec. Ritorna quanti item toccati."""
    touched = 0
    for spec in SHOP_ITEM_SPECS:
        item = session.scalar(
            select(ShopItem).where(
                ShopItem.location_key == spec["location_key"],
                ShopItem.action_kind == spec["action_kind"],
            )
        )
        if item is None:
            continue
        if item.stock != spec["stock"]:
            item.stock = spec["stock"]
            touched += 1
    session.flush()
    return touched
