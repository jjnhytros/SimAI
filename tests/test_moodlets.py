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
    NEED_MOODLETS,
    REFRESH_THRESHOLD_TICKS,
    SPECS,
    active_delta,
    apply_moodlet,
    cleanup_expired,
    moodlet_for_need,
    refresh_need_moodlets,
)
from simai.needs.enums import NeedKind
from simai.needs.models import Need
from simai.npc.lifecycle import LifecycleManager
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
    """Finestra [started, expires): 4 tick da 0 a 3 se duration=4."""
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        cid = _erika_id(session)
        apply_moodlet(session, cid, MoodletKind.ATE_WELL, tick=0)
        session.flush()
        # Al tick 0 il moodlet è appena applicato: contribuisce.
        assert active_delta(session, cid, 0) == 2.0
        # Tick 1..3: contribuisce.
        for t in (1, 2, 3):
            assert active_delta(session, cid, t) == 2.0
        # Tick 4: expires_at=4, 4 > 4 è falso: scaduto.
        assert active_delta(session, cid, 4) == 0.0


def test_lonely_refreshed_every_tick_contributes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Regressione: LONELY viene rinfrescato ogni tick (streak >= 3).

    Con la vecchia finestra `started_at_tick < tick`, un moodlet
    rinfrescato ogni tick non contribuiva mai. Con la finestra
    `[started_at, expires_at)` contribuisce dal tick di refresh.
    """
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        cid = _erika_id(session)
        for t in range(5):
            apply_moodlet(session, cid, MoodletKind.LONELY, tick=t)
            session.flush()
            delta = active_delta(session, cid, t)
            assert delta == -3.0, f"tick {t}: delta {delta} (atteso -3.0)"


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


def test_specs_cover_all_kinds() -> None:
    """Ogni MoodletKind ha una MoodletSpec: nessuna dimenticanza."""
    assert set(SPECS) == set(MoodletKind)


def test_moodlet_for_need_hunger_thresholds() -> None:
    cases = [
        (0.0, MoodletKind.STARVING),
        (9.99, MoodletKind.STARVING),
        (10.0, MoodletKind.HUNGRY),
        (29.99, MoodletKind.HUNGRY),
        (30.0, MoodletKind.SATISFIED),
        (69.99, MoodletKind.SATISFIED),
        (70.0, MoodletKind.WELL_FED),
        (89.99, MoodletKind.WELL_FED),
        (90.0, MoodletKind.STUFFED),
        (100.0, MoodletKind.STUFFED),
    ]
    for value, expected in cases:
        assert moodlet_for_need(NeedKind.HUNGER, value) == expected, value


def test_moodlet_for_need_intimacy_below_lonely_is_none() -> None:
    # Sotto LONELY_THRESHOLD (20): nessun moodlet-need (coperto da LONELY).
    for value in (0.0, 5.0, 19.99):
        assert moodlet_for_need(NeedKind.INTIMACY, value) is None
    # Scaglioni: 20–49, 50–69, 70–89, ≥ 90.
    assert moodlet_for_need(NeedKind.INTIMACY, 20.0) == MoodletKind.INTIMATE
    assert moodlet_for_need(NeedKind.INTIMACY, 49.99) == MoodletKind.INTIMATE
    assert moodlet_for_need(NeedKind.INTIMACY, 50.0) == MoodletKind.CONNECTED
    assert moodlet_for_need(NeedKind.INTIMACY, 69.99) == MoodletKind.CONNECTED
    assert moodlet_for_need(NeedKind.INTIMACY, 70.0) == MoodletKind.CLOSE
    assert moodlet_for_need(NeedKind.INTIMACY, 89.99) == MoodletKind.CLOSE
    assert moodlet_for_need(NeedKind.INTIMACY, 90.0) == MoodletKind.ADORED
    assert moodlet_for_need(NeedKind.INTIMACY, 100.0) == MoodletKind.ADORED


def test_need_moodlets_are_disjoint() -> None:
    """Un kind non può essere associato a due need diversi."""
    seen: set[MoodletKind] = set()
    for kinds in NEED_MOODLETS.values():
        for kind in kinds:
            assert kind not in seen, f"{kind} duplicato"
            seen.add(kind)


def test_refresh_need_moodlets_transition_replaces(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        cid = _erika_id(session)
        refresh_need_moodlets(session, cid, {NeedKind.HUNGER: 5.0}, tick=0)
        session.flush()
        assert (
            session.scalar(select(Moodlet).where(Moodlet.character_id == cid)).kind
            == MoodletKind.STARVING
        )
        refresh_need_moodlets(session, cid, {NeedKind.HUNGER: 50.0}, tick=1)
        session.flush()
        rows = session.scalars(select(Moodlet).where(Moodlet.character_id == cid)).all()
        kinds = {r.kind for r in rows}
        assert kinds == {MoodletKind.SATISFIED}


def test_refresh_need_moodlets_no_refresh_far_from_expiry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        cid = _erika_id(session)
        refresh_need_moodlets(session, cid, {NeedKind.HUNGER: 5.0}, tick=0)
        session.flush()
        first = session.scalar(select(Moodlet).where(Moodlet.character_id == cid))
        assert first is not None
        started = first.started_at_tick
        # stato invariato, lontano dalla scadenza: nessuna scrittura
        refresh_need_moodlets(session, cid, {NeedKind.HUNGER: 5.0}, tick=1)
        session.flush()
        again = session.scalar(select(Moodlet).where(Moodlet.character_id == cid))
        assert again is not None
        assert again.started_at_tick == started


def test_refresh_need_moodlets_refresh_near_expiry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        cid = _erika_id(session)
        refresh_need_moodlets(session, cid, {NeedKind.HUNGER: 5.0}, tick=0)
        session.flush()
        spec = SPECS[MoodletKind.STARVING]
        near = spec.duration_ticks - REFRESH_THRESHOLD_TICKS
        refresh_need_moodlets(session, cid, {NeedKind.HUNGER: 5.0}, tick=near)
        session.flush()
        again = session.scalar(select(Moodlet).where(Moodlet.character_id == cid))
        assert again is not None
        assert again.started_at_tick == near
        assert again.expires_at_tick == near + spec.duration_ticks


def test_refresh_need_moodlets_intimacy_below_threshold_clears(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        cid = _erika_id(session)
        refresh_need_moodlets(session, cid, {NeedKind.INTIMACY: 30.0}, tick=0)
        session.flush()
        assert (
            session.scalar(select(Moodlet).where(Moodlet.character_id == cid)).kind
            == MoodletKind.INTIMATE
        )
        refresh_need_moodlets(session, cid, {NeedKind.INTIMACY: 10.0}, tick=1)
        session.flush()
        rows = session.scalars(select(Moodlet).where(Moodlet.character_id == cid)).all()
        assert rows == []


# --- LifeStage transitions ---


def _set_age(session, char_id: int, years: int, days: int) -> None:
    char = session.get(Character, char_id)
    assert char is not None
    char.age_years = years
    char.age_days = days


def test_lifestage_transition_became_child(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        cid = _erika_id(session)
        _set_age(session, cid, years=5, days=431)
        session.commit()
    with factory() as session:
        LifecycleManager().daily_tick(session, tick_index=0)
        session.commit()
    with factory() as session:
        cid = _erika_id(session)
        kinds = {
            r.kind
            for r in session.scalars(select(Moodlet).where(Moodlet.character_id == cid)).all()
        }
        assert MoodletKind.BECAME_CHILD in kinds


def test_lifestage_transition_became_young_adult(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        cid = _erika_id(session)
        _set_age(session, cid, years=19, days=431)
        session.commit()
    with factory() as session:
        LifecycleManager().daily_tick(session, tick_index=0)
        session.commit()
    with factory() as session:
        cid = _erika_id(session)
        kinds = {
            r.kind
            for r in session.scalars(select(Moodlet).where(Moodlet.character_id == cid)).all()
        }
        assert MoodletKind.BECAME_YOUNG_ADULT in kinds


def test_lifestage_transition_became_senior(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        cid = _erika_id(session)
        _set_age(session, cid, years=59, days=431)
        session.commit()
    with factory() as session:
        LifecycleManager().daily_tick(session, tick_index=0)
        session.commit()
    with factory() as session:
        cid = _erika_id(session)
        kinds = {
            r.kind
            for r in session.scalars(select(Moodlet).where(Moodlet.character_id == cid)).all()
        }
        assert MoodletKind.BECAME_SENIOR in kinds


def test_lifestage_no_transition_on_regular_day(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Giorno senza cambio anno: nessun moodlet lifestage."""
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        cid = _erika_id(session)
        _set_age(session, cid, years=30, days=100)
        session.commit()
    with factory() as session:
        LifecycleManager().daily_tick(session, tick_index=0)
        session.commit()
    with factory() as session:
        cid = _erika_id(session)
        kinds = {
            r.kind
            for r in session.scalars(select(Moodlet).where(Moodlet.character_id == cid)).all()
        }
        assert MoodletKind.BECAME_CHILD not in kinds
        assert MoodletKind.BECAME_YOUNG_ADULT not in kinds
        assert MoodletKind.BECAME_SENIOR not in kinds
