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


def test_player_status_shows_mood(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _setup(tmp_path, monkeypatch)
    result = runner.invoke(app, ["player", "status"])
    assert result.exit_code == 0
    assert "Umore: 100.0 (sereno)" in result.stdout


def test_mood_drops_after_tick(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _setup(tmp_path, monkeypatch)
    runner.invoke(app, ["sim", "tick", "-m", "600"])
    result = runner.invoke(app, ["player", "status"])
    # 600 min -> HUNGER -60, THIRST -80, FUN -40, INTIMACY -20
    # mood = 0.25*40 + 0.20*20 + 0.30*60 + 0.25*80 = 10+4+18+20 = 52
    assert "Umore: 52.0" in result.stdout


def test_needs_show_includes_mood(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _setup(tmp_path, monkeypatch)
    result = runner.invoke(app, ["needs", "show", "-c", "erika"])
    assert result.exit_code == 0
    assert "Umore: 100.0" in result.stdout
