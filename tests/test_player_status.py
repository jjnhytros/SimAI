from pathlib import Path

import pytest
from sqlalchemy.engine import Engine

from alembic import command
from simai.db.alembic_utils import get_alembic_config
from simai.db.session import get_engine, get_session_factory
from simai.needs.enums import NeedKind
from simai.player.status import build_player_status
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


def test_status_initial(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        s = build_player_status(session)
    assert s is not None
    assert s.tick_index == 0
    assert s.character_key == "player"
    assert s.location_key == "casa"
    assert s.needs[NeedKind.HUNGER] == 100.0
    assert len(s.available_locations) == 3
    # Erika è a casa con il player
    assert "erika" in s.other_characters_here


def test_status_relationships_present(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        s = build_player_status(session)
    assert s is not None
    # Il player non ha relazioni nel seed: nessun FRIEND
    assert s.relationships == {}
