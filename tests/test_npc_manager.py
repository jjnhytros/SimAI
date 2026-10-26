from pathlib import Path

import pytest
from alembic import command
from sqlalchemy.engine import Engine

from simai.db.alembic_utils import get_alembic_config
from simai.db.session import get_engine, get_session_factory
from simai.needs.enums import NeedKind
from simai.npc.manager import NPCManager
from simai.world.models import Location
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


def _manager() -> NPCManager:
    return NPCManager()


def test_load_excludes_player_by_default(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        states = _manager().load(session, include_player=False)
    assert len(states) == 4
    assert all(not s.is_player for s in states)


def test_load_includes_player_when_requested(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        states = _manager().load(session, include_player=True)
    assert len(states) == 5
    assert any(s.is_player for s in states)


def test_load_populates_needs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        states = _manager().load(session, include_player=False)
    for state in states:
        assert set(state.needs.keys()) == set(NeedKind)


def test_load_populates_traits(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        states = _manager().load(session, include_player=False)
    by_key = {s.key: s for s in states}
    assert by_key["erika"].traits == ["solitary"]
    assert by_key["max"].traits == ["energetic"]
    assert by_key["luca"].traits == ["social"]
    assert by_key["giulia"].traits == ["lazy", "glutton"]


def test_update_all_returns_one_decision_per_npc(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    manager = _manager()
    with factory() as session:
        states = manager.load(session, include_player=False)
        decisions = manager.update_all(session, states, tick_index=0, master_seed=42)
        session.commit()
    assert len(decisions) == 4


def test_update_all_sorted_by_character_id(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    manager = _manager()
    with factory() as session:
        states = manager.load(session, include_player=False)
        reversed_states = list(reversed(states))
        decisions = manager.update_all(session, reversed_states, tick_index=0, master_seed=42)
        session.commit()
    ids = [d.character_id for d in decisions]
    assert ids == sorted(ids)


def test_update_all_updates_state_location(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    manager = _manager()
    with factory() as session:
        states = manager.load(session, include_player=False)
        # erika: a casa, lavoro a piazza. tick 7 → BEFORE_WORK,
        # ticks_until=1 ≤ PRIORITY_WINDOW=2. Si muove.
        erika_state = next(s for s in states if s.key == "erika")
        location_before = erika_state.location_id
        erika_state.needs[NeedKind.HUNGER] = 100.0
        decisions = manager.update_all(session, [erika_state], tick_index=7, master_seed=42)
        session.commit()
        assert len(decisions) == 1
        assert decisions[0].moved_to == "piazza"
        # La sync deve aver aggiornato state.location_id.
        assert erika_state.location_id != location_before
        piazza = session.query(Location).filter_by(key="piazza").one()
        assert erika_state.location_id == piazza.id


def test_tick_one_moves_to_work_within_priority_window(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    manager = _manager()
    with factory() as session:
        states = manager.load(session, include_player=False)
        erika_state = next(s for s in states if s.key == "erika")
        # erika è a casa, job a piazza, schedule_start=8.
        # tick 7 → BEFORE_WORK, ticks_until=1 ≤ PRIORITY_WINDOW=2.
        erika_state.needs[NeedKind.HUNGER] = 100.0
        decisions = manager.update_all(session, [erika_state], tick_index=7, master_seed=42)
        session.commit()
    assert len(decisions) == 1
    d = decisions[0]
    assert d.moved_to == "piazza"
    assert d.action is None


def test_tick_one_respects_hunger_safeguard(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    manager = _manager()
    with factory() as session:
        states = manager.load(session, include_player=False)
        erika_state = next(s for s in states if s.key == "erika")
        # Hunger < 10 → priorità lavoro decade.
        erika_state.needs[NeedKind.HUNGER] = 5.0
        decisions = manager.update_all(session, [erika_state], tick_index=7, master_seed=42)
        session.commit()
    assert len(decisions) == 1
    d = decisions[0]
    # Non si muove verso il lavoro: ha fame critica e la
    # salvaguardia fa decadere la priorità.
    assert d.moved_to != "piazza"


def test_npc_manager_like_is_structural(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """NPCManager soddisfa NPCManagerLike strutturalmente."""
    from simai.npc.manager import NPCManagerLike

    manager: NPCManagerLike = NPCManager()
    assert callable(manager.load)
    assert callable(manager.update_all)
