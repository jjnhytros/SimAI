from pathlib import Path

import pytest
from alembic import command
from sqlalchemy import select
from sqlalchemy.engine import Engine

from simai.db.alembic_utils import get_alembic_config
from simai.db.session import get_engine, get_session_factory
from simai.economy.models import Transaction
from simai.economy.payday import process_payday
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


def test_student_erika_absent_if_at_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Erika a casa al tick 12 (fine turno studente): assente."""
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        report = process_payday(session, tick_index=12)
        session.commit()
    assert "erika" in report.absent_keys


def test_student_erika_paid_if_moved_to_piazza(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        move_character(session, "erika", "piazza")
        session.flush()
        erika = session.scalar(select(Character).where(Character.key == "erika"))
        assert erika is not None
        before = erika.balance
        report = process_payday(session, tick_index=12)
        session.commit()
    assert report.paid == 2  # max + erika
    assert report.absent == 0
    with factory() as session:
        erika = session.scalar(select(Character).where(Character.key == "erika"))
        assert erika is not None
        assert erika.balance == before + 5.0


def test_player_absent_at_commesso_shift_end(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Player commesso (9-17, caffe). Tick 16: a casa, assente."""
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        report = process_payday(session, tick_index=16)
        session.commit()
    assert report.paid == 0
    assert report.absent == 1
    assert report.absent_keys == ("player",)


def test_player_paid_if_at_caffe(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        move_character(session, "player", "caffe")
        session.flush()
        player = session.scalar(select(Character).where(Character.is_player.is_(True)))
        assert player is not None
        before = player.balance
        report = process_payday(session, tick_index=16)
        session.commit()
    assert report.paid == 1
    assert report.absent == 0
    with factory() as session:
        player = session.scalar(select(Character).where(Character.is_player.is_(True)))
        assert player is not None
        assert player.balance == before + 20.0


def test_absent_creates_no_transaction(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Erika a casa al tick 12: nessuna transaction studente."""
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        process_payday(session, tick_index=12)
        session.commit()
    with factory() as session:
        txs = session.scalars(select(Transaction).where(Transaction.note.like("%studente%"))).all()
    # Solo Max (pagato), non Erika (assente)
    assert len(txs) == 1
