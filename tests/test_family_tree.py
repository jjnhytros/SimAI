from pathlib import Path

import pytest
from alembic import command
from sqlalchemy import select
from sqlalchemy.engine import Engine

from simai.db.alembic_utils import get_alembic_config
from simai.db.session import get_engine, get_session_factory
from simai.relationships.family_tree import (
    ancestors_of,
    children_of,
    descendants_of,
    parents_of,
    siblings_of,
)
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
        session.commit()
    return engine


def _char(session, key: str) -> Character:
    c = session.scalar(select(Character).where(Character.key == key))
    assert c is not None
    return c


def test_parents_of_erika(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        erika = _char(session, "erika")
        keys = [c.key for c in parents_of(session, erika.id)]
    assert keys == ["giulia"]


def test_parents_of_giulia_empty(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        giulia = _char(session, "giulia")
        keys = [c.key for c in parents_of(session, giulia.id)]
    assert keys == []


def test_children_of_giulia(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        giulia = _char(session, "giulia")
        keys = [c.key for c in children_of(session, giulia.id)]
    assert keys == ["erika"]


def test_siblings_of_erika_empty(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        erika = _char(session, "erika")
        keys = [c.key for c in siblings_of(session, erika.id)]
    assert keys == []


def test_ancestors_of_erika(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        erika = _char(session, "erika")
        keys = [c.key for c in ancestors_of(session, erika.id)]
    assert keys == ["giulia"]


def test_descendants_of_giulia(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        giulia = _char(session, "giulia")
        keys = [c.key for c in descendants_of(session, giulia.id)]
    assert keys == ["erika"]
