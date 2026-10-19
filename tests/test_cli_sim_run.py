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
    monkeypatch.setenv("SIMAI_SAVES_DIR", str(tmp_path / "saves"))
    command.upgrade(get_alembic_config(url=url), "head")
    runner.invoke(app, ["world", "seed"])


def test_sim_run_advances_state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _setup(tmp_path, monkeypatch)
    result = runner.invoke(app, ["sim", "run", "--ticks", "3", "-m", "60"])
    assert result.exit_code == 0, result.stdout
    assert "Eseguiti 3 tick" in result.stdout

    state = runner.invoke(app, ["sim", "state"])
    assert "tick_index: 3" in state.stdout


def test_sim_run_autosave(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _setup(tmp_path, monkeypatch)
    result = runner.invoke(
        app,
        [
            "sim",
            "run",
            "--ticks",
            "4",
            "--autosave-every",
            "2",
            "--autosave-name",
            "auto",
        ],
    )
    assert result.exit_code == 0
    assert "Autosave (2)" in result.stdout
    assert "auto_t2.sav" in result.stdout
    assert "auto_t4.sav" in result.stdout

    saves = runner.invoke(app, ["save", "list"])
    assert "auto_t2" in saves.stdout
    assert "auto_t4" in saves.stdout


def test_sim_run_quiet(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _setup(tmp_path, monkeypatch)
    result = runner.invoke(app, ["sim", "run", "--ticks", "2", "--quiet"])
    assert result.exit_code == 0
    # Nessuna riga per-tick
    assert "Tick 0 —" not in result.stdout
    assert "Tick 1 —" not in result.stdout
    assert "Eseguiti 2 tick" in result.stdout


def test_sim_run_rejects_zero_ticks(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _setup(tmp_path, monkeypatch)
    result = runner.invoke(app, ["sim", "run", "--ticks", "0"])
    assert result.exit_code == 1
    combined = (result.stdout or "") + (result.stderr or "")
    assert "ticks must be > 0" in combined


def test_sim_run_empty_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    url = f"sqlite:///{tmp_path / 'empty.db'}"
    monkeypatch.setenv("SIMAI_DB_URL", url)
    result = runner.invoke(app, ["sim", "run", "--ticks", "3"])
    assert result.exit_code == 1
    combined = (result.stdout or "") + (result.stderr or "")
    assert "Database non inizializzato" in combined
