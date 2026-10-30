from pathlib import Path

import pytest
from alembic import command
from sqlalchemy import select
from sqlalchemy.engine import Engine

from simai.db.alembic_utils import get_alembic_config
from simai.db.session import get_engine, get_session_factory
from simai.mood.enums import MoodletKind
from simai.mood.models import Moodlet
from simai.npc.intimacy.service import (
    apply_intimacy_moodlets,
    best_intimacy_level,
    intimacy_level,
    intimacy_levels_of,
)
from simai.relationships.models import Relationship
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


def _char_id(session, key: str) -> int:
    c = session.scalar(select(Character).where(Character.key == key))
    assert c is not None
    return c.id


def test_intimacy_level_boundaries() -> None:
    assert intimacy_level(0.0) == 0
    assert intimacy_level(19.99) == 0
    assert intimacy_level(20.0) == 1
    assert intimacy_level(39.99) == 1
    assert intimacy_level(40.0) == 2
    assert intimacy_level(59.99) == 2
    assert intimacy_level(60.0) == 3
    assert intimacy_level(79.99) == 3
    assert intimacy_level(80.0) == 4
    assert intimacy_level(94.99) == 4
    assert intimacy_level(95.0) == 5
    assert intimacy_level(100.0) == 5


def test_best_intimacy_level_no_relationships(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Player non ha relazioni di seed: best = 0."""
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        player_id = _char_id(session, "player")
        assert best_intimacy_level(session, player_id) == 0


def test_best_intimacy_level_erika_max(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Erika ha FRIEND 60 con Max, PARENT_OF/CHILD_OF 80 con Giulia.

    Il max strength è 80 → level 4.
    """
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        erika_id = _char_id(session, "erika")
        assert best_intimacy_level(session, erika_id) == 4


def test_intimacy_levels_of_returns_dict(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        erika_id = _char_id(session, "erika")
        levels = intimacy_levels_of(session, erika_id)
    assert "max" in levels
    assert "giulia" in levels
    assert levels["max"] == 3  # 60
    assert levels["giulia"] == 4  # 80


def test_apply_intimacy_moodlets_romantic(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Erika ha relationship a 80 (level 4) → ROMANTIC."""
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        erika_id = _char_id(session, "erika")
        kind = apply_intimacy_moodlets(session, erika_id, tick=0)
        session.flush()
    assert kind == MoodletKind.ROMANTIC


def test_apply_intimacy_moodlets_devoted(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Alzo la strength di Erika a 98 → DEVOTED."""
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        erika_id = _char_id(session, "erika")
        for rel in session.scalars(
            select(Relationship).where(Relationship.from_character_id == erika_id)
        ).all():
            rel.strength = 98.0
        session.flush()
        kind = apply_intimacy_moodlets(session, erika_id, tick=0)
        session.flush()
    assert kind == MoodletKind.DEVOTED


def test_apply_intimacy_moodlets_none_below_80(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Player senza relazioni → nessun moodlet."""
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        player_id = _char_id(session, "player")
        kind = apply_intimacy_moodlets(session, player_id, tick=0)
        session.flush()
    assert kind is None


def test_apply_intimacy_moodlets_no_duplicate_refresh(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Due chiamate consecutive non duplicano il moodlet, refreshano."""
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        erika_id = _char_id(session, "erika")
        apply_intimacy_moodlets(session, erika_id, tick=0)
        apply_intimacy_moodlets(session, erika_id, tick=1)
        session.flush()
        rows = session.scalars(
            select(Moodlet).where(
                Moodlet.character_id == erika_id,
                Moodlet.kind == MoodletKind.ROMANTIC,
            )
        ).all()
    assert len(rows) == 1

def test_apply_intimacy_moodlets_many_multi_char(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Batch: erika e max hanno level 4 (strength 80) → ROMANTIC."""
    from simai.npc.intimacy.service import apply_intimacy_moodlets_many

    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        ids = [_char_id(session, "erika"), _char_id(session, "max")]
        applied = apply_intimacy_moodlets_many(session, ids, tick=0)
        session.flush()
    assert applied == {ids[0]: MoodletKind.ROMANTIC, ids[1]: MoodletKind.ROMANTIC}


def test_apply_intimacy_moodlets_many_refresh_near_expiry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Batch: secondo tick non duplica, refresha in-place."""
    from simai.npc.intimacy.service import apply_intimacy_moodlets_many

    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        ids = [_char_id(session, "erika")]
        apply_intimacy_moodlets_many(session, ids, tick=0)
        apply_intimacy_moodlets_many(session, ids, tick=1)
        session.flush()
        rows = session.scalars(
            select(Moodlet).where(
                Moodlet.character_id == ids[0],
                Moodlet.kind == MoodletKind.ROMANTIC,
            )
        ).all()
    assert len(rows) == 1


