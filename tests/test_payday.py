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
    assert TICKS_PER_DAY == 24
    assert not is_payday_tick(0)
    assert is_payday_tick(23)


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
    """Seed:
       - giulia (insegnante, 8-14, piazza): fine turno tick 13
       - erika/max (studente, 8-13, piazza): fine turno tick 12
       - luca (barista, 8-16, caffe): fine turno tick 15
       - player (commesso, 9-17, caffe): fine turno tick 16
    Al tick 12: erika (a casa) assente, max (a piazza) pagato.
    """
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        before = {c.key: c.balance for c in session.scalars(select(Character)).all()}
        report = process_payday(session, tick_index=12)
        session.commit()
    assert report.paid == 1
    assert report.absent == 1
    assert report.absent_keys == ("erika",)
    with factory() as session:
        after = {c.key: c.balance for c in session.scalars(select(Character)).all()}
    assert after["max"] == before["max"] + 5.0
    assert after["erika"] == before["erika"]


def test_multiple_shifts_paid_at_own_tick(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        # tick 12: erika assente, max pagato (studenti)
        r12 = process_payday(session, tick_index=12)
        # tick 13: giulia pagata (insegnante)
        r13 = process_payday(session, tick_index=13)
        # tick 15: luca pagato (barista)
        r15 = process_payday(session, tick_index=15)
        # tick 16: player a casa, assente
        r16 = process_payday(session, tick_index=16)
        session.commit()
    assert r12.paid == 1 and r12.absent == 1
    assert r13.paid == 1 and r13.absent == 0
    assert r15.paid == 1 and r15.absent == 0
    assert r16.paid == 0 and r16.absent == 1
    assert r16.absent_keys == ("player",)


def test_records_salary_transactions(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        process_payday(session, tick_index=12)
        process_payday(session, tick_index=13)
        process_payday(session, tick_index=15)
        session.commit()
    with factory() as session:
        txs = session.scalars(select(Transaction)).all()
    assert len(txs) == 3
    assert all(t.kind == TransactionKind.SALARY for t in txs)
    assert {t.tick_index for t in txs} == {12, 13, 15}
