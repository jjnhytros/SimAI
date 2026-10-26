from pathlib import Path

import pytest
from alembic import command
from sqlalchemy import select
from sqlalchemy.engine import Engine

from simai.actions.reachability import available_moves
from simai.db.alembic_utils import get_alembic_config
from simai.db.session import get_engine, get_session_factory
from simai.needs.enums import NeedKind
from simai.world.models import Location
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


def _needs(
    hunger: float = 100.0,
    thirst: float = 100.0,
    fun: float = 100.0,
    intimacy: float = 100.0,
) -> dict[NeedKind, float]:
    return {
        NeedKind.HUNGER: hunger,
        NeedKind.THIRST: thirst,
        NeedKind.FUN: fun,
        NeedKind.INTIMACY: intimacy,
    }


def test_all_needs_high_no_moves(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        casa = session.scalar(select(Location).where(Location.key == "casa"))
        assert casa is not None
        moves = available_moves(
            session,
            current_location_id=casa.id,
            needs=_needs(),
        )
    assert moves == []


def test_thirsty_from_casa_reaches_drink_locations(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        casa = session.scalar(select(Location).where(Location.key == "casa"))
        assert casa is not None
        moves = available_moves(
            session,
            current_location_id=casa.id,
            needs=_needs(thirst=20.0),
        )
    # Caffè (DRINK 2 Athel) e piazza (fontanella gratis)
    targets = {(m.target_location_key, m.action_kind.value) for m in moves}
    assert ("caffe", "drink") in targets
    assert ("piazza", "drink") in targets
    assert len(moves) == 2
    assert all(m.satisfies == NeedKind.THIRST for m in moves)
    assert all(m.need_value == 20.0 for m in moves)


def test_hungry_from_caffe_can_reach_casa(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        caffe = session.scalar(select(Location).where(Location.key == "caffe"))
        assert caffe is not None
        moves = available_moves(
            session,
            current_location_id=caffe.id,
            needs=_needs(hunger=10.0),
        )
    # Caffe ha già EAT: ma hunger è basso e EAT è locale. Il move
    # scatta solo se l'azione non è locale. Qui non dovrebbe esserci.
    # In realtà la logica restituisce tutte le location non correnti
    # che contengono un'azione che soddisferebbe un bisogno sotto soglia.
    # A caffè c'è già EAT, ma la funzione non controlla cosa è locale:
    # filtra solo per location diverse e bisogno sotto soglia.
    # Casa ha EAT -> match.
    target_keys = {m.target_location_key for m in moves}
    assert "casa" in target_keys


def test_multiple_moves_from_casa(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        casa = session.scalar(select(Location).where(Location.key == "casa"))
        assert casa is not None
        moves = available_moves(
            session,
            current_location_id=casa.id,
            needs=_needs(thirst=10.0, intimacy=10.0),
        )
    targets = {(m.target_location_key, m.satisfies.value) for m in moves}
    # caffè per thirst, piazza/caffè per intimacy
    assert ("caffe", "thirst") in targets
    assert ("piazza", "intimacy") in targets
    assert ("caffe", "intimacy") in targets
