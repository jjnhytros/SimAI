from pathlib import Path

from alembic.config import Config

from simai import migrations as _migrations_pkg
from simai.config.settings import Settings
from simai.db.session import ensure_sqlite_parent_dir

MIGRATIONS_DIR: Path = Path(_migrations_pkg.__file__).parent


def get_alembic_config(url: str | None = None) -> Config:
    """Configurazione Alembic risolta rispetto al package installato.

    `script_location` è sempre il path assoluto di `simai.migrations`:
    qualunque valore nell'ini viene ignorato. Questo rende il comando
    indipendente dal CWD e dalla presenza di `pyproject.toml`.
    """
    ini_path = MIGRATIONS_DIR / "alembic.ini"
    cfg = Config(str(ini_path) if ini_path.exists() else None)

    # Sempre assoluto: l'ini non può decidere dove sono le migrazioni.
    cfg.set_main_option("script_location", str(MIGRATIONS_DIR))

    if not cfg.get_main_option("file_template"):
        cfg.set_main_option("file_template", "%(rev)s_%(slug)s")
    if not cfg.get_main_option("path_separator"):
        cfg.set_main_option("path_separator", "os")

    resolved = url or Settings().db_url
    ensure_sqlite_parent_dir(resolved)
    cfg.set_main_option("sqlalchemy.url", resolved)
    return cfg
