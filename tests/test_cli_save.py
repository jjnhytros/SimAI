from pathlib import Path

import pytest
from typer.testing import CliRunner

from alembic import command
from simai.cli.app import app
from simai.db.alembic_utils import get_alembic_config

runner = CliRunner()


def _setup(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    url = f"sqlite:///{tmp_path / 'cli.db'}"
    saves_dir = tmp_path / "saves"
    monkeypatch.setenv("SIMAI_DB_URL", url)
    monkeypatch.setenv("SIMAI_SAVES_DIR", str(saves_dir))
    command.upgrade(get_alembic_config(url=url), "head")
    runner.invoke(app, ["world", "seed"])


def test_save_create_and_list(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _setup(tmp_path, monkeypatch)
    r1 = runner.invoke(app, ["save", "create", "-n", "first"])
    assert r1.exit_code == 0, r1.stdout
    assert "Salvataggio creato" in r1.stdout

    r2 = runner.invoke(app, ["save", "list"])
    assert r2.exit_code == 0
    assert "first" in r2.stdout


def test_save_load_roundtrip(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _setup(tmp_path, monkeypatch)
    runner.invoke(app, ["sim", "tick"])
    runner.invoke(app, ["save", "create", "-n", "t1"])
    runner.invoke(app, ["sim", "tick"])
    runner.invoke(app, ["sim", "tick"])

    state_before = runner.invoke(app, ["sim", "state"])
    assert "tick_index: 3" in state_before.stdout

    load = runner.invoke(app, ["save", "load", "t1", "--yes"])
    assert load.exit_code == 0, load.stdout

    state_after = runner.invoke(app, ["sim", "state"])
    assert "tick_index: 1" in state_after.stdout


def test_save_load_requires_confirm_without_yes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _setup(tmp_path, monkeypatch)
    runner.invoke(app, ["save", "create", "-n", "c"])
    # CliRunner non è TTY: senza --yes, la conferma fallisce con exit != 0
    result = runner.invoke(app, ["save", "load", "c"])
    assert result.exit_code != 0


def test_save_load_unknown(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _setup(tmp_path, monkeypatch)
    result = runner.invoke(app, ["save", "load", "nope", "--yes"])
    assert result.exit_code == 1
    combined = (result.stdout or "") + (result.stderr or "")
    assert "non trovato" in combined.lower()


def test_save_inspect(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _setup(tmp_path, monkeypatch)
    runner.invoke(app, ["save", "create", "-n", "meta"])
    result = runner.invoke(app, ["save", "inspect", "meta"])
    assert result.exit_code == 0
    assert "Tick:" in result.stdout
    assert "Checksum:" in result.stdout
