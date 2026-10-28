from pathlib import Path

import pytest
from alembic import command
from sqlalchemy import select
from sqlalchemy.engine import Engine

from simai.db.alembic_utils import get_alembic_config
from simai.db.session import get_engine, get_session_factory
from simai.npc.pregnancy import (
    PREGNANCY_DAYS,
    conceive,
    deliver,
    due_pregnancies,
    roll_twins,
)
from simai.relationships.enums import RelationshipKind
from simai.relationships.models import Relationship
from simai.world.models import Character, Pregnancy
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


def test_roll_twins_distribution() -> None:
    import random

    rng = random.Random(0)
    counts: dict[int, int] = {1: 0, 2: 0}
    for _ in range(10000):
        n, _ = roll_twins(rng)
        counts[n] += 1
    assert 10000 * 0.60 < counts[1] < 10000 * 0.75
    assert 10000 * 0.25 < counts[2] < 10000 * 0.40


def test_conceive_creates_pregnancy(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        result = conceive(session, "giulia", "luca", tick_index=100, master_seed=42)
        session.commit()
    assert result.success
    assert result.due_at_tick == 100 + PREGNANCY_DAYS * 28


def test_conceive_rejects_minor(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        result = conceive(session, "erika", "max", tick_index=0, master_seed=42)
        session.commit()
    assert not result.success
    assert "18" in (result.error or "")


def test_conceive_rejects_existing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        conceive(session, "giulia", "luca", tick_index=0, master_seed=42)
        session.commit()
        result = conceive(session, "giulia", "luca", tick_index=0, master_seed=42)
        session.commit()
    assert not result.success
    assert "già" in (result.error or "")


def test_deliver_creates_children_and_relationships(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        conceive(session, "giulia", "luca", tick_index=0, master_seed=42)
        session.commit()

    with factory() as session:
        pregnancy = session.scalar(select(Pregnancy))
        assert pregnancy is not None
        result = deliver(session, pregnancy, master_seed=42)
        session.commit()
    assert result.success
    assert len(result.children_keys) >= 1

    with factory() as session:
        for key in result.children_keys:
            child = session.scalar(select(Character).where(Character.key == key))
            assert child is not None
            assert child.age_years == 0
            assert child.age_days == 0
        # Nessuna gravidanza rimasta
        remaining = session.scalars(select(Pregnancy)).all()
        assert remaining == []


def test_deliver_creates_parent_relationships(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        conceive(session, "giulia", "luca", tick_index=0, master_seed=42)
        session.commit()

    with factory() as session:
        pregnancy = session.scalar(select(Pregnancy))
        assert pregnancy is not None
        result = deliver(session, pregnancy, master_seed=42)
        session.commit()

    with factory() as session:
        giulia = session.scalar(select(Character).where(Character.key == "giulia"))
        luca = session.scalar(select(Character).where(Character.key == "luca"))
        assert giulia is not None and luca is not None
        for key in result.children_keys:
            child = session.scalar(select(Character).where(Character.key == key))
            assert child is not None
            rels = session.scalars(
                select(Relationship).where(
                    Relationship.to_character_id == child.id,
                )
            ).all()
            kinds = {(r.from_character_id, r.kind) for r in rels}
            assert (giulia.id, RelationshipKind.PARENT_OF) in kinds
            assert (luca.id, RelationshipKind.PARENT_OF) in kinds


def test_due_pregnancies(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        conceive(session, "giulia", "luca", tick_index=100, master_seed=42)
        session.commit()
    with factory() as session:
        due_before = due_pregnancies(session, 200)
        due_after = due_pregnancies(session, 999999)
    assert due_before == []
    assert len(due_after) == 1
