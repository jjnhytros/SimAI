from pathlib import Path

import pytest
from typer.testing import CliRunner

from alembic import command
from simai.cli.app import app
from simai.db.alembic_utils import get_alembic_config

runner = CliRunner()


def test_actions_choose_on_empty_db_gives_message(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    url = f"sqlite:///{tmp_path / 'empty.db'}"
    monkeypatch.setenv("SIMAI_DB_URL", url)
    # DB creato ma non migrato: nemmeno alembic_version esiste.
    result = runner.invoke(app, ["actions", "choose", "-c", "erika"])
    assert result.exit_code == 1
    combined = (result.stdout or "") + (result.stderr or "")
    assert "Database non inizializzato" in combined
    assert "simai db upgrade" in combined
    assert "Traceback" not in combined


def test_actions_choose_on_old_schema_gives_message(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    url = f"sqlite:///{tmp_path / 'old.db'}"
    monkeypatch.setenv("SIMAI_DB_URL", url)
    # Migriamo solo fino a 0001: lo schema è "vecchio".
    cfg = get_alembic_config(url=url)
    command.upgrade(cfg, "0001")

    result = runner.invoke(app, ["actions", "choose", "-c", "erika"])
    assert result.exit_code == 1
    combined = (result.stdout or "") + (result.stderr or "")
    assert "Schema DB non aggiornato" in combined
    assert "0001" in combined


def test_needs_show_on_empty_db_gives_message(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    url = f"sqlite:///{tmp_path / 'empty.db'}"
    monkeypatch.setenv("SIMAI_DB_URL", url)
    result = runner.invoke(app, ["needs", "show", "-c", "erika"])
    assert result.exit_code == 1
    combined = (result.stdout or "") + (result.stderr or "")
    assert "Database non inizializzato" in combined
    assert "Traceback" not in combined
