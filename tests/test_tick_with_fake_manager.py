from pathlib import Path

import pytest
from alembic import command
from sqlalchemy.engine import Engine

from simai.actions.enums import ActionKind
from simai.db.alembic_utils import get_alembic_config
from simai.db.session import get_engine, get_session_factory
from simai.needs.enums import NeedKind
from simai.npc.manager import NPCState
from simai.sim.reports import TickDecision
from simai.sim.tick import run_tick
from simai.world.seed import seed_muse_core


class FakeNPCManager:
    def __init__(self, decisions: list[TickDecision]) -> None:
        self._decisions = decisions
        self.called_load = False
        self.called_update_all = False
        self.load_args: dict[str, bool] = {}

    def load(self, session, *, include_player: bool) -> list[NPCState]:  # type: ignore[no-untyped-def]
        self.called_load = True
        self.load_args["include_player"] = include_player
        return []

    def update_all(  # type: ignore[no-untyped-def]
        self,
        session,
        states,
        *,
        tick_index: int,
        master_seed: int,
    ) -> list[TickDecision]:
        self.called_update_all = True
        return list(self._decisions)


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


def test_run_tick_uses_injected_manager(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    fake_decision = TickDecision(
        character_id=999,
        character_key="fake",
        location_key="casa",
        action=ActionKind.EAT,
        satisfied=NeedKind.HUNGER,
        value_before=50.0,
        value_after=90.0,
    )
    fake = FakeNPCManager([fake_decision])
    with factory() as session:
        report = run_tick(
            session,
            minutes=60,
            tick_index=0,
            master_seed=42,
            npc_manager=fake,
        )
        session.commit()
    assert fake.called_load
    assert fake.called_update_all
    assert fake.load_args["include_player"] is False
    assert len(report.decisions) == 1
    assert report.decisions[0].character_key == "fake"


def test_run_tick_passes_include_player_to_manager(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    fake = FakeNPCManager([])
    with factory() as session:
        run_tick(
            session,
            minutes=60,
            tick_index=0,
            master_seed=42,
            include_player=True,
            npc_manager=fake,
        )
        session.commit()
    assert fake.load_args["include_player"] is True


def test_run_tick_default_manager_produces_real_decisions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        report = run_tick(
            session,
            minutes=60,
            tick_index=0,
            master_seed=42,
        )
        session.commit()
    # 4 NPC, 4 decisioni (una per NPC), player escluso.
    assert len(report.decisions) == 4
    for d in report.decisions:
        assert d.character_key in {"erika", "max", "luca", "giulia"}
