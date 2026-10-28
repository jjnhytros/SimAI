from pathlib import Path

import pytest
from alembic import command
from sqlalchemy import select
from sqlalchemy.engine import Engine

from simai.db.alembic_utils import get_alembic_config
from simai.db.session import get_engine, get_session_factory
from simai.npc.death import MAX_AGE_YEARS, check_age, kill
from simai.world.enums import DeathCause
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


def test_kill_removes_character(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        result = kill(session, "erika", cause=DeathCause.MANUAL, tick_index=0)
        session.commit()
        assert result.success
        assert result.cause == DeathCause.MANUAL
    with factory() as session:
        erika = session.scalar(select(Character).where(Character.key == "erika"))
    assert erika is None


def test_kill_unknown_character(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        result = kill(session, "nobody", cause=DeathCause.MANUAL, tick_index=0)
        session.commit()
        assert not result.success
        assert result.error is not None


def test_kill_distributes_balance(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        erika = session.scalar(select(Character).where(Character.key == "erika"))
        giulia = session.scalar(select(Character).where(Character.key == "giulia"))
        assert erika is not None and giulia is not None
        erika.balance = 100.0
        giulia_before = giulia.balance
        session.commit()

        result = kill(session, "erika", cause=DeathCause.MANUAL, tick_index=0)
        session.commit()
        assert result.success
        assert result.inheritance is not None
        assert result.inheritance.allocations == {"giulia": 100.0}
    with factory() as session:
        giulia = session.scalar(select(Character).where(Character.key == "giulia"))
        assert giulia is not None
        assert giulia.balance == giulia_before + 100.0


def test_kill_cancels_relationships(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from simai.relationships.models import Relationship

    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        erika = session.scalar(select(Character).where(Character.key == "erika"))
        assert erika is not None
        erika_id = erika.id
        kill(session, "erika", cause=DeathCause.MANUAL, tick_index=0)
        session.commit()
    with factory() as session:
        erika_rels = session.scalars(
            select(Relationship).where(
                (Relationship.from_character_id == erika_id)
                | (Relationship.to_character_id == erika_id)
            )
        ).all()
    assert erika_rels == []


def test_check_age_kills_at_100(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        erika = session.scalar(select(Character).where(Character.key == "erika"))
        assert erika is not None
        erika.age_years = MAX_AGE_YEARS
        session.commit()

        kills = check_age(session, tick_index=0)
        session.commit()
        assert len(kills) == 1
        assert kills[0].character_key == "erika"
        assert kills[0].cause == DeathCause.OLD_AGE
    with factory() as session:
        erika = session.scalar(select(Character).where(Character.key == "erika"))
    assert erika is None


def test_check_age_no_kill_below_100(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        kills = check_age(session, tick_index=0)
        session.commit()
    assert kills == []
