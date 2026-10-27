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


def test_economy_balance_single(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _setup(tmp_path, monkeypatch)
    result = runner.invoke(app, ["economy", "balance", "-c", "luca"])
    assert result.exit_code == 0, result.stdout
    assert "luca" in result.stdout
    assert "100.00" in result.stdout
    assert "barista" in result.stdout


def test_economy_balance_all(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _setup(tmp_path, monkeypatch)
    result = runner.invoke(app, ["economy", "balance", "--all"])
    assert result.exit_code == 0
    for key in ("player", "erika", "max", "luca", "giulia"):
        assert key in result.stdout


def test_economy_balance_requires_argument(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _setup(tmp_path, monkeypatch)
    result = runner.invoke(app, ["economy", "balance"])
    assert result.exit_code == 1
    combined = (result.stdout or "") + (result.stderr or "")
    assert "--character" in combined


def test_economy_jobs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _setup(tmp_path, monkeypatch)
    result = runner.invoke(app, ["economy", "jobs"])
    assert result.exit_code == 0
    assert "Lavori (5)" in result.stdout
    assert "barista" in result.stdout
    assert "insegnante" in result.stdout
    assert "studente" in result.stdout


def test_economy_ledger_empty(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _setup(tmp_path, monkeypatch)
    result = runner.invoke(app, ["economy", "ledger"])
    assert result.exit_code == 0
    assert "Transazioni" in result.stdout


def test_economy_ledger_after_payday(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _setup(tmp_path, monkeypatch)
    # 28 tick: payday al tick 27
    runner.invoke(app, ["sim", "run", "--ticks", "28"])
    result = runner.invoke(app, ["economy", "ledger", "-c", "luca"])
    assert result.exit_code == 0
    assert "salary" in result.stdout.lower()
    assert "25.00" in result.stdout


def test_economy_ledger_rejects_zero_limit(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _setup(tmp_path, monkeypatch)
    result = runner.invoke(app, ["economy", "ledger", "-n", "0"])
    assert result.exit_code == 1
