from pathlib import Path

import pytest
from sqlalchemy import select
from sqlalchemy.engine import Engine

from alembic import command
from simai.db.alembic_utils import get_alembic_config
from simai.db.session import get_engine, get_session_factory
from simai.mood.service import (
    MOOD_WEIGHTS,
    compute_mood,
    mood_label,
    update_mood,
)
from simai.needs.enums import NeedKind
from simai.needs.models import Need
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


def test_compute_mood_all_full() -> None:
    needs = {k: 100.0 for k in NeedKind}
    assert compute_mood(needs) == 100.0


def test_compute_mood_all_zero() -> None:
    needs = {k: 0.0 for k in NeedKind}
    assert compute_mood(needs) == 0.0


def test_compute_mood_weighted() -> None:
    # FUN a 0, altri a 100 -> mood = 1 - peso_fun = 0.70 -> 70
    needs = {k: 100.0 for k in NeedKind}
    needs[NeedKind.FUN] = 0.0
    assert compute_mood(needs) == pytest.approx(100.0 * (1 - MOOD_WEIGHTS[NeedKind.FUN]))


def test_compute_mood_missing_need_counts_as_zero() -> None:
    needs = {NeedKind.HUNGER: 100.0}
    # manca tutto il resto -> mood = 25.0
    assert compute_mood(needs) == pytest.approx(100.0 * MOOD_WEIGHTS[NeedKind.HUNGER])


def test_mood_label_thresholds() -> None:
    assert mood_label(100.0) == "sereno"
    assert mood_label(80.0) == "sereno"
    assert mood_label(60.0) == "tranquillo"
    assert mood_label(40.0) == "così così"
    assert mood_label(20.0) == "giù"
    assert mood_label(0.0) == "a terra"


def test_seed_sets_mood_to_100(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        chars = session.scalars(select(Character)).all()
        assert all(c.mood == 100.0 for c in chars)


def test_update_mood_reflects_needs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        erika = session.scalar(select(Character).where(Character.key == "erika"))
        assert erika is not None
        # Abbasso HUNGER a 0
        need = session.scalar(
            select(Need).where(
                Need.character_id == erika.id,
                Need.kind == NeedKind.HUNGER,
            )
        )
        assert need is not None
        need.value = 0.0
        session.flush()
        mood = update_mood(session, erika.id)
        session.commit()
    assert mood == pytest.approx(100.0 * (1 - MOOD_WEIGHTS[NeedKind.HUNGER]))
