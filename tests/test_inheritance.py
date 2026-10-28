from pathlib import Path

import pytest
from alembic import command
from sqlalchemy import select
from sqlalchemy.engine import Engine

from simai.db.alembic_utils import get_alembic_config
from simai.db.session import get_engine, get_session_factory
from simai.npc.inheritance import distribute
from simai.relationships.enums import RelationshipKind
from simai.relationships.service import ensure_relationship
from simai.world.models import Character
from simai.world.seed import seed_muse_core


def _seeded(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Engine:
    url = f"sqlite:///{tmp_path / 'test.db'}"
    monkeypatch.setenv("SIMAI_DB_URL", url)
    command.upgrade(get_alembic_config(url=url), "head")
    engine = get_engine(url)
    factory = get_session_factory(engine)
    with factory() as session:
        seed_muse_core(session)
        session.commit()
    return engine


def _char(session, key: str) -> Character:
    c = session.scalar(select(Character).where(Character.key == key))
    assert c is not None
    return c


def test_inherit_to_parent(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Erika (no spouse, no figli) → giulia (madre) eredita tutto."""
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        erika = _char(session, "erika")
        giulia = _char(session, "giulia")
        erika.balance = 100.0
        giulia_before = giulia.balance
        session.commit()

        result = distribute(session, erika, tick_index=0)
        session.commit()

        assert result.tier == "parent"
        assert result.allocations == {"giulia": 100.0}
        assert result.to_world == 0.0
        assert giulia.balance == giulia_before + 100.0


def test_inherit_to_child(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Giulia (madre di erika) → erika eredita."""
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        giulia = _char(session, "giulia")
        erika = _char(session, "erika")
        giulia.balance = 200.0
        erika_before = erika.balance
        session.commit()

        result = distribute(session, giulia, tick_index=0)
        session.commit()

        assert result.tier == "child"
        assert result.allocations == {"erika": 200.0}
        assert erika.balance == erika_before + 200.0


def test_inherit_to_world_no_heir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Player (no famiglia, no spouse) → world."""
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        player = _char(session, "player")
        player.balance = 50.0
        session.commit()

        result = distribute(session, player, tick_index=0)
        session.commit()

        assert result.tier == "other"
        assert result.allocations == {}
        assert result.to_world == 50.0


def test_inherit_spouse_50_percent(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Giulia (spouse luca, 1 figlia erika): 50% luca, 50% erika.

    Giulia ha un solo figlio (erika). Luca padre di max è irrilevante:
    il deceased è giulia, i suoi figli sono solo quelli con
    `PARENT_OF` da giulia.
    """
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        luca = _char(session, "luca")
        giulia = _char(session, "giulia")
        ensure_relationship(
            session,
            giulia.id,
            luca.id,
            kind=RelationshipKind.SPOUSE_OF,
            strength=80.0,
        )
        giulia.balance = 100.0
        session.commit()

        result = distribute(session, giulia, tick_index=0)
        session.commit()

        assert result.tier == "spouse"
        assert result.allocations["luca"] == 50.0
        assert result.allocations["erika"] == 50.0
        assert result.to_world == 0.0


def test_inherit_zero_balance(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        erika = _char(session, "erika")
        erika.balance = 0.0
        session.commit()
        result = distribute(session, erika, tick_index=0)
        session.commit()
    assert result.tier == "none"
    assert result.total == 0.0
