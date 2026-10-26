from pathlib import Path

import pytest
from alembic import command
from sqlalchemy import select
from sqlalchemy.engine import Engine

from simai.db.alembic_utils import get_alembic_config
from simai.db.session import get_engine, get_session_factory
from simai.needs.enums import NeedKind
from simai.needs.service import (
    VALUE_MIN,
    apply_decay,
    decay_value,
    needs_of,
)
from simai.world.models import Character
from simai.world.seed import seed_muse_core


def _engine(tmp_path: Path) -> Engine:
    url = f"sqlite:///{tmp_path / 'test.db'}"
    command.upgrade(get_alembic_config(url=url), "head")
    return get_engine(url)


def test_seed_creates_four_needs_per_character(tmp_path: Path) -> None:
    engine = _engine(tmp_path)
    factory = get_session_factory(engine)
    with factory() as session:
        seed_muse_core(session)
        session.commit()
    with factory() as session:
        for char in session.scalars(select(Character)).all():
            assert len(needs_of(session, char.id)) == 4


def test_seed_needs_is_idempotent(tmp_path: Path) -> None:
    engine = _engine(tmp_path)
    factory = get_session_factory(engine)
    with factory() as session:
        seed_muse_core(session)
        session.commit()
    with factory() as session:
        report = seed_muse_core(session)
        session.commit()
    assert report["needs_created"] == 0


def test_decay_value_proportional() -> None:
    # HUNGER 100, 60 minuti -> -4 -> 96
    assert decay_value(100.0, NeedKind.HUNGER, 60) == pytest.approx(96.0)


def test_decay_floors_at_zero() -> None:
    assert decay_value(10.0, NeedKind.HUNGER, 10_000) == VALUE_MIN


def test_decay_no_op_for_zero_minutes() -> None:
    assert decay_value(50.0, NeedKind.FUN, 0) == 50.0


def test_decay_negative_minutes_clamped() -> None:
    assert decay_value(50.0, NeedKind.FUN, -10) == 50.0


def test_apply_decay_persists(tmp_path: Path) -> None:
    """Decadimento senza tratti (player): tutti i bisogni scendono
    del valore base."""
    engine = _engine(tmp_path)
    factory = get_session_factory(engine)
    with factory() as session:
        seed_muse_core(session)
        session.commit()
    with factory() as session:
        cid = session.scalars(select(Character.id).where(Character.key == "player")).one()
        # traits=None: apply_decay legge dal personaggio (player=[])
        apply_decay(session, cid, 120)
        session.commit()
    with factory() as session:
        values = needs_of(session, cid)
    # 120 min = 2h -> HUNGER -8, THIRST -10, FUN -6, INTIMACY -3
    assert values[NeedKind.HUNGER] == pytest.approx(92.0)
    assert values[NeedKind.THIRST] == pytest.approx(90.0)
    assert values[NeedKind.FUN] == pytest.approx(94.0)
    assert values[NeedKind.INTIMACY] == pytest.approx(97.0)


def test_apply_decay_with_solitary_trait(
    tmp_path: Path,
) -> None:
    """Erika (solitary): INTIMACY decade *0.60."""
    engine = _engine(tmp_path)
    factory = get_session_factory(engine)
    with factory() as session:
        seed_muse_core(session)
        session.commit()
    with factory() as session:
        cid = session.scalars(select(Character.id).where(Character.key == "erika")).one()
        apply_decay(session, cid, 120)
        session.commit()
    with factory() as session:
        values = needs_of(session, cid)
    # 120 min = 2h
    # HUNGER -8 (nessun tratto su hunger)
    assert values[NeedKind.HUNGER] == pytest.approx(92.0)
    # THIRST -10 (nessun tratto)
    assert values[NeedKind.THIRST] == pytest.approx(90.0)
    # FUN -6 (nessun tratto)
    assert values[NeedKind.FUN] == pytest.approx(94.0)
    # INTIMACY: 1.5 * 0.60 = 0.9/h * 2h = 1.8 -> 98.2
    assert values[NeedKind.INTIMACY] == pytest.approx(98.2)
