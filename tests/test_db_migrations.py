from pathlib import Path

from alembic import command
from sqlalchemy import create_engine, text

import simai.migrations
from simai.db.alembic_utils import get_alembic_config


def _url(tmp_path: Path) -> str:
    return f"sqlite:///{tmp_path / 'test.db'}"


def test_upgrade_creates_core_version(tmp_path: Path) -> None:
    url = _url(tmp_path)
    command.upgrade(get_alembic_config(url=url), "head")

    engine = create_engine(url)
    with engine.connect() as conn:
        row = conn.execute(text("SELECT schema_version FROM core_version WHERE id=1")).fetchone()
    assert row is not None
    assert row[0] == "0.1.0"


def test_upgrade_is_idempotent(tmp_path: Path) -> None:
    url = _url(tmp_path)
    cfg = get_alembic_config(url=url)
    command.upgrade(cfg, "head")
    command.upgrade(cfg, "head")

    engine = create_engine(url)
    with engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM core_version")).scalar()
    assert count == 1


def test_downgrade_drops_table(tmp_path: Path) -> None:
    url = _url(tmp_path)
    cfg = get_alembic_config(url=url)
    command.upgrade(cfg, "head")
    command.downgrade(cfg, "base")

    engine = create_engine(url)
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name='core_version'")
        ).fetchone()
    assert row is None


def test_upgrade_creates_missing_parent_dir(tmp_path: Path) -> None:
    nested = tmp_path / "does" / "not" / "exist"
    url = f"sqlite:///{nested / 'test.db'}"
    assert not nested.exists()

    command.upgrade(get_alembic_config(url=url), "head")

    assert (nested / "test.db").exists()


def test_migrations_packaged_inside_simai() -> None:
    """Regressione: le migrazioni devono stare nel package, non alla root.

    Se qualcuno le rimuove dal package, questo test fallisce prima che
    un wheel rotto venga pubblicato.
    """
    from pathlib import Path

    mig_dir = Path(simai.migrations.__file__).parent
    assert (mig_dir / "env.py").is_file()
    assert (mig_dir / "script.py.mako").is_file()
    assert (mig_dir / "versions").is_dir()
    versions = list((mig_dir / "versions").glob("*.py"))
    # 0001..0014 + 5200_04 + 0015 + 5200_08 = 17
    assert len(versions) >= 17
