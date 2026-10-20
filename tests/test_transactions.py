from pathlib import Path

import pytest
from alembic import command
from sqlalchemy import select
from sqlalchemy.engine import Engine

from simai.db.alembic_utils import get_alembic_config
from simai.db.session import get_engine, get_session_factory
from simai.economy.enums import TransactionKind
from simai.economy.service import (
    record_transaction,
    transactions_of,
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


def test_record_salary(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        erika = session.scalar(select(Character).where(Character.key == "erika"))
        assert erika is not None
        tx = record_transaction(
            session,
            tick_index=24,
            amount=5.0,
            kind=TransactionKind.SALARY,
            to_character_id=erika.id,
            note="payday",
        )
        session.commit()
        assert tx.id is not None
        assert tx.kind == TransactionKind.SALARY


def test_record_rejects_non_positive(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session, pytest.raises(ValueError):
        record_transaction(
            session,
            tick_index=1,
            amount=0.0,
            kind=TransactionKind.SALARY,
        )


def test_transactions_of_returns_both_sides(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        erika = session.scalar(select(Character).where(Character.key == "erika"))
        luca = session.scalar(select(Character).where(Character.key == "luca"))
        assert erika is not None and luca is not None
        record_transaction(
            session,
            tick_index=24,
            amount=5.0,
            kind=TransactionKind.SALARY,
            to_character_id=erika.id,
        )
        record_transaction(
            session,
            tick_index=25,
            amount=2.0,
            kind=TransactionKind.PURCHASE,
            from_character_id=erika.id,
            to_character_id=luca.id,
            note="drink",
        )
        session.commit()
        txs = transactions_of(session, erika.id)
    assert len(txs) == 2
    assert {t.kind for t in txs} == {
        TransactionKind.SALARY,
        TransactionKind.PURCHASE,
    }
