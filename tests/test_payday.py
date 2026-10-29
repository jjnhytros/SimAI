from pathlib import Path

import pytest
from alembic import command
from sqlalchemy import select
from sqlalchemy.engine import Engine

from simai.db.alembic_utils import get_alembic_config
from simai.db.session import get_engine, get_session_factory
from simai.economy.calendar import TICKS_PER_DAY, is_payday_tick
from simai.economy.enums import TransactionKind
from simai.economy.models import Transaction
from simai.economy.payday import process_payday
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


def test_is_payday_tick_utility() -> None:
    assert TICKS_PER_DAY == 28
    assert not is_payday_tick(0)
    assert is_payday_tick(27)
    assert is_payday_tick(55)
    assert not is_payday_tick(28)
    assert not is_payday_tick(54)


def test_mid_shift_does_nothing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Tick 5: nessun turno finisce. Zero pagati, zero assenti."""
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        report = process_payday(session, tick_index=5)
        session.commit()
    assert report.paid == 0
    assert report.absent == 0


def test_payday_at_end_of_shift(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Seed 1.7.1:
       - giulia (insegnante, 7-18, piazza, break 14-15): fine turno tick 17
       - erika/max (studente, 7-18, piazza, break 14-15): fine turno tick 17
       - luca (barista, 14-21, caffe): fine turno tick 20
       - player (commesso, 10-19, caffe): fine turno tick 18
    Al tick 17: erika (a casa) assente, max e giulia (a piazza) pagati.
    """
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        before = {c.key: c.balance for c in session.scalars(select(Character)).all()}
        report = process_payday(session, tick_index=17)
        session.commit()
    assert report.paid == 2
    assert report.absent == 1
    assert report.absent_keys == ("erika",)
    with factory() as session:
        after = {c.key: c.balance for c in session.scalars(select(Character)).all()}
    assert after["max"] == before["max"] + 5.0
    assert after["erika"] == before["erika"]
    assert after["giulia"] == before["giulia"] + 22.0


def test_multiple_shifts_paid_at_own_tick(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        # tick 17: erika assente, max e giulia pagati
        r17 = process_payday(session, tick_index=17)
        # tick 18: player a casa, assente
        r18 = process_payday(session, tick_index=18)
        # tick 20: luca a caffe, pagato
        r20 = process_payday(session, tick_index=20)
        session.commit()
    assert r17.paid == 2 and r17.absent == 1
    assert r17.absent_keys == ("erika",)
    assert r18.paid == 0 and r18.absent == 1
    assert r18.absent_keys == ("player",)
    assert r20.paid == 1 and r20.absent == 0


def test_records_salary_transactions(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        process_payday(session, tick_index=17)
        process_payday(session, tick_index=18)
        process_payday(session, tick_index=20)
        session.commit()
    with factory() as session:
        txs = session.scalars(select(Transaction)).all()
    assert len(txs) == 3
    assert all(t.kind == TransactionKind.SALARY for t in txs)
    assert {t.tick_index for t in txs} == {17, 20}


def test_payday_skips_pediatric_non_student(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """NPC pediatrico non-STUDENTE non viene pagato (job sospeso)."""
    from simai.economy.enums import JobTitle
    from simai.economy.models import Job
    from simai.economy.payday import process_payday

    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        erika = session.scalar(select(Character).where(Character.key == "erika"))
        assert erika is not None
        job = session.scalar(select(Job).where(Job.character_id == erika.id))
        assert job is not None
        job.title = JobTitle.BARISTA
        job.location_key = "casa"
        job.schedule_end_tick = 10
        session.commit()

    with factory() as session:
        report = process_payday(session, tick_index=9)
        session.commit()
    assert report.paid == 0
    assert "erika" not in report.absent_keys


def test_payday_pays_pediatric_student(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """STUDENTE è esente: Erika riceve la paghetta anche a 14 anni."""
    from simai.economy.payday import process_payday
    from simai.world.models import Location

    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        erika = session.scalar(select(Character).where(Character.key == "erika"))
        assert erika is not None
        balance_before = erika.balance
        piazza = session.scalar(select(Location).where(Location.key == "piazza"))
        assert piazza is not None
        erika.location_id = piazza.id
        session.commit()

    with factory() as session:
        report = process_payday(session, tick_index=17)
        session.commit()

    with factory() as session:
        erika = session.scalar(select(Character).where(Character.key == "erika"))
        assert erika is not None
        assert erika.balance == balance_before + 5.0
        assert report.paid >= 1
