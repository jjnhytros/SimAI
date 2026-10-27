from pathlib import Path

import pytest
from alembic import command
from sqlalchemy import select
from sqlalchemy.engine import Engine

from simai.db.alembic_utils import get_alembic_config
from simai.db.session import get_engine, get_session_factory
from simai.economy.enums import JobTitle
from simai.economy.models import Job
from simai.economy.work import (
    CRITICAL_HUNGER_THRESHOLD,
    PRIORITY_WINDOW,
    WorkState,
    should_prioritize_work,
    tick_in_day,
    work_state_for,
)
from simai.needs.enums import NeedKind
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


def _make_job(start: int, end: int) -> Job:
    return Job(
        id=0,
        character_id=1,
        title=JobTitle.BARISTA,
        location_key="caffe",
        daily_wage=20.0,
        schedule_start_tick=start,
        schedule_end_tick=end,
    )


def test_tick_in_day() -> None:
    assert tick_in_day(0) == 0
    assert tick_in_day(23) == 23
    assert tick_in_day(28) == 0
    assert tick_in_day(47) == 19
    assert tick_in_day(55) == 27


def test_work_state_no_job() -> None:
    assert work_state_for(None, 5) == WorkState.NO_JOB


def test_work_state_before() -> None:
    job = _make_job(8, 16)
    assert work_state_for(job, 5) == WorkState.BEFORE_WORK


def test_work_state_working() -> None:
    job = _make_job(8, 16)
    assert work_state_for(job, 10) == WorkState.WORKING


def test_work_state_after() -> None:
    job = _make_job(8, 16)
    assert work_state_for(job, 18) == WorkState.AFTER_WORK


def test_priority_near_start() -> None:
    job = _make_job(8, 16)
    # tick 6 -> ticks_until 2 == PRIORITY_WINDOW
    assert should_prioritize_work(job, 6, 50.0) is True
    assert should_prioritize_work(job, 7, 50.0) is True


def test_priority_too_far() -> None:
    job = _make_job(8, 16)
    # tick 5 -> ticks_until 3 > 2
    assert should_prioritize_work(job, 5, 50.0) is False


def test_priority_critical_hunger() -> None:
    job = _make_job(8, 16)
    assert should_prioritize_work(job, 6, CRITICAL_HUNGER_THRESHOLD - 1.0) is False


def test_priority_window_constant() -> None:
    assert PRIORITY_WINDOW == 2


def _set_job_schedule(session, character_key: str, start: int, end: int) -> None:
    char = session.scalar(select(Character).where(Character.key == character_key))
    assert char is not None
    job = session.scalar(select(Job).where(Job.character_id == char.id))
    assert job is not None
    job.schedule_start_tick = start
    job.schedule_end_tick = end


def _move_and_reset_needs(session, character_key: str, location_key: str) -> None:
    move_character(session, character_key, location_key)
    char = session.scalar(select(Character).where(Character.key == character_key))
    assert char is not None
    needs = session.scalars(select(Need).where(Need.character_id == char.id)).all()
    for n in needs:
        n.value = 100.0


def test_npc_moves_to_work_when_priority(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Luca (barista al caffè) è a casa alle 06:00 con job start 08:00.
    Priorità attiva: deve muoversi al caffè."""
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        _set_job_schedule(session, "luca", start=8, end=16)
        _move_and_reset_needs(session, "luca", "casa")
        session.commit()

    with factory() as session:
        report = run_tick(session, minutes=60, tick_index=6, master_seed=42)
        session.commit()

    d = next(d for d in report.decisions if d.character_key == "luca")
    assert d.moved_from == "casa"
    assert d.moved_to == "caffe"
    assert d.action is None

    with factory() as session:
        luca = session.scalar(select(Character).where(Character.key == "luca"))
        assert luca is not None
        assert luca.location.key == "caffe"


def test_npc_does_not_move_when_already_at_work(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Luca è già al caffè alle 06:00. Priorità attiva ma location
    corretta: no move, azioni locali normali (skip se bisogni alti)."""
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        _set_job_schedule(session, "luca", start=8, end=16)
        session.commit()

    with factory() as session:
        report = run_tick(session, minutes=60, tick_index=6, master_seed=42)
        session.commit()

    d = next(d for d in report.decisions if d.character_key == "luca")
    assert d.moved_to is None


def test_npc_skips_work_on_critical_hunger(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Luca a casa alle 06:00 con hunger 5. Salvaguardia: priorità
    decade, mangia a casa."""
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        _set_job_schedule(session, "luca", start=8, end=16)
        _move_and_reset_needs(session, "luca", "casa")
        luca = session.scalar(select(Character).where(Character.key == "luca"))
        assert luca is not None
        hunger = session.scalar(
            select(Need).where(
                Need.character_id == luca.id,
                Need.kind == NeedKind.HUNGER,
            )
        )
        assert hunger is not None
        hunger.value = 5.0
        session.commit()

    with factory() as session:
        report = run_tick(session, minutes=1, tick_index=6, master_seed=42)
        session.commit()

    d = next(d for d in report.decisions if d.character_key == "luca")
    assert d.moved_to is None
    assert d.action is not None
    assert d.action.value == "eat"


def test_priority_during_working_state() -> None:
    """Durante WORKING, la priorità è attiva indipendentemente dal
    tick (purché hunger >= 10)."""
    job = _make_job(8, 16)
    # t=10 è nel mezzo del turno
    assert should_prioritize_work(job, 10, 50.0) is True
    assert should_prioritize_work(job, 15, 50.0) is True


def test_priority_after_work_inactive() -> None:
    job = _make_job(8, 16)
    assert should_prioritize_work(job, 16, 50.0) is False
    assert should_prioritize_work(job, 20, 50.0) is False


def test_priority_working_state_critical_hunger() -> None:
    """Salvaguardia fame si applica anche durante il turno."""
    job = _make_job(8, 16)
    assert should_prioritize_work(job, 10, CRITICAL_HUNGER_THRESHOLD - 1.0) is False


def test_work_state_on_break() -> None:
    from simai.economy.models import Job
    from simai.economy.work import WorkState, work_state_for

    job = Job(
        character_id=1,
        title="insegnante",
        location_key="piazza",
        daily_wage=22.0,
        schedule_start_tick=7,
        schedule_end_tick=18,
        break_start_tick=14,
        break_end_tick=15,
    )
    assert work_state_for(job, 6) == WorkState.BEFORE_WORK
    assert work_state_for(job, 7) == WorkState.WORKING
    assert work_state_for(job, 13) == WorkState.WORKING
    assert work_state_for(job, 14) == WorkState.ON_BREAK
    assert work_state_for(job, 15) == WorkState.WORKING
    assert work_state_for(job, 17) == WorkState.WORKING
    assert work_state_for(job, 18) == WorkState.AFTER_WORK


def test_should_prioritize_work_on_break() -> None:
    from simai.economy.models import Job
    from simai.economy.work import should_prioritize_work

    job = Job(
        character_id=1,
        title="insegnante",
        location_key="piazza",
        daily_wage=22.0,
        schedule_start_tick=7,
        schedule_end_tick=18,
        break_start_tick=14,
        break_end_tick=15,
    )
    assert should_prioritize_work(job, 14, 100.0) is False
    assert should_prioritize_work(job, 15, 100.0) is True
