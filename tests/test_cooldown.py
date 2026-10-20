from pathlib import Path

import pytest
from sqlalchemy import select
from sqlalchemy.engine import Engine

from alembic import command
from simai.actions.catalog import CATALOG, actions_for_location
from simai.actions.enums import ActionKind
from simai.actions.utility import filter_by_cooldown
from simai.db.alembic_utils import get_alembic_config
from simai.db.session import get_engine, get_session_factory
from simai.needs.enums import NeedKind
from simai.needs.models import Need
from simai.sim.tick import run_tick
from simai.world.enums import LocationKind
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


def test_catalog_cooldowns_match_design() -> None:
    cooldowns = {a.kind: a.cooldown_ticks for a in CATALOG}
    assert cooldowns[ActionKind.EAT] == 8
    assert cooldowns[ActionKind.DRINK] == 4
    assert cooldowns[ActionKind.PLAY] == 8
    assert cooldowns[ActionKind.SOCIALIZE] == 12


def test_filter_removes_action_in_cooldown() -> None:
    available = actions_for_location(LocationKind.LEISURE)
    result = filter_by_cooldown(
        available,
        current_tick=5,
        last_satisfied={NeedKind.HUNGER: 5},
    )
    kinds = {a.kind for a in result}
    assert ActionKind.EAT not in kinds
    assert ActionKind.DRINK in kinds
    assert ActionKind.PLAY in kinds
    assert ActionKind.SOCIALIZE in kinds


def test_filter_keeps_expired_cooldown() -> None:
    available = actions_for_location(LocationKind.LEISURE)
    result = filter_by_cooldown(
        available,
        current_tick=10,
        last_satisfied={NeedKind.HUNGER: 2},
    )
    kinds = {a.kind for a in result}
    assert ActionKind.EAT in kinds


def test_filter_no_history() -> None:
    available = actions_for_location(LocationKind.LEISURE)
    result = filter_by_cooldown(available, current_tick=5, last_satisfied={})
    assert len(result) == len(available)


def test_erika_eats_then_skips_due_to_cooldown(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)

    with factory() as session:
        erika = session.scalar(select(Character).where(Character.key == "erika"))
        assert erika is not None
        needs = session.scalars(select(Need).where(Need.character_id == erika.id)).all()
        for n in needs:
            n.value = 0.0 if n.kind == NeedKind.HUNGER else 100.0
            n.last_satisfied_at_tick = None
        session.commit()

    with factory() as session:
        r0 = run_tick(session, minutes=60, tick_index=0, master_seed=42)
        session.commit()
    d0 = next(d for d in r0.decisions if d.character_key == "erika")
    assert d0.action == ActionKind.EAT

    with factory() as session:
        r1 = run_tick(session, minutes=60, tick_index=1, master_seed=42)
        session.commit()
    d1 = next(d for d in r1.decisions if d.character_key == "erika")
    # EAT in cooldown: deve essere PLAY (unica altra azione a casa)
    assert d1.action == ActionKind.PLAY

    with factory() as session:
        r2 = run_tick(session, minutes=60, tick_index=2, master_seed=42)
        session.commit()
    d2 = next(d for d in r2.decisions if d.character_key == "erika")
    # EAT e PLAY in cooldown: deve essere NESSUNA AZIONE
    assert d2.action is None
