from pathlib import Path

import pytest
from alembic import command
from sqlalchemy import select
from sqlalchemy.engine import Engine

from simai.actions.enums import ActionKind
from simai.db.alembic_utils import get_alembic_config
from simai.db.session import get_engine, get_session_factory
from simai.needs.enums import NeedKind
from simai.npc.traits import (
    Trait,
    trait_decay_multiplier,
    trait_move_penalty,
    trait_utility_bonus,
)
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


def test_trait_enum_values() -> None:
    assert {t.value for t in Trait} == {
        "lazy",
        "energetic",
        "social",
        "solitary",
        "glutton",
    }


def test_decay_multiplier_no_traits() -> None:
    assert trait_decay_multiplier([], NeedKind.FUN) == 1.0
    assert trait_decay_multiplier([], NeedKind.HUNGER) == 1.0


def test_decay_multiplier_lazy_fun() -> None:
    assert trait_decay_multiplier(["lazy"], NeedKind.FUN) == pytest.approx(1.30)


def test_decay_multiplier_solitary_intimacy() -> None:
    assert trait_decay_multiplier(["solitary"], NeedKind.INTIMACY) == pytest.approx(0.60)


def test_decay_multiplier_combined() -> None:
    # lazy+glutton non toccano lo stesso bisogno: fattori separati
    assert trait_decay_multiplier(["lazy", "glutton"], NeedKind.HUNGER) == pytest.approx(1.30)
    assert trait_decay_multiplier(["lazy", "glutton"], NeedKind.FUN) == pytest.approx(1.30)


def test_decay_multiplier_unknown_trait_ignored() -> None:
    assert trait_decay_multiplier(["nonesiste"], NeedKind.FUN) == 1.0


def test_utility_bonus_glutton_eat() -> None:
    assert trait_utility_bonus(["glutton"], ActionKind.EAT) == pytest.approx(0.15)


def test_utility_bonus_social_socialize() -> None:
    assert trait_utility_bonus(["social"], ActionKind.SOCIALIZE) == pytest.approx(0.15)


def test_utility_bonus_no_match() -> None:
    assert trait_utility_bonus(["glutton"], ActionKind.PLAY) == 0.0


def test_move_penalty_solitary() -> None:
    assert trait_move_penalty(["solitary"]) == pytest.approx(-0.10)
    assert trait_move_penalty([]) == 0.0
    assert trait_move_penalty(["lazy"]) == 0.0


def test_seed_assigns_traits(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        chars = {c.key: c.traits for c in session.scalars(select(Character)).all()}
    assert chars["player"] == []
    assert chars["erika"] == ["solitary"]
    assert chars["max"] == ["energetic"]
    assert chars["luca"] == ["social"]
    assert set(chars["giulia"]) == {"lazy", "glutton"}


def test_seed_traits_idempotent(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        seed_muse_core(session)
        session.commit()
    with factory() as session:
        erika = session.scalar(select(Character).where(Character.key == "erika"))
        assert erika is not None
        assert erika.traits == ["solitary"]
