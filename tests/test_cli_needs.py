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


def test_needs_show_lists_all_kinds(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _setup(tmp_path, monkeypatch)
    result = runner.invoke(app, ["needs", "show", "--character", "erika"])
    assert result.exit_code == 0
    for kind in ("hunger", "thirst", "fun", "intimacy"):
        assert kind in result.stdout.lower()
    assert "100.0" in result.stdout


def test_needs_decay_changes_values(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _setup(tmp_path, monkeypatch)
    result = runner.invoke(
        app,
        ["needs", "decay", "--character", "erika", "--minutes", "120"],
    )
    assert result.exit_code == 0
    assert "88.0" in result.stdout


def test_needs_show_unknown_character(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _setup(tmp_path, monkeypatch)
    result = runner.invoke(app, ["needs", "show", "--character", "fantasma"])
    assert result.exit_code == 1
    out = (result.stdout or "") + (result.stderr or "")
    assert "non trovato" in out.lower()
