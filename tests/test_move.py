from pathlib import Path

import pytest
from sqlalchemy.engine import Engine

from alembic import command
from simai.db.alembic_utils import get_alembic_config
from simai.db.session import get_engine, get_session_factory
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


def test_move_changes_location(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        result = move_character(session, "player", "piazza")
        session.commit()
    assert result.success
    assert result.from_location_key == "casa"
    assert result.to_location_key == "piazza"


def test_move_to_same_location_is_noop(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        result = move_character(session, "player", "casa")
    assert result.success
    assert result.from_location_key == "casa"
    assert result.to_location_key == "casa"


def test_move_unknown_character(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        result = move_character(session, "fantasma", "casa")
    assert not result.success
    assert "non trovato" in (result.error or "")


def test_move_unknown_location(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        result = move_character(session, "player", "luna")
    assert not result.success
    assert "non trovata" in (result.error or "")
