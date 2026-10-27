from pathlib import Path

import pytest
from alembic import command
from sqlalchemy.engine import Engine

from simai.actions.enums import ActionKind
from simai.db.alembic_utils import get_alembic_config
from simai.db.session import get_engine, get_session_factory
from simai.economy.market import offer_of
from simai.economy.seed import seed_demo_economy
from simai.sim.daily import daily_tick
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


def test_daily_tick_noop_on_non_multiple(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        offer = offer_of(session, "caffe", ActionKind.EAT)
        assert offer is not None
        offer.stock = 5
        session.commit()

    with factory() as session:
        daily_tick(session, 23)
        session.commit()

    with factory() as session:
        offer = offer_of(session, "caffe", ActionKind.EAT)
        assert offer is not None
        assert offer.stock == 5


def test_daily_tick_restocks_at_tick_zero(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Tick 0 è multiplo di 24, quindi restock. Ma lo stock è già
    pieno: no-op."""
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        daily_tick(session, 0)
        session.commit()

    with factory() as session:
        offer = offer_of(session, "caffe", ActionKind.EAT)
        assert offer is not None
        assert offer.stock == 20


def test_daily_tick_restocks_at_tick_24(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        offer = offer_of(session, "caffe", ActionKind.EAT)
        assert offer is not None
        offer.stock = 3
        session.commit()

    with factory() as session:
        daily_tick(session, 24)
        session.commit()

    with factory() as session:
        offer = offer_of(session, "caffe", ActionKind.EAT)
        assert offer is not None
        assert offer.stock == 20


def test_daily_tick_restocks_all_locations(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        caffe_eat = offer_of(session, "caffe", ActionKind.EAT)
        caffe_drink = offer_of(session, "caffe", ActionKind.DRINK)
        caffe_play = offer_of(session, "caffe", ActionKind.PLAY)
        piazza_eat = offer_of(session, "piazza", ActionKind.EAT)
        for offer in (caffe_eat, caffe_drink, caffe_play, piazza_eat):
            assert offer is not None
            offer.stock = 0
        session.commit()

    with factory() as session:
        daily_tick(session, 48)
        session.commit()

    with factory() as session:
        expected = {
            ("caffe", ActionKind.EAT): 20,
            ("caffe", ActionKind.DRINK): 20,
            ("caffe", ActionKind.PLAY): 10,
            ("piazza", ActionKind.EAT): 15,
        }
        for (loc, kind), expected_stock in expected.items():
            offer = offer_of(session, loc, kind)
            assert offer is not None
            assert offer.stock == expected_stock
