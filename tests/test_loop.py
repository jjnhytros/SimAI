from pathlib import Path

import pytest
from sqlalchemy import select
from sqlalchemy.engine import Engine

from alembic import command
from simai.db.alembic_utils import get_alembic_config
from simai.db.session import get_engine, get_session_factory
from simai.sim.loop import run_simulation
from simai.sim.state import get_state
from simai.world.models import Character
from simai.world.seed import seed_muse_core


def _seeded(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Engine:
    url = f"sqlite:///{tmp_path / 'test.db'}"
    monkeypatch.setenv("SIMAI_DB_URL", url)
    monkeypatch.setenv("SIMAI_SAVES_DIR", str(tmp_path / "saves"))
    command.upgrade(get_alembic_config(url=url), "head")
    engine = get_engine(url)
    factory = get_session_factory(engine)
    with factory() as session:
        seed_muse_core(session)
        session.commit()
    return engine


def test_run_simulation_executes_n_ticks(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        report = run_simulation(session, ticks=5, minutes_per_tick=60)
    assert report.ticks_executed == 5
    assert report.total_minutes == 300
    assert report.failed_at_tick is None


def test_run_simulation_advances_state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        report = run_simulation(session, ticks=3, minutes_per_tick=60)
        assert report.started_at_tick == 0
        assert report.ended_at_tick == 3
    with factory() as session:
        assert get_state(session).tick_index == 3


def test_run_simulation_is_deterministic_across_fresh_dbs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def outcome(label: str) -> tuple[int, dict[str, float]]:
        sub = tmp_path / label
        sub.mkdir()
        engine = _seeded(sub, monkeypatch)
        factory = get_session_factory(engine)
        with factory() as session:
            run_simulation(session, ticks=3, minutes_per_tick=60)
        with factory() as session:
            from simai.needs.service import needs_of

            erika = session.scalar(select(Character).where(Character.key == "erika"))
            assert erika is not None
            return (
                get_state(session).tick_index,
                needs_of(session, erika.id),
            )

    assert outcome("a") == outcome("b")


def test_autosave_creates_files_at_expected_ticks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        report = run_simulation(
            session,
            ticks=4,
            minutes_per_tick=60,
            autosave_every=2,
            autosave_name="auto",
        )
    assert len(report.autosaves) == 2
    assert [a.tick for a in report.autosaves] == [2, 4]
    for a in report.autosaves:
        assert a.error is None
        assert a.path is not None
        assert a.path.exists()


def test_autosave_disabled_when_zero(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        report = run_simulation(session, ticks=3, minutes_per_tick=60, autosave_every=0)
    assert report.autosaves == ()


def test_failed_tick_stops_loop_and_rolls_back(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)

    import simai.sim.loop as loop_mod

    real_run_tick = loop_mod.run_tick
    calls = {"n": 0}

    def flaky(*args, **kwargs):  # type: ignore[no-untyped-def]
        calls["n"] += 1
        if calls["n"] == 3:
            raise RuntimeError("boom")
        return real_run_tick(*args, **kwargs)

    monkeypatch.setattr(loop_mod, "run_tick", flaky)

    with factory() as session:
        report = run_simulation(session, ticks=5, minutes_per_tick=60)

    assert report.ticks_executed == 2
    assert report.failed_at_tick == 2
    assert report.error_message is not None
    assert "boom" in report.error_message

    with factory() as session:
        assert get_state(session).tick_index == 2


def test_invalid_arguments(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        with pytest.raises(ValueError):
            run_simulation(session, ticks=0, minutes_per_tick=60)
        with pytest.raises(ValueError):
            run_simulation(session, ticks=1, minutes_per_tick=0)
        with pytest.raises(ValueError):
            run_simulation(session, ticks=1, minutes_per_tick=60, autosave_every=-1)
