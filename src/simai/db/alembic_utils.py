from pathlib import Path

from alembic.config import Config

from simai.config.settings import Settings
from simai.db.session import ensure_sqlite_parent_dir


def _find_project_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    return current.parents[-1]


PROJECT_ROOT = _find_project_root()


def get_alembic_config(url: str | None = None) -> Config:
    """Configurazione Alembic risolta rispetto alla root del progetto."""
    cfg = Config(str(PROJECT_ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(PROJECT_ROOT / "alembic"))
    resolved = url or Settings().db_url
    ensure_sqlite_parent_dir(resolved)
    cfg.set_main_option("sqlalchemy.url", resolved)
    return cfg
