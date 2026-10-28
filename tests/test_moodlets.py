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
    refresh_need_moodlets_many,
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


# --- Test esistenti (1.9.0), invariati ---


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
        assert active_delta(session, cid, 0) == 2.0
        for t in (1, 2, 3):
            assert active_delta(session, cid, t) == 2.0
        assert active_delta(session, cid, 4) == 0.0


def test_lonely_refreshed_every_tick_contributes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
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

    with factory() as session:
        run_tick(session, minutes=1, tick_index=0, master_seed=42)
        session.commit()

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


# --- Test 0.1100 ---


def test_specs_cover_all_kinds() -> None:
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
    for value in (0.0, 5.0, 19.99):
        assert moodlet_for_need(NeedKind.INTIMACY, value) is None
    assert moodlet_for_need(NeedKind.INTIMACY, 20.0) == MoodletKind.INTIMATE
    assert moodlet_for_need(NeedKind.INTIMACY, 49.99) == MoodletKind.INTIMATE
    assert moodlet_for_need(NeedKind.INTIMACY, 50.0) == MoodletKind.CONNECTED
    assert moodlet_for_need(NeedKind.INTIMACY, 69.99) == MoodletKind.CONNECTED
    assert moodlet_for_need(NeedKind.INTIMACY, 70.0) == MoodletKind.CLOSE
    assert moodlet_for_need(NeedKind.INTIMACY, 89.99) == MoodletKind.CLOSE
    assert moodlet_for_need(NeedKind.INTIMACY, 90.0) == MoodletKind.ADORED
    assert moodlet_for_need(NeedKind.INTIMACY, 100.0) == MoodletKind.ADORED


def test_need_moodlets_are_disjoint() -> None:
    seen: set[MoodletKind] = set()
    for kinds in NEED_MOODLETS.values():
        for kind in kinds:
            assert kind not in seen, f"{kind} duplicato"
            seen.add(kind)


# --- Test 0.1101 (B3): Δ positivi a +0.5 ---


def test_need_moodlet_positive_deltas_are_small() -> None:
    """B3: i 13 Δ positivi need-based sono +0.5, non +2/+3/+4/+5."""
    positive = 0
    for need_kinds in NEED_MOODLETS.values():
        for kind in need_kinds:
            spec = SPECS[kind]
            if spec.delta_per_tick > 0:
                assert spec.delta_per_tick == 0.5, f"{kind}: {spec.delta_per_tick}"
                positive += 1
    assert positive == 13


def test_need_moodlet_negative_deltas_unchanged() -> None:
    """I 6 Δ negativi restano invariati."""
    expected = {
        MoodletKind.STARVING: -15.0,
        MoodletKind.HUNGRY: -6.0,
        MoodletKind.DEHYDRATED: -15.0,
        MoodletKind.THIRSTY: -6.0,
        MoodletKind.MISERABLE: -12.0,
        MoodletKind.BORED: -5.0,
    }
    for kind, delta in expected.items():
        assert SPECS[kind].delta_per_tick == delta


# --- Test 0.1101: refresh batch ---


def test_refresh_many_transition_updates_not_recreates(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """La transizione deve fare UPDATE del kind, non DELETE+INSERT."""
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        cid = _erika_id(session)
        refresh_need_moodlets_many(session, {cid: {NeedKind.HUNGER: 5.0}}, tick=0)
        session.flush()
        first = session.scalar(select(Moodlet).where(Moodlet.character_id == cid))
        assert first is not None
        first_id = first.id
        refresh_need_moodlets_many(session, {cid: {NeedKind.HUNGER: 50.0}}, tick=1)
        session.flush()
        rows = session.scalars(select(Moodlet).where(Moodlet.character_id == cid)).all()
        assert len(rows) == 1
        assert rows[0].id == first_id  # UPDATE, non nuovo record
        assert rows[0].kind == MoodletKind.SATISFIED
        assert rows[0].need == NeedKind.HUNGER


def test_refresh_many_no_refresh_far_from_expiry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        cid = _erika_id(session)
        refresh_need_moodlets_many(session, {cid: {NeedKind.HUNGER: 5.0}}, tick=0)
        session.flush()
        first = session.scalar(select(Moodlet).where(Moodlet.character_id == cid))
        assert first is not None
        started = first.started_at_tick
        refresh_need_moodlets_many(session, {cid: {NeedKind.HUNGER: 5.0}}, tick=1)
        session.flush()
        again = session.scalar(select(Moodlet).where(Moodlet.character_id == cid))
        assert again is not None
        assert again.started_at_tick == started


def test_refresh_many_refresh_near_expiry(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        cid = _erika_id(session)
        refresh_need_moodlets_many(session, {cid: {NeedKind.HUNGER: 5.0}}, tick=0)
        session.flush()
        spec = SPECS[MoodletKind.STARVING]
        near = spec.duration_ticks - REFRESH_THRESHOLD_TICKS
        refresh_need_moodlets_many(session, {cid: {NeedKind.HUNGER: 5.0}}, tick=near)
        session.flush()
        again = session.scalar(select(Moodlet).where(Moodlet.character_id == cid))
        assert again is not None
        assert again.started_at_tick == near
        assert again.expires_at_tick == near + spec.duration_ticks


def test_refresh_many_intimacy_below_threshold_clears(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        cid = _erika_id(session)
        refresh_need_moodlets_many(session, {cid: {NeedKind.INTIMACY: 30.0}}, tick=0)
        session.flush()
        row = session.scalar(select(Moodlet).where(Moodlet.character_id == cid))
        assert row is not None
        assert row.kind == MoodletKind.INTIMATE
        refresh_need_moodlets_many(session, {cid: {NeedKind.INTIMACY: 10.0}}, tick=1)
        session.flush()
        assert session.scalars(select(Moodlet).where(Moodlet.character_id == cid)).all() == []


def test_refresh_many_batch_multiple_characters(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Un solo SELECT per tutti i char: verifica funzionale del batch."""
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        chars = session.scalars(select(Character)).all()
        ids = [c.id for c in chars]
        needs_by_char = {cid: {NeedKind.HUNGER: 5.0} for cid in ids}
        refresh_need_moodlets_many(session, needs_by_char, tick=0)
        session.flush()
        rows = session.scalars(select(Moodlet)).all()
        assert len(rows) == len(ids)
        assert all(r.kind == MoodletKind.STARVING for r in rows)


# --- Test coerenza update_mood(needs=...) ---


def test_update_mood_with_needs_matches_internal_query(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from simai.mood.service import update_mood
    from simai.needs.service import needs_of

    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        cid = _erika_id(session)
        needs = needs_of(session, cid)
        mood_without = update_mood(session, cid, tick=0)
        mood_with = update_mood(session, cid, tick=0, needs=needs)
        assert mood_without == mood_with


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
