from typer.testing import CliRunner

from simai.cli.app import app
from simai.i18n.checker import check

runner = CliRunner()


def test_i18n_checker_reports_no_problems() -> None:
    assert check() == []


def test_i18n_check_cli() -> None:
    result = runner.invoke(app, ["i18n", "check"])
    assert result.exit_code == 0, result.stdout
    assert "i18n OK" in result.stdout
