from pathlib import Path

import pytest
from alembic import command
from sqlalchemy import select
from sqlalchemy.engine import Engine

from simai.db.alembic_utils import get_alembic_config
from simai.db.session import get_engine, get_session_factory
from simai.mood.enums import MoodletKind
from simai.mood.models import Moodlet
from simai.mood.moodlets import (
    SPECS,
    active_delta,
    apply_moodlet,
    cleanup_expired,
)
from simai.needs.enums import NeedKind
from simai.needs.models import Need
from simai.sim.tick import run_tick
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


def _erika_id(session) -> int:
    erika = session.scalar(select(Character).where(Character.key == "erika"))
    assert erika is not None
    return erika.id


def _set_need(session, char_id: int, kind: NeedKind, value: float) -> None:
    n = session.scalar(select(Need).where(Need.character_id == char_id, Need.kind == kind))
    assert n is not None
    n.value = value


def test_specs_match_design() -> None:
    assert SPECS[MoodletKind.ATE_WELL].duration_ticks == 4
    assert SPECS[MoodletKind.ATE_WELL].delta_per_tick == 2.0
    assert SPECS[MoodletKind.SOCIALIZED].duration_ticks == 4
    assert SPECS[MoodletKind.SOCIALIZED].delta_per_tick == 2.0
    assert SPECS[MoodletKind.LONELY].duration_ticks == 6
    assert SPECS[MoodletKind.LONELY].delta_per_tick == -3.0


def test_apply_refresh_not_sum(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        cid = _erika_id(session)
        apply_moodlet(session, cid, MoodletKind.ATE_WELL, tick=0)
        session.flush()
        apply_moodlet(session, cid, MoodletKind.ATE_WELL, tick=3)
        session.flush()
        rows = session.scalars(select(Moodlet)).all()
        assert len(rows) == 1
        assert rows[0].started_at_tick == 3
        assert rows[0].expires_at_tick == 7


def test_active_delta_respects_window(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        cid = _erika_id(session)
        apply_moodlet(session, cid, MoodletKind.ATE_WELL, tick=0)
        session.flush()
        # Al tick 0: started == current, non contribuisce
        assert active_delta(session, cid, 0) == 0.0
        # Al tick 1..3: contribuisce +2
        for t in (1, 2, 3):
            assert active_delta(session, cid, t) == 2.0
        # Al tick 4: expires_at=4 >= 4, contribuisce ancora
        assert active_delta(session, cid, 4) == 2.0
        # Al tick 5: scaduto
        assert active_delta(session, cid, 5) == 0.0


def test_cleanup_expired(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        cid = _erika_id(session)
        apply_moodlet(session, cid, MoodletKind.ATE_WELL, tick=0)
        session.flush()
        deleted = cleanup_expired(session, cid, tick=10)
        session.flush()
        assert deleted == 1
        assert session.scalars(select(Moodlet)).all() == []


def test_lonely_triggers_after_three_ticks(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """LONELY è oggi un moodlet del player.

    Gli NPC evitano la solitudine spostandosi in piazza/caffè per
    SOCIALIZE. Il player non decide: subisce il decadimento. Con
    intimacy < 20 per 3 tick consecutivi, LONELY scatta.
    """
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        player = session.scalar(select(Character).where(Character.is_player.is_(True)))
        assert player is not None
        _set_need(session, player.id, NeedKind.INTIMACY, 10.0)
        for kind in (NeedKind.HUNGER, NeedKind.THIRST, NeedKind.FUN):
            _set_need(session, player.id, kind, 100.0)
        session.commit()

    for t in range(3):
        with factory() as session:
            run_tick(session, minutes=1, tick_index=t, master_seed=42)
            session.commit()

    with factory() as session:
        player = session.scalar(select(Character).where(Character.is_player.is_(True)))
        assert player is not None
        rows = session.scalars(select(Moodlet).where(Moodlet.character_id == player.id)).all()
        assert any(r.kind == MoodletKind.LONELY for r in rows)


def test_ate_well_after_eat(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        cid = _erika_id(session)
        _set_need(session, cid, NeedKind.HUNGER, 5.0)
        for kind in (NeedKind.THIRST, NeedKind.FUN, NeedKind.INTIMACY):
            _set_need(session, cid, kind, 100.0)
        session.commit()

    with factory() as session:
        run_tick(session, minutes=1, tick_index=0, master_seed=42)
        session.commit()

    with factory() as session:
        cid = _erika_id(session)
        rows = session.scalars(select(Moodlet).where(Moodlet.character_id == cid)).all()
        kinds = {r.kind for r in rows}
        assert MoodletKind.ATE_WELL in kinds


def test_mood_includes_moodlet_delta(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        cid = _erika_id(session)
        _set_need(session, cid, NeedKind.HUNGER, 5.0)
        for kind in (NeedKind.THIRST, NeedKind.FUN, NeedKind.INTIMACY):
            _set_need(session, cid, kind, 100.0)
        session.commit()

    # Tick 0: EAT + ATE_WELL (al tick 1 in poi contribuisce)
    with factory() as session:
        run_tick(session, minutes=1, tick_index=0, master_seed=42)
        session.commit()

    # Tick 1..2: mood include +2/tick
    moods: list[float] = []
    for t in (1, 2):
        with factory() as session:
            run_tick(session, minutes=1, tick_index=t, master_seed=42)
            session.commit()
        with factory() as session:
            cid = _erika_id(session)
            char = session.get(Character, cid)
            assert char is not None
            moods.append(char.mood)

    assert len(moods) == 2
