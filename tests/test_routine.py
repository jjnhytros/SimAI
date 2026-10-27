from pathlib import Path

import pytest
from alembic import command
from sqlalchemy import select
from sqlalchemy.engine import Engine

from simai.db.alembic_utils import get_alembic_config
from simai.db.session import get_engine, get_session_factory
from simai.economy.work import (
    HOME_FUN_THRESHOLD,
    HOME_INTIMACY_THRESHOLD,
    should_prioritize_home,
)
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


def test_home_seeded(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        chars = session.scalars(select(Character)).all()
        for c in chars:
            assert c.home_location_id is not None


def test_should_prioritize_home_after_work(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Dopo il turno (tick 19+ per commesso 10-19), a caffe, con
    intimacy/fun alti: priorità casa attiva."""
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        player = session.scalar(select(Character).where(Character.is_player.is_(True)))
        assert player is not None
        assert player.home_location_id is not None
        from simai.economy.service import job_of

        job = job_of(session, player.id)
        assert job is not None
        # t=19: AFTER_WORK per commesso (10-19)
        assert (
            should_prioritize_home(
                job,
                t_in_day=19,
                home_key="casa",
                current_key="caffe",
                intimacy=80.0,
                fun=80.0,
            )
            is True
        )


def test_no_home_priority_when_low_intimacy(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        player = session.scalar(select(Character).where(Character.is_player.is_(True)))
        assert player is not None
        from simai.economy.service import job_of

        job = job_of(session, player.id)
        assert job is not None
        # intimacy 30 < 40: nessuna priorità casa
        assert (
            should_prioritize_home(
                job,
                t_in_day=19,
                home_key="casa",
                current_key="caffe",
                intimacy=30.0,
                fun=80.0,
            )
            is False
        )


def test_no_home_priority_during_work(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        player = session.scalar(select(Character).where(Character.is_player.is_(True)))
        assert player is not None
        from simai.economy.service import job_of

        job = job_of(session, player.id)
        assert job is not None
        # t=12: WORKING per commesso (10-19)
        assert (
            should_prioritize_home(
                job,
                t_in_day=12,
                home_key="casa",
                current_key="caffe",
                intimacy=80.0,
                fun=80.0,
            )
            is False
        )


def test_npc_returns_home_after_shift(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Luca (barista, 14-21) a caffe al tick 22 (dopo la fine turno):
    priorità casa, torna a casa."""
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        luca = session.scalar(select(Character).where(Character.key == "luca"))
        assert luca is not None
        # Bisogni alti (default): nessun bisogno urgente
        needs = session.scalars(select(Need).where(Need.character_id == luca.id)).all()
        for n in needs:
            n.value = 100.0
        session.commit()

    # tick 22: t_in_day = 22, dopo il turno di luca (14-21)
    with factory() as session:
        report = run_tick(session, minutes=1, tick_index=22, master_seed=42)
        session.commit()
    d = next(
        (d for d in report.decisions if d.character_key == "luca"),
        None,
    )
    assert d is not None
    assert d.moved_to == "casa"


def test_constants() -> None:
    assert HOME_INTIMACY_THRESHOLD == 40.0
    assert HOME_FUN_THRESHOLD == 40.0
