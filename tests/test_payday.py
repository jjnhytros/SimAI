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


def test_is_payday_tick() -> None:
    assert TICKS_PER_DAY == 24
    assert not is_payday_tick(0)
    assert not is_payday_tick(22)
    assert is_payday_tick(23)
    assert not is_payday_tick(24)
    assert is_payday_tick(47)
    assert is_payday_tick(71)


def test_non_payday_does_nothing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        paid = process_payday(session, tick_index=5)
        session.commit()
    assert paid == 0


def test_payday_credits_everyone(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        before = {c.key: c.balance for c in session.scalars(select(Character)).all()}
        paid = process_payday(session, tick_index=23)
        session.commit()
    assert paid == 5
    with factory() as session:
        after = {c.key: c.balance for c in session.scalars(select(Character)).all()}
    assert after["luca"] == before["luca"] + 25.0
    assert after["giulia"] == before["giulia"] + 22.0
    assert after["player"] == before["player"] + 20.0
    assert after["erika"] == before["erika"] + 5.0
    assert after["max"] == before["max"] + 5.0


def test_payday_records_salary_transactions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        process_payday(session, tick_index=23)
        session.commit()
    with factory() as session:
        txs = session.scalars(select(Transaction)).all()
    assert len(txs) == 5
    assert all(t.kind == TransactionKind.SALARY for t in txs)
    assert all(t.tick_index == 23 for t in txs)


def test_payday_deterministic_across_ticks(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        assert process_payday(session, 23) == 5
        assert process_payday(session, 24) == 0
        assert process_payday(session, 47) == 5
        session.commit()
