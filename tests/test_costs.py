from pathlib import Path

import pytest
from alembic import command
from sqlalchemy import select
from sqlalchemy.engine import Engine

from simai.actions.do import do_action
from simai.actions.enums import ActionKind
from simai.db.alembic_utils import get_alembic_config
from simai.db.session import get_engine, get_session_factory
from simai.needs.enums import NeedKind
from simai.needs.models import Need
from simai.world.models import Character
from simai.world.move import move_character
from simai.world.seed import seed_muse_core


def _seeded(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Engine:
    url = f"sqlite:///{tmp_path / 'test.db'}"
    monkeypatch.setenv("SIMAI_DB_URL", url)
    command.upgrade(get_alembic_config(url=url), "head")
    engine = get_engine(url)
    factory = get_session_factory(engine)
    with factory() as session:
        seed_muse_core(session)
        session.commit()
    return engine


def _set_thirst(session, char_id: int, value: float) -> None:
    n = session.scalar(
        select(Need).where(
            Need.character_id == char_id,
            Need.kind == NeedKind.THIRST,
        )
    )
    assert n is not None
    n.value = value


def test_drink_at_caffe_costs_two(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        player = session.scalar(select(Character).where(Character.key == "player"))
        assert player is not None
        move_character(session, "player", "caffe")
        session.flush()
        _set_thirst(session, player.id, 20.0)
        session.flush()
        before = player.balance
        result = do_action(session, "player", ActionKind.DRINK)
        session.commit()
    assert result.success
    with factory() as session:
        player = session.scalar(select(Character).where(Character.key == "player"))
        assert player is not None
        assert player.balance == before - 2.0


def test_drink_at_home_is_free(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        player = session.scalar(select(Character).where(Character.key == "player"))
        assert player is not None
        _set_thirst(session, player.id, 20.0)
        session.flush()
        before = player.balance
        result = do_action(session, "player", ActionKind.DRINK)
        session.commit()
    assert result.success
    # drink a casa: amount 15 (non 30)
    assert result.need_after == 35.0
    with factory() as session:
        player = session.scalar(select(Character).where(Character.key == "player"))
        assert player is not None
        assert player.balance == before


def test_cannot_afford_drink(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        player = session.scalar(select(Character).where(Character.key == "player"))
        assert player is not None
        player.balance = 1.0
        move_character(session, "player", "caffe")
        session.flush()
        _set_thirst(session, player.id, 20.0)
        session.flush()
        result = do_action(session, "player", ActionKind.DRINK)
        session.rollback()
    assert not result.success
    assert result.error is not None
    assert "Athel" in result.error
    assert "2" in result.error


def test_cannot_afford_creates_no_transaction(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from simai.economy.models import Transaction

    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        player = session.scalar(select(Character).where(Character.key == "player"))
        assert player is not None
        player.balance = 0.0
        move_character(session, "player", "caffe")
        session.flush()
        _set_thirst(session, player.id, 20.0)
        session.flush()
        do_action(session, "player", ActionKind.DRINK)
        session.commit()
    with factory() as session:
        assert session.scalars(select(Transaction)).all() == []
