from pathlib import Path

import pytest
from alembic import command
from sqlalchemy import select
from sqlalchemy.engine import Engine

from simai.db.alembic_utils import get_alembic_config
from simai.db.session import get_engine, get_session_factory
from simai.needs.models import Need
from simai.sim.tick import run_tick
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


def _force_needs(session, character_key: str, **values: float) -> None:
    char = session.scalar(select(Character).where(Character.key == character_key))
    assert char is not None
    needs = session.scalars(select(Need).where(Need.character_id == char.id)).all()
    for n in needs:
        if n.kind.value in values:
            n.value = values[n.kind.value]


def test_erika_moves_to_caffe_when_thirsty(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        # Erika a casa, thirst 20, tutto il resto alto
        _force_needs(
            session,
            "erika",
            thirst=20.0,
            hunger=100.0,
            fun=100.0,
            intimacy=100.0,
        )
        session.commit()

    with factory() as session:
        report = run_tick(session, minutes=1, tick_index=0, master_seed=42)
        session.commit()

    d = next(
        (d for d in report.decisions if d.character_key == "erika"),
        None,
    )
    assert d is not None
    assert d.moved_from == "casa"
    assert d.moved_to == "caffe"
    assert d.action is None

    with factory() as session:
        erika = session.scalar(select(Character).where(Character.key == "erika"))
        assert erika is not None
        assert erika.location.key == "caffe"


def test_after_moving_erika_drinks(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        _force_needs(
            session,
            "erika",
            thirst=20.0,
            hunger=100.0,
            fun=100.0,
            intimacy=100.0,
        )
        session.commit()

    with factory() as session:
        r0 = run_tick(session, minutes=1, tick_index=0, master_seed=42)
        session.commit()
    d0 = next(d for d in r0.decisions if d.character_key == "erika")
    assert d0.moved_to == "caffe"

    with factory() as session:
        r1 = run_tick(session, minutes=1, tick_index=1, master_seed=42)
        session.commit()
    d1 = next(d for d in r1.decisions if d.character_key == "erika")
    # Ora a caffè: drink disponibile (thirst ~19 < 40)
    assert d1.action is not None
    assert d1.action.value == "drink"


def test_npc_stays_if_nothing_critical(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        _force_needs(
            session,
            "erika",
            hunger=100.0,
            thirst=100.0,
            fun=100.0,
            intimacy=100.0,
        )
        session.commit()

    with factory() as session:
        report = run_tick(session, minutes=1, tick_index=0, master_seed=42)
        session.commit()
    d = next(d for d in report.decisions if d.character_key == "erika")
    assert d.moved_to is None
    assert d.action is None
