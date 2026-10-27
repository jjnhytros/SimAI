"""Test opzionali di simulazione accelerata.

Marcati `slow`: esclusi di default. Eseguire con:
    pytest -m slow
"""

from pathlib import Path

import pytest

from simai.sim.benchmark import run_benchmark

pytestmark = pytest.mark.slow


def test_one_year_simulation(tmp_path: Path) -> None:
    db = tmp_path / "bench_1y.db"
    report = run_benchmark(db, years=1.0, sample_every=336)
    assert report.ticks == 12096
    assert report.invariants_ok, report.invariant_violations
    assert report.relationships_active == 2
    # Almeno un NPC mantiene mood medio > 0.
    npcs = [c for c in report.characters if not c.is_player]
    assert any(c.mood_mean > 20 for c in npcs)
