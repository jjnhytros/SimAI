from pathlib import Path

import pytest
from alembic import command
from sqlalchemy import select
from sqlalchemy.engine import Engine

from simai.db.alembic_utils import get_alembic_config
from simai.db.session import get_engine, get_session_factory
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


def test_roundtrip_preserves_moodlets(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from simai.mood.enums import MoodletKind
    from simai.mood.models import Moodlet
    from simai.mood.moodlets import apply_moodlet

    engine = _seeded_engine(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        erika = session.scalar(select(Character).where(Character.key == "erika"))
        assert erika is not None
        apply_moodlet(session, erika.id, MoodletKind.ATE_WELL, tick=5)
        session.flush()
        create_save(session, name="mood")
        session.commit()

    with factory() as session:
        session.execute(Moodlet.__table__.delete())
        session.commit()

    with factory() as session:
        load_save(session, "mood")
        session.commit()

    with factory() as session:
        rows = session.scalars(select(Moodlet)).all()
        assert len(rows) == 1
        assert rows[0].kind == MoodletKind.ATE_WELL
        assert rows[0].expires_at_tick == 9


def test_roundtrip_preserves_economy(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from simai.economy.models import Job, Transaction

    engine = _seeded_engine(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        erika = session.scalar(select(Character).where(Character.key == "erika"))
        assert erika is not None
        erika.balance = 123.45
        session.commit()
        create_save(session, name="econ")

    with factory() as session:
        erika = session.scalar(select(Character).where(Character.key == "erika"))
        assert erika is not None
        erika.balance = 0.0
        session.execute(Transaction.__table__.delete())
        session.execute(Job.__table__.delete())
        session.commit()

    with factory() as session:
        load_save(session, "econ")
        session.commit()

    with factory() as session:
        erika = session.scalar(select(Character).where(Character.key == "erika"))
        assert erika is not None
        assert erika.balance == 123.45
        jobs = session.scalars(select(Job)).all()
        assert len(jobs) == 5


def test_roundtrip_preserves_traits(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded_engine(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        erika = session.scalar(select(Character).where(Character.key == "erika"))
        assert erika is not None
        assert erika.traits == ["solitary"]
        create_save(session, name="tr")

    with factory() as session:
        erika = session.scalar(select(Character).where(Character.key == "erika"))
        assert erika is not None
        erika.traits = []
        session.commit()

    with factory() as session:
        load_save(session, "tr")
        session.commit()

    with factory() as session:
        erika = session.scalar(select(Character).where(Character.key == "erika"))
        assert erika is not None
        assert erika.traits == ["solitary"]


def test_roundtrip_preserves_moodlet_need(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from simai.mood.enums import MoodletKind
    from simai.mood.models import Moodlet
    from simai.mood.moodlets import refresh_need_moodlets_many
    from simai.needs.enums import NeedKind

    engine = _seeded_engine(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        erika = session.scalar(select(Character).where(Character.key == "erika"))
        assert erika is not None
        refresh_need_moodlets_many(session, {erika.id: {NeedKind.HUNGER: 5.0}}, tick=5)
        session.flush()
        create_save(session, name="need")
        session.commit()

    with factory() as session:
        session.execute(Moodlet.__table__.delete())
        session.commit()

    with factory() as session:
        load_save(session, "need")
        session.commit()

    with factory() as session:
        rows = session.scalars(select(Moodlet)).all()
        assert len(rows) == 1
        assert rows[0].kind == MoodletKind.STARVING
        assert rows[0].need == NeedKind.HUNGER
