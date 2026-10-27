from pathlib import Path

import pytest
from alembic import command
from sqlalchemy import select
from sqlalchemy.engine import Engine

from simai.actions.enums import ActionKind
from simai.db.alembic_utils import get_alembic_config
from simai.db.session import get_engine, get_session_factory
from simai.economy.models import ShopItem
from simai.economy.seed import (
    SHOP_ITEM_SPECS,
    restock_all,
    seed_demo_economy,
)


def _upgraded(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Engine:
    url = f"sqlite:///{tmp_path / 'test.db'}"
    monkeypatch.setenv("SIMAI_DB_URL", url)
    command.upgrade(get_alembic_config(url=url), "head")
    return get_engine(url)


def test_seed_creates_four_shop_items(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _upgraded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        report = seed_demo_economy(session)
        session.commit()
    assert report["shop_items_created"] == 4
    with factory() as session:
        items = session.scalars(select(ShopItem)).all()
    assert len(items) == 4


def test_seed_idempotent(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _upgraded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        seed_demo_economy(session)
        session.commit()
    with factory() as session:
        report = seed_demo_economy(session)
        session.commit()
    assert report["shop_items_created"] == 0


def test_specs_cover_expected_pairs() -> None:
    pairs = {(s["location_key"], s["action_kind"]) for s in SHOP_ITEM_SPECS}
    assert ("caffe", ActionKind.EAT) in pairs
    assert ("caffe", ActionKind.DRINK) in pairs
    assert ("caffe", ActionKind.PLAY) in pairs
    assert ("piazza", ActionKind.EAT) in pairs


def test_restock_resets_stock(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _upgraded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        seed_demo_economy(session)
        session.commit()

    with factory() as session:
        item = session.scalar(
            select(ShopItem).where(
                ShopItem.location_key == "caffe",
                ShopItem.action_kind == ActionKind.EAT,
            )
        )
        assert item is not None
        item.stock = 3
        session.commit()

    with factory() as session:
        touched = restock_all(session)
        session.commit()
    assert touched == 1

    with factory() as session:
        item = session.scalar(
            select(ShopItem).where(
                ShopItem.location_key == "caffe",
                ShopItem.action_kind == ActionKind.EAT,
            )
        )
        assert item is not None
        # spec 1.6.0: stock=20 + restock giornaliero da `daily_tick`.
        assert item.stock == 20


def test_restock_is_noop_when_already_full(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _upgraded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        seed_demo_economy(session)
        session.commit()
    with factory() as session:
        touched = restock_all(session)
        session.commit()
    assert touched == 0
