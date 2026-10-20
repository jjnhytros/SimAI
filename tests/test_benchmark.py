from pathlib import Path

import pytest

from simai.sim.benchmark import (
    TICKS_PER_YEAR,
    run_benchmark,
)


def test_ticks_per_year_constant() -> None:
    assert TICKS_PER_YEAR == 8760


def test_run_benchmark_short(tmp_path: Path) -> None:
    db = tmp_path / "bench.db"
    report = run_benchmark(db, years=0.01, sample_every=1)
    # 0.01 * 8760 = 87.6 -> 87
    assert report.ticks == 87
    assert report.invariants_ok
    assert report.relationships_active >= 0
    assert len(report.characters) == 5


def test_run_benchmark_no_player_decisions(tmp_path: Path) -> None:
    db = tmp_path / "bench.db"
    report = run_benchmark(db, years=0.005, sample_every=1)
    players = [c for c in report.characters if c.is_player]
    assert len(players) == 1
    # Player non agisce: bisogni a 0 dopo abbastanza tempo.
    p = players[0]
    assert p.needs_final["hunger"] < 50


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
