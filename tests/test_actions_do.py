from pathlib import Path

import pytest
from alembic import command
from sqlalchemy import select
from sqlalchemy.engine import Engine

from simai.actions.do import do_action
from simai.actions.enums import ActionKind
from simai.db.alembic_utils import get_alembic_config
from simai.db.session import get_engine, get_session_factory
from simai.needs.enums import NeedKind
from simai.world.models import Character
from simai.world.move import move_character
from simai.world.seed import seed_muse_core


def _seeded(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Engine:
    url = f"sqlite:///{tmp_path / 'test.db'}"
    monkeypatch.setenv("SIMAI_DB_URL", url)
    monkeypatch.setenv("SIMAI_SAVES_DIR", str(tmp_path / "saves"))
    command.upgrade(get_alembic_config(url=url), "head")
    engine = get_engine(url)
    factory = get_session_factory(engine)
    with factory() as session:
        seed_muse_core(session)
        session.commit()
    return engine


def test_do_action_valid_in_leisure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        move_character(session, "player", "caffe")
        session.flush()
        # Abbasso thirst del player: DRINK richiede thirst < 40.
        from simai.needs.models import Need

        thirst = session.scalar(
            select(Need).where(
                Need.character_id == 1,  # player
                Need.kind == NeedKind.THIRST,
            )
        )
        assert thirst is not None
        thirst.value = 20.0
        session.flush()
        result = do_action(session, "player", ActionKind.DRINK)
        session.commit()
    assert result.success
    assert result.location_key == "caffe"
    assert result.need_kind == NeedKind.THIRST
    assert result.need_after == 50.0  # 20 + 30


def test_do_action_invalid_in_location(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        # player è a casa: DRINK non è disponibile.
        result = do_action(session, "player", ActionKind.DRINK)
    assert not result.success
    assert result.error is not None
    assert "non disponibile" in result.error
    assert "'casa'" in result.error
    assert "eat, play" in result.error


def test_do_action_unknown_character(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        result = do_action(session, "fantasma", ActionKind.EAT)
    assert not result.success
    assert "non trovato" in (result.error or "")


def test_do_action_socialize_boosts_relationship(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        move_character(session, "player", "piazza")
        session.flush()
        # Abbasso intimacy di max: SOCIALIZE richiede intimacy < 70.
        from simai.needs.models import Need

        max_char = session.scalar(select(Character).where(Character.key == "max"))
        assert max_char is not None
        intimacy = session.scalar(
            select(Need).where(
                Need.character_id == max_char.id,
                Need.kind == NeedKind.INTIMACY,
            )
        )
        assert intimacy is not None
        intimacy.value = 50.0
        session.flush()
        result = do_action(session, "max", ActionKind.SOCIALIZE)
        session.commit()
    assert result.success
    # Max ed Erika non sono nella stessa location, nessun boost relazionale.
    assert result.relationship_strength_after is None
