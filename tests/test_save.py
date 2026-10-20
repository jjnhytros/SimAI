from pathlib import Path

import pytest
from sqlalchemy import select
from sqlalchemy.engine import Engine

from alembic import command
from simai.db.alembic_utils import get_alembic_config
from simai.db.session import get_engine, get_session_factory
from simai.needs.models import Need
from simai.needs.service import needs_of
from simai.save.errors import (
    SaveError,
    SaveFormatError,
    SaveNotFoundError,
    SaveVersionError,
)
from simai.save.format import MAGIC, decode
from simai.save.service import (
    create_save,
    delete_save,
    list_saves,
    load_save,
)
from simai.sim.state import get_state
from simai.sim.tick import run_tick
from simai.world.models import Character
from simai.world.seed import seed_muse_core


def _seeded_engine(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Engine:
    url = f"sqlite:///{tmp_path / 'test.db'}"
    saves_dir = tmp_path / "saves"
    monkeypatch.setenv("SIMAI_DB_URL", url)
    monkeypatch.setenv("SIMAI_SAVES_DIR", str(saves_dir))
    command.upgrade(get_alembic_config(url=url), "head")
    engine = get_engine(url)
    factory = get_session_factory(engine)
    with factory() as session:
        seed_muse_core(session)
        session.commit()
    return engine


def test_create_save_writes_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded_engine(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        info = create_save(session, name="first")
    assert info.path.exists()
    assert info.path.read_bytes().startswith(MAGIC)
    assert info.header.version == 1


def test_create_then_load_roundtrips_state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded_engine(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        run_tick(session, minutes=60, tick_index=None, master_seed=None)
        session.commit()
        create_save(session, name="before")

    with factory() as session:
        erika = session.scalar(select(Character).where(Character.key == "erika"))
        assert erika is not None
        needs_before = needs_of(session, erika.id)

    # Modifica DB
    with factory() as session:
        run_tick(session, minutes=60, tick_index=None, master_seed=None)
        run_tick(session, minutes=60, tick_index=None, master_seed=None)
        session.commit()
        state = get_state(session)
        assert state.tick_index == 3

    # Load
    with factory() as session:
        header = load_save(session, "before")
        session.commit()
        assert header.tick_index == 1

    with factory() as session:
        erika = session.scalar(select(Character).where(Character.key == "erika"))
        assert erika is not None
        assert needs_of(session, erika.id) == needs_before
        assert get_state(session).tick_index == 1


def test_load_unknown_raises(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded_engine(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session, pytest.raises(SaveNotFoundError):
        load_save(session, "nope")


def test_corrupted_checksum_raises(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded_engine(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        info = create_save(session, name="broken")
    data = bytearray(info.path.read_bytes())
    # Altero un byte del payload: il checksum non torna più.
    data[-1] ^= 0xFF
    info.path.write_bytes(bytes(data))

    with factory() as session, pytest.raises(SaveFormatError):
        load_save(session, "broken")


def test_future_version_raises(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded_engine(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        info = create_save(session, name="future")
    data = bytearray(info.path.read_bytes())
    # Magic (6) + version (2) -> cambio il byte di versione.
    data[6] = 0
    data[7] = 99
    info.path.write_bytes(bytes(data))

    with pytest.raises(SaveVersionError):
        decode(bytes(data))


def test_list_saves_returns_created(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded_engine(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        create_save(session, name="a")
        create_save(session, name="b")
    names = {s.name for s in list_saves()}
    assert names == {"a", "b"}


def test_delete_save_removes_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded_engine(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        info = create_save(session, name="gone")
    delete_save("gone")
    assert not info.path.exists()


def test_invalid_name_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded_engine(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session, pytest.raises(SaveError):
        create_save(session, name="../etc/passwd")


def test_roundtrip_preserves_cooldown(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    engine = _seeded_engine(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        erika = session.scalar(
            select(Character).where(Character.key == "erika")
        )
        assert erika is not None
        needs = session.scalars(
            select(Need).where(Need.character_id == erika.id)
        ).all()
        for n in needs:
            n.last_satisfied_at_tick = 42
        session.commit()
        create_save(session, name="cd")

    with factory() as session:
        needs = session.scalars(
            select(Need).where(Need.character_id == erika.id)
        ).all()
        for n in needs:
            n.last_satisfied_at_tick = 999
        session.commit()

    with factory() as session:
        load_save(session, "cd")
        session.commit()

    with factory() as session:
        needs = session.scalars(
            select(Need).where(Need.character_id == erika.id)
        ).all()
        assert all(n.last_satisfied_at_tick == 42 for n in needs)
