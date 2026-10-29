from pathlib import Path

import pytest
from alembic import command
from sqlalchemy import select
from sqlalchemy.engine import Engine

from simai.db.alembic_utils import get_alembic_config
from simai.db.session import get_engine, get_session_factory
from simai.npc.lifecycle import DAYS_PER_YEAR, apply_aging
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


def test_seed_has_age_days(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        by_key = {c.key: c for c in session.scalars(select(Character)).all()}
    assert by_key["erika"].age_days == 24
    assert by_key["max"].age_days == 32
    assert by_key["giulia"].age_days == 0
    assert by_key["luca"].age_days == 0
    assert by_key["player"].age_days == 0


def test_apply_aging_increments_days(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        erika = session.scalar(select(Character).where(Character.key == "erika"))
        assert erika is not None
        erika.age_days = 100
        session.commit()

    with factory() as session:
        birthdays = apply_aging(session)
        session.commit()
    assert birthdays == 0

    with factory() as session:
        erika = session.scalar(select(Character).where(Character.key == "erika"))
        assert erika is not None
        assert erika.age_days == 101
        assert erika.age_years == 14


def test_apply_aging_birthday(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        erika = session.scalar(select(Character).where(Character.key == "erika"))
        assert erika is not None
        erika.age_days = DAYS_PER_YEAR - 1
        erika.age_years = 14
        session.commit()

    with factory() as session:
        birthdays = apply_aging(session)
        session.commit()
    assert birthdays == 1

    with factory() as session:
        erika = session.scalar(select(Character).where(Character.key == "erika"))
        assert erika is not None
        assert erika.age_days == 0
        assert erika.age_years == 15


def test_apply_aging_wraps_after_432(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Dopo 432 tick, erika passa da 14y 0d a 15y 0d."""
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        erika = session.scalar(select(Character).where(Character.key == "erika"))
        assert erika is not None
        erika.age_days = 0
        erika.age_years = 14
        session.commit()

    with factory() as session:
        for _ in range(DAYS_PER_YEAR):
            apply_aging(session)
        session.commit()

    with factory() as session:
        erika = session.scalar(select(Character).where(Character.key == "erika"))
        assert erika is not None
        assert erika.age_years == 15
        assert erika.age_days == 0


def test_apply_aging_counts_all_characters(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Con il seed (erika 24d, max 32d, giulia/luca/player 0d),
    dopo 432 tick tutti e 5 scattano il compleanno una volta.

    erika scatta a tick 408 (24 + 408 = 432), max a tick 400
    (32 + 400 = 432), giulia/luca/player a tick 432.
    """
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        total = 0
        for _ in range(DAYS_PER_YEAR):
            total += apply_aging(session)
        session.commit()
    assert total == 5


def test_lifecycle_kills_at_100(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from simai.npc.lifecycle import LifecycleManager
    from simai.world.enums import DeathCause

    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        erika = session.scalar(select(Character).where(Character.key == "erika"))
        assert erika is not None
        erika.age_years = 100
        erika.age_days = 0
        session.commit()

    with factory() as session:
        kills, deliveries = LifecycleManager().daily_tick(session, tick_index=28, master_seed=42)
        session.commit()

    assert len(kills) == 1
    assert kills[0].character_key == "erika"
    assert kills[0].cause == DeathCause.OLD_AGE
    assert deliveries == []

    with factory() as session:
        erika = session.scalar(select(Character).where(Character.key == "erika"))
    assert erika is None


def test_lifecycle_delivers_due_pregnancy(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from simai.npc.lifecycle import LifecycleManager
    from simai.npc.pregnancy import PREGNANCY_DAYS, conceive

    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        conceive(session, "giulia", "luca", tick_index=28, master_seed=42)
        session.commit()

    due_tick = 28 + PREGNANCY_DAYS * 28
    # Arrotonda al primo daily_tick >= due_tick
    aligned = ((due_tick + 27) // 28) * 28

    with factory() as session:
        kills, deliveries = LifecycleManager().daily_tick(
            session, tick_index=aligned, master_seed=42
        )
        session.commit()
    assert kills == []
    assert len(deliveries) == 1
    assert deliveries[0].success
    assert len(deliveries[0].children_keys) >= 1
