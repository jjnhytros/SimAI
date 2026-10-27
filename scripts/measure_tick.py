"""Misura query/tick e profilo CPU su N tick. Uso: uv run python scripts/measure_tick.py"""

import cProfile
import pstats
import sys
import tempfile
from pathlib import Path

from alembic import command
from sqlalchemy import event

from simai.db.alembic_utils import get_alembic_config
from simai.db.session import get_engine, get_session_factory
from simai.sim.tick import run_tick
from simai.world.seed import seed_muse_core

TICKS = 200


def setup_db() -> tuple:
    tmp = Path(tempfile.mkdtemp(prefix="simai-measure-"))
    url = f"sqlite:///{tmp / 'm.db'}"
    command.upgrade(get_alembic_config(url=url), "head")
    engine = get_engine(url)
    factory = get_session_factory(engine)
    with factory() as session:
        seed_muse_core(session)
        session.commit()
    return engine, factory


def measure_queries(engine, factory) -> int:
    queries: list[str] = []

    @event.listens_for(engine, "before_cursor_execute")
    def _count(conn, cursor, statement, parameters, context, executemany):
        queries.append(statement)

    with factory() as session:
        for _ in range(TICKS):
            run_tick(session, minutes=60)
            session.commit()

    event.remove(engine, "before_cursor_execute", _count)
    return len(queries)


def profile(factory) -> None:
    with factory() as session:
        profiler = cProfile.Profile()
        profiler.enable()
        for _ in range(TICKS):
            run_tick(session, minutes=60)
            session.commit()
        profiler.disable()
    stats = pstats.Stats(profiler, stream=sys.stdout)
    stats.sort_stats("cumulative").print_stats(25)


if __name__ == "__main__":
    engine, factory = setup_db()
    q = measure_queries(engine, factory)
    print(f"\nQuery totali su {TICKS} tick: {q}")
    print(f"Query per tick: {q / TICKS:.2f}")
    print("\n=== Profiling ===\n")
    profile(factory)
