from pathlib import Path

from typer.testing import CliRunner

from simai.cli.app import app

runner = CliRunner()


def test_sim_benchmark_short(tmp_path: Path) -> None:
    out = tmp_path / "report.json"
    db = tmp_path / "bench.db"
    result = runner.invoke(
        app,
        [
            "sim",
            "benchmark",
            "--years",
            "0.001",
            "--db",
            str(db),
            "--output",
            str(out),
        ],
    )
    assert result.exit_code == 0, result.stdout
    assert "Benchmark" in result.stdout
    assert "Invarianti: OK" in result.stdout
    assert out.exists()
    assert '"ticks"' in out.read_text()


def test_sim_benchmark_rejects_bad_years(tmp_path: Path) -> None:
    db = tmp_path / "bench.db"
    result = runner.invoke(
        app,
        ["sim", "benchmark", "--years", "0", "--db", str(db)],
    )
    assert result.exit_code == 1
    combined = (result.stdout or "") + (result.stderr or "")
    assert "years must be > 0" in combined
