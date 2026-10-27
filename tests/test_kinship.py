from pathlib import Path

import pytest
from alembic import command
from sqlalchemy import select
from sqlalchemy.engine import Engine

from simai.db.alembic_utils import get_alembic_config
from simai.db.session import get_engine, get_session_factory
from simai.relationships.kinship import (
    kinship_coefficient,
    relationship_coefficient,
    relationship_name,
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


def _ids(session) -> dict[str, int]:
    return {c.key: c.id for c in session.scalars(select(Character)).all()}


def test_r_mother_daughter(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        ids = _ids(session)
        r = relationship_coefficient(session, ids["erika"], ids["giulia"])
    assert r == 0.5


def test_r_non_consanguinei(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        ids = _ids(session)
        r = relationship_coefficient(session, ids["erika"], ids["max"])
    assert r == 0.0


def test_kinship_is_half_r(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        ids = _ids(session)
        k = kinship_coefficient(session, ids["erika"], ids["giulia"])
    assert k == 0.25


def test_relationship_name_parent(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """`relationship_name` è direzionale: `relationship_name(a, b)` =
    "cosa è a rispetto a b", non simmetrica."""
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        ids = _ids(session)
        # erika è figlio/a di giulia
        name_child = relationship_name(session, ids["erika"], ids["giulia"])
        # giulia è genitore di erika
        name_parent = relationship_name(session, ids["giulia"], ids["erika"])
    assert name_child == "figlio/a"
    assert name_parent == "genitore"


def test_relationship_name_friend(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        ids = _ids(session)
        name = relationship_name(session, ids["erika"], ids["max"])
    assert name == "amico/a"


def test_relationship_name_unknown(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        ids = _ids(session)
        name = relationship_name(session, ids["player"], ids["luca"])
    assert name == "sconosciuto"
