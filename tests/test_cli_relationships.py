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
    command.upgrade(get_alembic_config(url=url), "head")
    runner.invoke(app, ["world", "seed"])


def test_relationships_show(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _setup(tmp_path, monkeypatch)
    result = runner.invoke(app, ["relationships", "show", "-c", "erika"])
    assert result.exit_code == 0, result.stdout
    assert "Relazioni di 'erika' (2)" in result.stdout
    assert "FRIEND" in result.stdout
    assert "CHILD_OF" in result.stdout
    assert "[max]" in result.stdout
    assert "FRIEND" in result.stdout
    assert "60.0" in result.stdout


def test_relationships_show_empty(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _setup(tmp_path, monkeypatch)
    # player non ha relazioni (gli altri hanno famiglia o FRIEND).
    result = runner.invoke(app, ["relationships", "show", "-c", "player"])
    assert result.exit_code == 0
    assert "(0)" in result.stdout


def test_relationships_show_unknown_character(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _setup(tmp_path, monkeypatch)
    result = runner.invoke(app, ["relationships", "show", "-c", "fantasma"])
    assert result.exit_code == 1
    combined = (result.stdout or "") + (result.stderr or "")
    assert "non trovato" in combined.lower()
