from pathlib import Path

import pytest

from simai.sim.benchmark import (
    TICKS_PER_YEAR,
    run_benchmark,
)


def test_ticks_per_year_constant() -> None:
    assert TICKS_PER_YEAR == 12096


def test_run_benchmark_short(tmp_path: Path) -> None:
    db = tmp_path / "bench.db"
    report = run_benchmark(db, years=0.01, sample_every=1)
    # 0.01 * 12096 = 120.96 -> 120
    assert report.ticks == 120
    assert report.invariants_ok
    assert report.relationships_active >= 0
    # Player escluso di default
    assert len(report.characters) == 4
    assert all(not c.is_player for c in report.characters)


def test_run_benchmark_no_player_decisions(
    tmp_path: Path,
) -> None:
    db = tmp_path / "bench.db"
    report = run_benchmark(db, years=0.005, sample_every=1)
    # Player escluso: non c'è modo di verificare "no decisions"
    # dal report se non appare. Verifichiamo esplicitamente che
    # nessun character nel report sia il player.
    assert all(not c.is_player for c in report.characters)
    assert len(report.characters) == 4


def test_run_benchmark_includes_player_when_asked(
    tmp_path: Path,
) -> None:
    db = tmp_path / "bench.db"
    report = run_benchmark(db, years=0.001, sample_every=1, include_player=True)
    players = [c for c in report.characters if c.is_player]
    assert len(players) == 1
    assert len(report.characters) == 5


def test_run_benchmark_invalid_args(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        run_benchmark(tmp_path / "b.db", years=0)
    with pytest.raises(ValueError):
        run_benchmark(tmp_path / "b.db", years=1, minutes_per_tick=0)
    with pytest.raises(ValueError):
        run_benchmark(tmp_path / "b.db", years=1, sample_every=0)


def test_report_serializes_to_json(tmp_path: Path) -> None:
    db = tmp_path / "bench.db"
    report = run_benchmark(db, years=0.001)
    payload = report.to_json()
    assert '"ticks"' in payload
    assert '"characters"' in payload
    assert '"invariants_ok"' in payload


def test_run_benchmark_reports_balance(tmp_path: Path) -> None:
    db = tmp_path / "bench.db"
    report = run_benchmark(db, years=0.01, sample_every=1)
    assert report.salary_transactions >= 0
    assert report.purchase_transactions >= 0
    for c in report.characters:
        assert c.balance_final >= 0.0
        assert c.balance_mean >= 0.0


def test_run_benchmark_death_count_field(tmp_path: Path) -> None:
    """Il report espone death_count, anche se 0 sul seed attuale."""
    db = tmp_path / "bench.db"
    report = run_benchmark(db, years=0.01, sample_every=1)
    assert report.death_count == 0
