from pathlib import Path

import pytest
from alembic import command
from typer.testing import CliRunner

from simai.cli.app import app
from simai.db.alembic_utils import get_alembic_config

runner = CliRunner()


def _setup(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    url = f"sqlite:///{tmp_path / 'cli.db'}"
    monkeypatch.setenv("SIMAI_DB_URL", url)
    monkeypatch.setenv("SIMAI_SAVES_DIR", str(tmp_path / "saves"))
    command.upgrade(get_alembic_config(url=url), "head")
    runner.invoke(app, ["world", "seed"])


def test_watch_rejects_zero_ticks(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _setup(tmp_path, monkeypatch)
    result = runner.invoke(app, ["watch", "run", "--ticks", "0"])
    assert result.exit_code == 1
    combined = (result.stdout or "") + (result.stderr or "")
    assert "--ticks" in combined


def test_watch_on_empty_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    url = f"sqlite:///{tmp_path / 'empty.db'}"
    monkeypatch.setenv("SIMAI_DB_URL", url)
    result = runner.invoke(app, ["watch", "run", "--ticks", "1"])
    assert result.exit_code == 1
    combined = (result.stdout or "") + (result.stderr or "")
    assert "Database non inizializzato" in combined


def test_watch_runs_and_advances_state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _setup(tmp_path, monkeypatch)
    result = runner.invoke(
        app,
        ["watch", "run", "--ticks", "3", "--delay", "0"],
    )
    assert result.exit_code == 0, result.stdout
    state = runner.invoke(app, ["sim", "state"])
    assert "tick_index: 3" in state.stdout


def test_watch_include_player(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _setup(tmp_path, monkeypatch)
    result = runner.invoke(
        app,
        [
            "watch",
            "run",
            "--ticks",
            "2",
            "--delay",
            "0",
            "--include-player",
        ],
    )
    assert result.exit_code == 0
