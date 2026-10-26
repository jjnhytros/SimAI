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


def _force_needs(session, character_key: str, **values: float) -> None:
    char = session.scalar(select(Character).where(Character.key == character_key))
    assert char is not None
    needs = session.scalars(select(Need).where(Need.character_id == char.id)).all()
    for n in needs:
        if n.kind.value in values:
            n.value = values[n.kind.value]


def test_erika_drinks_at_piazza_when_thirsty(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Piazza ha DRINK gratis (fontanella): Erika non si sposta."""
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        move_character(session, "erika", "piazza")
        session.flush()
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

    d = next(d for d in report.decisions if d.character_key == "erika")
    assert d.moved_to is None
    assert d.action is not None
    assert d.action.value == "drink"
    assert d.cost_paid == 0.0


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
