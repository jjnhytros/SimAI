from pathlib import Path

from alembic import command
from sqlalchemy.engine import Engine

from simai.db.alembic_utils import get_alembic_config
from simai.db.session import get_engine, get_session_factory
from simai.sim.state import get_state, reset_state


def _engine(tmp_path: Path) -> Engine:
    url = f"sqlite:///{tmp_path / 'test.db'}"
    command.upgrade(get_alembic_config(url=url), "head")
    return get_engine(url)


def test_migration_seeds_singleton(tmp_path: Path) -> None:
    engine = _engine(tmp_path)
    factory = get_session_factory(engine)
    with factory() as session:
        state = get_state(session)
        assert state.tick_index == 0
        assert state.master_seed == 42


def test_get_state_is_idempotent(tmp_path: Path) -> None:
    engine = _engine(tmp_path)
    factory = get_session_factory(engine)
    with factory() as session:
        s1 = get_state(session)
        s2 = get_state(session)
        assert s1.id == s2.id == 1


def test_reset_state_sets_seed(tmp_path: Path) -> None:
    engine = _engine(tmp_path)
    factory = get_session_factory(engine)
    with factory() as session:
        state = get_state(session)
        state.tick_index = 17
        session.flush()
        reset_state(session, master_seed=999)
        session.commit()
    with factory() as session:
        state = get_state(session)
        assert state.tick_index == 0
        assert state.master_seed == 999
