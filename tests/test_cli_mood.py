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


def test_player_status_shows_mood(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _setup(tmp_path, monkeypatch)
    result = runner.invoke(app, ["player", "status"])
    assert result.exit_code == 0
    assert "Umore: 100.0 (sereno)" in result.stdout


def test_mood_drops_after_tick(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _setup(tmp_path, monkeypatch)
    runner.invoke(app, ["sim", "tick", "-m", "600"])
    result = runner.invoke(app, ["player", "status"])
    # 600 min = 10h -> HUNGER -40, THIRST -50, FUN -30, INTIMACY -15
    # Base pesata: 60, 50, 70, 85 → 67.25
    # Moodlet 0.1101 (B3, Δ positivi +0.5):
    #   HUNGER=60   → SATISFIED   +0.5
    #   THIRST=50   → HYDRATED    +0.5
    #   FUN=70      → ENTERTAINED +0.5 (70 non è < 70)
    #   INTIMACY=85 → CLOSE       +0.5
    # Delta moodlet = +2.0 → mood = 67.25 + 2.0 = 69.25 → "69.2"
    assert "Umore: 69.2" in result.stdout


def test_needs_show_includes_mood(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _setup(tmp_path, monkeypatch)
    result = runner.invoke(app, ["needs", "show", "-c", "erika"])
    assert result.exit_code == 0
    assert "Umore: 100.0" in result.stdout
