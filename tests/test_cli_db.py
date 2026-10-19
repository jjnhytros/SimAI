from pathlib import Path

import pytest
from sqlalchemy import create_engine, text
from typer.testing import CliRunner

from simai.cli.app import app

runner = CliRunner()


def test_db_upgrade(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    url = f"sqlite:///{tmp_path / 'cli.db'}"
    monkeypatch.setenv("SIMAI_DB_URL", url)

    result = runner.invoke(app, ["db", "upgrade"])
    assert result.exit_code == 0, result.stdout

    engine = create_engine(url)
    with engine.connect() as conn:
        row = conn.execute(text("SELECT schema_version FROM core_version WHERE id=1")).fetchone()
    assert row is not None


def test_db_status_uninitialized(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    url = f"sqlite:///{tmp_path / 'empty.db'}"
    monkeypatch.setenv("SIMAI_DB_URL", url)

    result = runner.invoke(app, ["db", "status"])
    assert result.exit_code == 1


def test_db_status_after_upgrade(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    url = f"sqlite:///{tmp_path / 'cli.db'}"
    monkeypatch.setenv("SIMAI_DB_URL", url)

    assert runner.invoke(app, ["db", "upgrade"]).exit_code == 0
    result = runner.invoke(app, ["db", "status"])
    assert result.exit_code == 0
    assert "Revisione corrente:" in result.stdout
    assert "non inizializzato" not in result.stdout


def test_db_status_missing_parent_dir_does_not_crash(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    url = f"sqlite:///{tmp_path / 'deep' / 'nested' / 'empty.db'}"
    monkeypatch.setenv("SIMAI_DB_URL", url)

    result = runner.invoke(app, ["db", "status"])
    assert result.exit_code == 1
    assert "DB non inizializzato" in result.stdout
