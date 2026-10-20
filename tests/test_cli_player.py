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


def test_player_status(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _setup(tmp_path, monkeypatch)
    result = runner.invoke(app, ["player", "status"])
    assert result.exit_code == 0, result.stdout
    assert "Tick: 0" in result.stdout
    assert "Player: Giocatore" in result.stdout
    assert "[casa]" in result.stdout
    assert "hunger: 100.0" in result.stdout
    assert "erika" in result.stdout


def test_player_do_valid(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _setup(tmp_path, monkeypatch)
    # Al primo avvio, hunger=100 -> EAT rifiutata. Verifichiamo quello.
    rejected = runner.invoke(app, ["player", "do", "-a", "eat"])
    assert rejected.exit_code == 1
    combined = (rejected.stdout or "") + (rejected.stderr or "")
    assert "non necessaria" in combined

    # Poi avanziamo di molti tick: hunger scende sotto 30, EAT ok.
    runner.invoke(app, ["sim", "tick", "-m", "900"])  # 15h
    accepted = runner.invoke(app, ["player", "do", "-a", "eat"])
    assert accepted.exit_code == 0, accepted.stdout
    assert "player esegue eat" in accepted.stdout


def test_player_do_invalid(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _setup(tmp_path, monkeypatch)
    result = runner.invoke(app, ["player", "do", "-a", "drink"])
    assert result.exit_code == 1
    combined = (result.stdout or "") + (result.stderr or "")
    assert "non disponibile" in combined


def test_player_move(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _setup(tmp_path, monkeypatch)
    result = runner.invoke(app, ["player", "move", "-l", "piazza"])
    assert result.exit_code == 0
    assert "player: casa → piazza" in result.stdout

    status = runner.invoke(app, ["player", "status"])
    assert "[piazza]" in status.stdout


def test_player_move_unknown_location(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _setup(tmp_path, monkeypatch)
    result = runner.invoke(app, ["player", "move", "-l", "luna"])
    assert result.exit_code == 1
    combined = (result.stdout or "") + (result.stderr or "")
    assert "non trovata" in combined


def test_player_status_on_empty_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    url = f"sqlite:///{tmp_path / 'empty.db'}"
    monkeypatch.setenv("SIMAI_DB_URL", url)
    result = runner.invoke(app, ["player", "status"])
    assert result.exit_code == 1
    combined = (result.stdout or "") + (result.stderr or "")
    assert "Database non inizializzato" in combined
