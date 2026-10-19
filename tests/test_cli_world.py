from pathlib import Path

import pytest
from alembic import command
from typer.testing import CliRunner

from simai.cli.app import app
from simai.db.alembic_utils import get_alembic_config

runner = CliRunner()


def _setup(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> str:
    url = f"sqlite:///{tmp_path / 'cli.db'}"
    monkeypatch.setenv("SIMAI_DB_URL", url)
    command.upgrade(get_alembic_config(url=url), "head")
    return url


def test_world_seed_creates_data(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _setup(tmp_path, monkeypatch)
    result = runner.invoke(app, ["world", "seed"])
    assert result.exit_code == 0, result.stdout
    assert "3 location" in result.stdout
    assert "5 personaggi" in result.stdout


def test_world_seed_is_idempotent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _setup(tmp_path, monkeypatch)
    first = runner.invoke(app, ["world", "seed"])
    second = runner.invoke(app, ["world", "seed"])
    assert first.exit_code == 0
    assert second.exit_code == 0
    assert "0 location" in second.stdout
    assert "0 personaggi" in second.stdout


def test_world_list_after_seed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _setup(tmp_path, monkeypatch)
    runner.invoke(app, ["world", "seed"])
    result = runner.invoke(app, ["world", "list"])
    assert result.exit_code == 0
    assert "Piazza delle Muse" in result.stdout
    assert "Erika Lamborghetti" in result.stdout
    assert "★ [player]" in result.stdout