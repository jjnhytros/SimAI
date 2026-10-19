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


def test_sim_state_initial(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _setup(tmp_path, monkeypatch)
    result = runner.invoke(app, ["sim", "state"])
    assert result.exit_code == 0, result.stdout
    assert "tick_index: 0" in result.stdout
    assert "master_seed: 42" in result.stdout


def test_sim_tick_uses_and_increments_persisted_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _setup(tmp_path, monkeypatch)
    r1 = runner.invoke(app, ["sim", "tick", "-m", "60"])
    assert r1.exit_code == 0
    assert "Tick 0" in r1.stdout

    r2 = runner.invoke(app, ["sim", "tick", "-m", "60"])
    assert r2.exit_code == 0
    assert "Tick 1" in r2.stdout

    r3 = runner.invoke(app, ["sim", "state"])
    assert "tick_index: 2" in r3.stdout


def test_sim_tick_explicit_tick_does_not_advance_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _setup(tmp_path, monkeypatch)
    runner.invoke(app, ["sim", "tick", "--tick", "10"])
    result = runner.invoke(app, ["sim", "state"])
    assert "tick_index: 0" in result.stdout


def test_sim_reset(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _setup(tmp_path, monkeypatch)
    runner.invoke(app, ["sim", "tick"])
    runner.invoke(app, ["sim", "tick"])
    result = runner.invoke(app, ["sim", "reset", "--seed", "123"])
    assert result.exit_code == 0
    assert "master_seed: 123" in result.stdout

    state = runner.invoke(app, ["sim", "state"])
    assert "tick_index: 0" in state.stdout
    assert "master_seed: 123" in state.stdout
