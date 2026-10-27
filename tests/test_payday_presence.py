from pathlib import Path

import pytest
from alembic import command
from sqlalchemy import select
from sqlalchemy.engine import Engine

from simai.db.alembic_utils import get_alembic_config
from simai.db.session import get_engine, get_session_factory
from simai.economy.models import Job, Transaction
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
    """Erika a casa al tick 17 (fine turno studente): assente."""
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        report = process_payday(session, tick_index=17)
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
        report = process_payday(session, tick_index=17)
        session.commit()
    # erika, max e giulia finiscono il turno al tick 17 (end=18).
    # erika è a piazza (mossa), max e giulia sono a piazza (seed).
    assert report.paid == 3
    assert report.absent == 0
    with factory() as session:
        erika = session.scalar(select(Character).where(Character.key == "erika"))
        assert erika is not None
        assert erika.balance == before + 5.0


def test_player_absent_at_commesso_shift_end(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Player commesso (10-19, caffe). Tick 18: a casa, assente."""
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        report = process_payday(session, tick_index=18)
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
        report = process_payday(session, tick_index=18)
        session.commit()
    assert report.paid == 1
    assert report.absent == 0
    with factory() as session:
        player = session.scalar(select(Character).where(Character.is_player.is_(True)))
        assert player is not None
        assert player.balance == before + 20.0


def test_absent_creates_no_transaction(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Erika a casa al tick 17: nessuna transaction studente.
    Max (a piazza) e Giulia (a piazza) vengono pagati, ma Giulia
    ha note 'insegnante', non 'studente'."""
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        process_payday(session, tick_index=17)
        session.commit()
    with factory() as session:
        txs = session.scalars(select(Transaction).where(Transaction.note.like("%studente%"))).all()
    assert len(txs) == 1


def test_payday_skipped_during_break_absence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Giulia in pausa (14) può uscire; se al tick 17 non è in
    location, non viene pagata. Il payday è a schedule_end_tick - 1 = 17."""
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        giulia = session.scalar(select(Character).where(Character.key == "giulia"))
        assert giulia is not None
        job = session.scalar(select(Job).where(Job.character_id == giulia.id))
        assert job is not None
        assert job.break_start_tick == 14
        assert job.break_end_tick == 15
        assert job.schedule_end_tick == 18
        move_character(session, "giulia", "caffe")
        session.commit()

        report = process_payday(session, 17)
        session.commit()
        assert "giulia" in report.absent_keys
