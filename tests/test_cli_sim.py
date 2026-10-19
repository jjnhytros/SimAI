from pathlib import Path

import pytest
from typer.testing import CliRunner

from alembic import command
from simai.cli.app import app
from simai.db.alembic_utils import get_alembic_config

runner = CliRunner()


def _setup(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    url = f"sqlite:///{tmp_path / 'cli.db'}"
    monkeypatch.setenv("SIMAI_DB_URL", url)
    command.upgrade(get_alembic_config(url=url), "head")
    runner.invoke(app, ["world", "seed"])


def test_sim_tick_outputs_report(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _setup(tmp_path, monkeypatch)
    result = runner.invoke(app, ["sim", "tick", "-m", "60", "--tick", "0"])
    assert result.exit_code == 0, result.stdout
    assert "Tick 0" in result.stdout
    assert "60 minuti" in result.stdout
    for key in ("erika", "max", "luca", "giulia"):
        assert key in result.stdout
    assert "player" not in result.stdout


def test_sim_tick_include_player(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _setup(tmp_path, monkeypatch)
    result = runner.invoke(app, ["sim", "tick", "-m", "60", "--include-player"])
    assert result.exit_code == 0
    assert "player" in result.stdout


def test_sim_tick_deterministic_across_fresh_dbs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    urls = [f"sqlite:///{tmp_path / n}" for n in ("a.db", "b.db")]
    for url in urls:
        monkeypatch.setenv("SIMAI_DB_URL", url)
        command.upgrade(get_alembic_config(url=url), "head")
        runner.invoke(app, ["world", "seed"])

    monkeypatch.setenv("SIMAI_DB_URL", urls[0])
    r1 = runner.invoke(app, ["sim", "tick", "-m", "60", "--tick", "0"])
    monkeypatch.setenv("SIMAI_DB_URL", urls[1])
    r2 = runner.invoke(app, ["sim", "tick", "-m", "60", "--tick", "0"])
    assert r1.exit_code == 0
    assert r2.exit_code == 0
    assert r1.stdout == r2.stdout


def test_sim_tick_on_empty_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    url = f"sqlite:///{tmp_path / 'empty.db'}"
    monkeypatch.setenv("SIMAI_DB_URL", url)
    result = runner.invoke(app, ["sim", "tick"])
    assert result.exit_code == 1
    combined = (result.stdout or "") + (result.stderr or "")
    assert "Database non inizializzato" in combined
    assert "Traceback" not in combined
