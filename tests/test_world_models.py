from pathlib import Path

from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import joinedload

from alembic import command
from simai.db.alembic_utils import get_alembic_config
from simai.db.session import get_engine, get_session_factory
from simai.world.enums import LocationKind
from simai.world.models import Character, Location
from simai.world.seed import seed_muse_core


def _engine(tmp_path: Path) -> Engine:
    url = f"sqlite:///{tmp_path / 'test.db'}"
    command.upgrade(get_alembic_config(url=url), "head")
    return get_engine(url)


def test_seed_creates_expected_counts(tmp_path: Path) -> None:
    engine = _engine(tmp_path)
    factory = get_session_factory(engine)
    with factory() as session:
        report = seed_muse_core(session)
        session.commit()
    assert report == {"locations_created": 3, "characters_created": 5}


def test_seed_is_idempotent(tmp_path: Path) -> None:
    engine = _engine(tmp_path)
    factory = get_session_factory(engine)
    with factory() as session:
        seed_muse_core(session)
        session.commit()
    with factory() as session:
        second = seed_muse_core(session)
        session.commit()
    assert second == {"locations_created": 0, "characters_created": 0}


def test_player_is_unique_and_at_home(tmp_path: Path) -> None:
    engine = _engine(tmp_path)
    factory = get_session_factory(engine)
    with factory() as session:
        seed_muse_core(session)
        session.commit()
    with factory() as session:
        players = (
            session.scalars(
                select(Character)
                .where(Character.is_player.is_(True))
                .options(joinedload(Character.location))
            )
            .unique()
            .all()
        )
        assert len(players) == 1
        assert players[0].location.key == "casa"


def test_all_kinds_are_represented(tmp_path: Path) -> None:
    engine = _engine(tmp_path)
    factory = get_session_factory(engine)
    with factory() as session:
        seed_muse_core(session)
        session.commit()
    with factory() as session:
        kinds = set(session.scalars(select(Location.kind)).all())
    assert kinds == {
        LocationKind.RESIDENTIAL,
        LocationKind.SOCIAL,
        LocationKind.LEISURE,
    }
