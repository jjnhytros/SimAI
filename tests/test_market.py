from pathlib import Path

import pytest
from alembic import command
from sqlalchemy import select
from sqlalchemy.engine import Engine

from simai.actions.catalog import actions_for_location
from simai.actions.enums import ActionKind
from simai.db.alembic_utils import get_alembic_config
from simai.db.session import get_engine, get_session_factory
from simai.economy.market import (
    buy,
    filter_by_stock,
    offer_of,
    stock_of,
)
from simai.economy.models import Transaction
from simai.economy.seed import seed_demo_economy
from simai.world.enums import LocationKind
from simai.world.models import Character
from simai.world.seed import seed_muse_core


def _seeded(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Engine:
    url = f"sqlite:///{tmp_path / 'test.db'}"
    monkeypatch.setenv("SIMAI_DB_URL", url)
    command.upgrade(get_alembic_config(url=url), "head")
    engine = get_engine(url)
    factory = get_session_factory(engine)
    with factory() as session:
        seed_muse_core(session)
        seed_demo_economy(session)
        session.commit()
    return engine


def _eat_caffe():
    return next(a for a in actions_for_location(LocationKind.LEISURE) if a.kind == ActionKind.EAT)


def test_offer_of_returns_item(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        offer = offer_of(session, "caffe", ActionKind.EAT)
    assert offer is not None
    assert offer.price == 3.0
    assert offer.stock == 20


def test_stock_of_missing_returns_none(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        assert stock_of(session, "casa", ActionKind.EAT) is None


def test_filter_by_stock_drops_exhausted(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        offer = offer_of(session, "caffe", ActionKind.EAT)
        assert offer is not None
        offer.stock = 0
        session.commit()

        actions = actions_for_location(LocationKind.LEISURE)
        filtered = filter_by_stock(session, actions, "caffe")
    kinds = {a.kind for a in filtered}
    assert ActionKind.EAT not in kinds
    assert ActionKind.DRINK in kinds


def test_buy_decrements_stock_and_balance(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    action = _eat_caffe()
    with factory() as session:
        offer = offer_of(session, "caffe", ActionKind.EAT)
        assert offer is not None
        offer.stock = 20
        session.commit()

        player = session.scalar(select(Character).where(Character.key == "player"))
        assert player is not None
        result = buy(session, player, "caffe", action, tick_index=5)
        session.commit()
        assert result.success
        assert result.price_paid == 3.0
        assert result.stock_before == 20
        assert result.stock_after == 19
        assert result.balance_after == 97.0
        assert result.transaction_id is not None

    with factory() as session:
        item = offer_of(session, "caffe", ActionKind.EAT)
        assert item is not None
        assert item.stock == 19
        tx = session.scalar(select(Transaction).where(Transaction.id == result.transaction_id))
        assert tx is not None
        assert tx.amount == 3.0
        assert tx.tick_index == 5


def test_buy_rejects_out_of_stock(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    action = _eat_caffe()
    with factory() as session:
        offer = offer_of(session, "caffe", ActionKind.EAT)
        assert offer is not None
        offer.stock = 0
        session.commit()

        player = session.scalar(select(Character).where(Character.key == "player"))
        assert player is not None
        balance_before = player.balance
        result = buy(session, player, "caffe", action, tick_index=0)
        session.commit()

        assert not result.success
        assert result.error is not None and "esaurito" in result.error
        assert player.balance == balance_before


def test_buy_rejects_insufficient_balance(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    action = _eat_caffe()
    with factory() as session:
        player = session.scalar(select(Character).where(Character.key == "player"))
        assert player is not None
        player.balance = 1.0
        session.commit()

        result = buy(session, player, "caffe", action, tick_index=0)
        session.commit()

        assert not result.success
        assert result.error is not None and "Servono" in result.error


def test_buy_with_infinite_stock_keeps_minus_one(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    action = _eat_caffe()
    with factory() as session:
        offer = offer_of(session, "caffe", ActionKind.EAT)
        assert offer is not None
        offer.stock = -1
        session.commit()

        player = session.scalar(select(Character).where(Character.key == "player"))
        assert player is not None
        result = buy(session, player, "caffe", action, tick_index=0)
        session.commit()
        assert result.success
        assert result.stock_before == -1
        assert result.stock_after == -1


def test_save_load_preserves_shop_items(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from simai.save.service import create_save, load_save

    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    action = _eat_caffe()
    with factory() as session:
        # 1. Stock è 20 dal seed 1.6.0. Compra.
        offer_before_buy = offer_of(session, "caffe", ActionKind.EAT)
        assert offer_before_buy is not None
        assert offer_before_buy.stock == 20
        session.commit()

        player = session.scalar(select(Character).where(Character.key == "player"))
        assert player is not None
        buy(session, player, "caffe", action, tick_index=0)
        session.commit()

        # 2. Snapshot: stock è 19.
        save_path = tmp_path / "roundtrip.sav"
        create_save(session, name="roundtrip", output=save_path)

        # 3. Sporca lo stato in memoria: stock diventa 99.
        offer_after_buy = offer_of(session, "caffe", ActionKind.EAT)
        assert offer_after_buy is not None
        offer_after_buy.stock = 99
        session.commit()

        # 4. Load: deve riportare stock a 19 (dal save).
        load_save(session, str(save_path))
        session.commit()

    with factory() as session:
        item = offer_of(session, "caffe", ActionKind.EAT)
        assert item is not None
        assert item.stock == 19


def test_shop_item_price_matches_catalog() -> None:
    """Se questo fallisce, ShopItem e CATALOG sono divergenti.

    `filter_by_affordability` usa ActionDef.cost; `market_buy` usa
    ShopItem.price. Se divergono, il filtro lascia passare azioni che
    poi l'acquisto rifiuta.
    """
    from simai.actions.catalog import CATALOG
    from simai.economy.seed import SHOP_ITEM_SPECS

    catalog_by_key: dict[tuple[str, str], float] = {}
    for action in CATALOG:
        for loc_kind in action.allowed_at:
            catalog_by_key[(loc_kind.value, action.kind.value)] = action.cost

    location_key_to_kind = {
        "casa": "residential",
        "piazza": "social",
        "caffe": "leisure",
    }

    for spec in SHOP_ITEM_SPECS:
        loc_kind = location_key_to_kind[spec["location_key"]]
        key = (loc_kind, spec["action_kind"].value)
        assert key in catalog_by_key, f"Spec orfana: {spec}"
        assert spec["price"] == catalog_by_key[key], (
            f"Prezzo divergente per {spec['location_key']}/"
            f"{spec['action_kind'].value}: "
            f"ShopItem={spec['price']}, CATALOG={catalog_by_key[key]}"
        )


def test_stock_exhaustion_and_restock_via_tick(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """20 acquisti esauriscono EAT caffè; daily_tick a tick 28 ripristina."""
    from simai.sim.tick import run_tick

    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    action = _eat_caffe()

    with factory() as session:
        offer = offer_of(session, "caffe", ActionKind.EAT)
        assert offer is not None
        offer.stock = 1
        session.commit()

        player = session.scalar(select(Character).where(Character.key == "player"))
        assert player is not None
        player.balance = 1000.0
        session.commit()

        # Compra finché c'è stock.
        result = buy(session, player, "caffe", action, tick_index=10)
        session.commit()
        assert result.success
        assert result.stock_after == 0

        # Secondo acquisto: stock esaurito.
        result = buy(session, player, "caffe", action, tick_index=11)
        session.commit()
        assert not result.success
        assert result.error is not None and "esaurito" in result.error

        # Tick 28: daily_tick restock.
        run_tick(session, minutes=60, tick_index=28, master_seed=42)
        session.commit()

    with factory() as session:
        offer = offer_of(session, "caffe", ActionKind.EAT)
        assert offer is not None
        assert offer.stock == 20
