from pathlib import Path

from alembic import command
from sqlalchemy import select
from sqlalchemy.engine import Engine

from simai.actions.catalog import ActionDef
from simai.actions.enums import ActionKind
from simai.db.alembic_utils import get_alembic_config
from simai.db.session import get_engine, get_session_factory
from simai.needs.enums import NeedKind
from simai.relationships.models import Relationship
from simai.relationships.service import (
    SOCIALIZE_BOOST,
    boost_social_relationship,
    relationships_of,
)
from simai.sim.tick import run_tick
from simai.world.models import Character, Location
from simai.world.seed import seed_muse_core


def _seeded(tmp_path: Path) -> Engine:
    url = f"sqlite:///{tmp_path / 'test.db'}"
    command.upgrade(get_alembic_config(url=url), "head")
    engine = get_engine(url)
    factory = get_session_factory(engine)
    with factory() as session:
        seed_muse_core(session)
        session.commit()
    return engine


def test_seed_creates_symmetric_friendship(tmp_path: Path) -> None:
    engine = _seeded(tmp_path)
    factory = get_session_factory(engine)
    with factory() as session:
        erika = session.scalar(select(Character).where(Character.key == "erika"))
        max_c = session.scalar(select(Character).where(Character.key == "max"))
        assert erika is not None and max_c is not None
        assert len(relationships_of(session, erika.id)) == 1
        assert len(relationships_of(session, max_c.id)) == 1
        rel_em = session.scalar(
            select(Relationship).where(
                Relationship.from_character_id == erika.id,
                Relationship.to_character_id == max_c.id,
            )
        )
        rel_me = session.scalar(
            select(Relationship).where(
                Relationship.from_character_id == max_c.id,
                Relationship.to_character_id == erika.id,
            )
        )
        assert rel_em is not None and rel_me is not None
        assert rel_em.strength == 60.0
        assert rel_me.strength == 60.0


def test_boost_returns_none_for_non_socialize(tmp_path: Path) -> None:
    engine = _seeded(tmp_path)
    factory = get_session_factory(engine)
    eat = ActionDef(
        kind=ActionKind.EAT,
        satisfies=NeedKind.HUNGER,
        amount=40.0,
        allowed_at=frozenset(),
        max_need_to_start=30.0,
    )
    with factory() as session:
        erika = session.scalar(select(Character).where(Character.key == "erika"))
        assert erika is not None
        assert boost_social_relationship(session, erika.id, eat) is None


def test_boost_returns_none_when_no_friend_in_location(
    tmp_path: Path,
) -> None:
    engine = _seeded(tmp_path)
    factory = get_session_factory(engine)
    socialize = ActionDef(
        kind=ActionKind.SOCIALIZE,
        satisfies=NeedKind.INTIMACY,
        amount=25.0,
        allowed_at=frozenset(),
        max_need_to_start=70.0,
    )
    with factory() as session:
        erika = session.scalar(select(Character).where(Character.key == "erika"))
        assert erika is not None
        # Max è a piazza, Erika a casa: nessun FRIEND locale.
        assert boost_social_relationship(session, erika.id, socialize) is None


def test_boost_increases_both_directions(tmp_path: Path) -> None:
    engine = _seeded(tmp_path)
    factory = get_session_factory(engine)
    socialize = ActionDef(
        kind=ActionKind.SOCIALIZE,
        satisfies=NeedKind.INTIMACY,
        amount=25.0,
        allowed_at=frozenset(),
        max_need_to_start=70.0,
    )
    with factory() as session:
        erika = session.scalar(select(Character).where(Character.key == "erika"))
        max_c = session.scalar(select(Character).where(Character.key == "max"))
        piazza = session.scalar(select(Location).where(Location.key == "piazza"))
        assert erika is not None and max_c is not None
        assert piazza is not None
        erika.location_id = piazza.id
        session.flush()

        new_strength = boost_social_relationship(session, max_c.id, socialize)
        session.commit()

    assert new_strength == 60.0 + SOCIALIZE_BOOST

    with factory() as session:
        erika = session.scalar(select(Character).where(Character.key == "erika"))
        max_c = session.scalar(select(Character).where(Character.key == "max"))
        assert erika is not None and max_c is not None
        rel_me = session.scalar(
            select(Relationship).where(
                Relationship.from_character_id == max_c.id,
                Relationship.to_character_id == erika.id,
            )
        )
        rel_em = session.scalar(
            select(Relationship).where(
                Relationship.from_character_id == erika.id,
                Relationship.to_character_id == max_c.id,
            )
        )
        assert rel_me is not None and rel_em is not None
        assert rel_me.strength == 60.0 + SOCIALIZE_BOOST
        assert rel_em.strength == 60.0 + SOCIALIZE_BOOST


def test_tick_socialize_boosts_relationship(tmp_path: Path) -> None:
    engine = _seeded(tmp_path)
    factory = get_session_factory(engine)
    with factory() as session:
        erika = session.scalar(select(Character).where(Character.key == "erika"))
        max_c = session.scalar(select(Character).where(Character.key == "max"))
        piazza = session.scalar(select(Location).where(Location.key == "piazza"))
        assert erika is not None and max_c is not None
        assert piazza is not None
        erika.location_id = piazza.id
        # Forza SOCIALIZE: intimacy al minimo, fun pieno.
        from simai.needs.models import Need

        intimacy = session.scalar(
            select(Need).where(
                Need.character_id == max_c.id,
                Need.kind == NeedKind.INTIMACY,
            )
        )
        fun = session.scalar(
            select(Need).where(
                Need.character_id == max_c.id,
                Need.kind == NeedKind.FUN,
            )
        )
        assert intimacy is not None and fun is not None
        intimacy.value = 5.0
        fun.value = 100.0
        session.commit()

    with factory() as session:
        report = run_tick(session, minutes=1, tick_index=0, master_seed=42)
        session.commit()

    max_decision = next(
        (d for d in report.decisions if d.character_key == "max"),
        None,
    )
    assert max_decision is not None
    assert max_decision.action == ActionKind.SOCIALIZE
    assert max_decision.relationship_strength_after == (60.0 + SOCIALIZE_BOOST)
