from pathlib import Path

import pytest
from sqlalchemy import select
from sqlalchemy.engine import Engine

from alembic import command
from simai.actions.catalog import CATALOG, actions_for_location
from simai.actions.enums import ActionKind
from simai.actions.utility import filter_by_need_threshold
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


def test_catalog_thresholds_match_design() -> None:
    thresholds = {a.kind: a.max_need_to_start for a in CATALOG}
    assert thresholds[ActionKind.EAT] == 30
    assert thresholds[ActionKind.DRINK] == 40
    assert thresholds[ActionKind.PLAY] == 70
    assert thresholds[ActionKind.SOCIALIZE] == 70


def test_filter_hides_eat_above_threshold() -> None:
    available = actions_for_location(LocationKind.LEISURE)
    needs = {
        NeedKind.HUNGER: 80.0,
        NeedKind.THIRST: 50.0,
        NeedKind.FUN: 90.0,
        NeedKind.INTIMACY: 90.0,
    }
    result = filter_by_need_threshold(available, needs)
    kinds = {a.kind for a in result}
    assert ActionKind.EAT not in kinds
    # DRINK soglia 40, thirst 50 -> non disponibile
    assert ActionKind.DRINK not in kinds
    # PLAY soglia 70, fun 90 -> non disponibile
    assert ActionKind.PLAY not in kinds
    assert ActionKind.SOCIALIZE not in kinds


def test_filter_shows_eat_below_threshold() -> None:
    available = actions_for_location(LocationKind.LEISURE)
    needs = {
        NeedKind.HUNGER: 25.0,
        NeedKind.THIRST: 100.0,
        NeedKind.FUN: 100.0,
        NeedKind.INTIMACY: 100.0,
    }
    result = filter_by_need_threshold(available, needs)
    kinds = {a.kind for a in result}
    assert kinds == {ActionKind.EAT}


def test_filter_uses_threshold_not_fixed_value() -> None:
    available = actions_for_location(LocationKind.LEISURE)
    # hunger 31: sopra soglia EAT (30), non disponibile
    needs = {
        NeedKind.HUNGER: 31.0,
        NeedKind.THIRST: 100.0,
        NeedKind.FUN: 100.0,
        NeedKind.INTIMACY: 100.0,
    }
    result = filter_by_need_threshold(available, needs)
    assert ActionKind.EAT not in {a.kind for a in result}


def test_erika_eats_when_hungry_then_skips(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Erika a casa: con hunger 0 mangia. Poi per due tick è sazia e
    salta. Poi torna a mangiare quando hunger scende sotto 30."""
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)

    with factory() as session:
        erika = session.scalar(select(Character).where(Character.key == "erika"))
        assert erika is not None
        needs = session.scalars(select(Need).where(Need.character_id == erika.id)).all()
        for n in needs:
            n.value = 0.0 if n.kind == NeedKind.HUNGER else 100.0
        session.commit()

    # Tick 0: hunger 0 -> EAT -> 40
    with factory() as session:
        r0 = run_tick(session, minutes=60, tick_index=0, master_seed=42)
        session.commit()
    d0 = next(d for d in r0.decisions if d.character_key == "erika")
    assert d0.action == ActionKind.EAT

    # Tick 1: hunger 40 - 6 = 34 > 30 -> skip
    with factory() as session:
        r1 = run_tick(session, minutes=60, tick_index=1, master_seed=42)
        session.commit()
    d1 = next(d for d in r1.decisions if d.character_key == "erika")
    assert d1.action is None

    # Tick 2: hunger 34 - 6 = 28 < 30 -> EAT -> 68
    with factory() as session:
        r2 = run_tick(session, minutes=60, tick_index=2, master_seed=42)
        session.commit()
    d2 = next(d for d in r2.decisions if d.character_key == "erika")
    assert d2.action == ActionKind.EAT


def test_all_needs_above_threshold_skips_turn(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)

    with factory() as session:
        erika = session.scalar(select(Character).where(Character.key == "erika"))
        assert erika is not None
        needs = session.scalars(select(Need).where(Need.character_id == erika.id)).all()
        for n in needs:
            n.value = 100.0
        session.commit()

    with factory() as session:
        report = run_tick(session, minutes=1, tick_index=0, master_seed=42)
        session.commit()
    d = next(d for d in report.decisions if d.character_key == "erika")
    # 1 minuto di decay: tutti a 100 - epsilon, ancora sopra soglia.
    # Nessuna azione con soglia <= 100 (tranne niente) -> skip.
    # Ma PLAY soglia 70, fun 99.93 > 70 -> non disponibile.
    assert d.action is None
