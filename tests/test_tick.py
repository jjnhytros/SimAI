from pathlib import Path

import pytest
from sqlalchemy import select
from sqlalchemy.engine import Engine

from alembic import command
from simai.actions.catalog import CATALOG
from simai.actions.enums import ActionKind
from simai.db.alembic_utils import get_alembic_config
from simai.db.session import get_engine, get_session_factory
from simai.needs.service import apply_effect
from simai.sim.tick import run_tick
from simai.world.models import Character
from simai.world.seed import seed_muse_core


def _seeded(tmp_path: Path) -> Engine:
    url = f"sqlite:///{tmp_path / 'test.db'}"
    command.upgrade(get_alembic_config(url=url), "head")
    engine = get_engine(url)
    factory = get_session_factory(engine)
    with factory() as session:
        seed_muse_core(session)
        session.commit()
    return engine


def test_run_tick_produces_decision_per_npc(tmp_path: Path) -> None:
    engine = _seeded(tmp_path)
    factory = get_session_factory(engine)
    with factory() as session:
        report = run_tick(session, minutes=60, tick_index=0, master_seed=42)
        session.commit()
    assert len(report.decisions) == 4


def test_run_tick_applies_effect_or_skips(tmp_path: Path) -> None:
    engine = _seeded(tmp_path)
    factory = get_session_factory(engine)
    with factory() as session:
        report = run_tick(session, minutes=60, tick_index=0, master_seed=42)
        session.commit()
    for d in report.decisions:
        if d.action is None:
            continue
        assert d.value_before is not None
        assert d.value_after is not None
        assert d.value_after >= d.value_before


def test_run_tick_is_deterministic_across_fresh_dbs(
    tmp_path: Path,
) -> None:
    def run(label: str) -> list[ActionKind | None]:
        engine = _seeded(tmp_path / label)
        factory = get_session_factory(engine)
        with factory() as session:
            report = run_tick(session, minutes=60, tick_index=0, master_seed=42)
            session.rollback()
        return [d.action for d in report.decisions]

    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    assert run("a") == run("b")


def test_run_tick_skips_player_by_default(tmp_path: Path) -> None:
    engine = _seeded(tmp_path)
    factory = get_session_factory(engine)
    with factory() as session:
        report = run_tick(session, minutes=60, tick_index=0, master_seed=42)
        session.commit()
    keys = {d.character_key for d in report.decisions}
    assert keys == {"erika", "max", "luca", "giulia"}


def test_run_tick_includes_player_when_asked(tmp_path: Path) -> None:
    engine = _seeded(tmp_path)
    factory = get_session_factory(engine)
    with factory() as session:
        report = run_tick(
            session,
            minutes=60,
            tick_index=0,
            master_seed=42,
            include_player=True,
        )
        session.commit()
    keys = {d.character_key for d in report.decisions}
    assert "player" in keys
    assert len(report.decisions) == 5


def test_run_tick_rejects_non_positive_minutes(tmp_path: Path) -> None:
    engine = _seeded(tmp_path)
    factory = get_session_factory(engine)
    with factory() as session, pytest.raises(ValueError):
        run_tick(session, minutes=0, tick_index=0, master_seed=42)


def test_run_tick_rejects_negative_tick(tmp_path: Path) -> None:
    engine = _seeded(tmp_path)
    factory = get_session_factory(engine)
    with factory() as session, pytest.raises(ValueError):
        run_tick(session, minutes=60, tick_index=-1, master_seed=42)


def test_apply_effect_clamps_at_100(tmp_path: Path) -> None:
    engine = _seeded(tmp_path)
    factory = get_session_factory(engine)
    eat = next(a for a in CATALOG if a.kind == ActionKind.EAT)
    with factory() as session:
        char = session.scalar(select(Character).where(Character.key == "erika"))
        assert char is not None
        value = apply_effect(session, char.id, eat)
        assert value == 100.0
