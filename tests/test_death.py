from pathlib import Path

import pytest
from alembic import command
from sqlalchemy import select
from sqlalchemy.engine import Engine

from simai.db.alembic_utils import get_alembic_config
from simai.db.session import get_engine, get_session_factory
from simai.npc.death import (
    DEATH_CAUSE_WEIGHTS,
    EXP_MAX_YEARS,
    MAX_AGE_YEARS,
    MORTALITY_BASE,
    MORTALITY_MAX,
    _roll_cause,
    check_age,
    check_probabilistic,
    kill,
    probability_of_death,
    probability_of_death_per_day,
)
from simai.world.enums import DeathCause
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


def test_kill_removes_character(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        result = kill(session, "erika", cause=DeathCause.MANUAL, tick_index=0)
        session.commit()
        assert result.success
        assert result.cause == DeathCause.MANUAL
    with factory() as session:
        erika = session.scalar(select(Character).where(Character.key == "erika"))
    assert erika is None


def test_kill_unknown_character(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        result = kill(session, "nobody", cause=DeathCause.MANUAL, tick_index=0)
        session.commit()
        assert not result.success
        assert result.error is not None


def test_kill_distributes_balance(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        erika = session.scalar(select(Character).where(Character.key == "erika"))
        giulia = session.scalar(select(Character).where(Character.key == "giulia"))
        assert erika is not None and giulia is not None
        erika.balance = 100.0
        giulia_before = giulia.balance
        session.commit()

        result = kill(session, "erika", cause=DeathCause.MANUAL, tick_index=0)
        session.commit()
        assert result.success
        assert result.inheritance is not None
        assert result.inheritance.allocations == {"giulia": 100.0}
    with factory() as session:
        giulia = session.scalar(select(Character).where(Character.key == "giulia"))
        assert giulia is not None
        assert giulia.balance == giulia_before + 100.0


def test_kill_cancels_relationships(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from simai.relationships.models import Relationship

    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        erika = session.scalar(select(Character).where(Character.key == "erika"))
        assert erika is not None
        erika_id = erika.id
        kill(session, "erika", cause=DeathCause.MANUAL, tick_index=0)
        session.commit()
    with factory() as session:
        erika_rels = session.scalars(
            select(Relationship).where(
                (Relationship.from_character_id == erika_id)
                | (Relationship.to_character_id == erika_id)
            )
        ).all()
    assert erika_rels == []


def test_check_age_kills_at_100(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        erika = session.scalar(select(Character).where(Character.key == "erika"))
        assert erika is not None
        erika.age_years = MAX_AGE_YEARS
        session.commit()

        kills = check_age(session, tick_index=0)
        session.commit()
        assert len(kills) == 1
        assert kills[0].character_key == "erika"
        assert kills[0].cause == DeathCause.OLD_AGE
    with factory() as session:
        erika = session.scalar(select(Character).where(Character.key == "erika"))
    assert erika is None


def test_check_age_no_kill_below_100(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        kills = check_age(session, tick_index=0)
        session.commit()
    assert kills == []


def test_probability_of_death_boundaries() -> None:
    assert probability_of_death(0) == MORTALITY_BASE
    assert probability_of_death(EXP_MAX_YEARS) == 1.0
    assert probability_of_death(EXP_MAX_YEARS + 50) == 1.0


def test_probability_of_death_monotonic() -> None:
    prev = -1.0
    for age in range(0, EXP_MAX_YEARS + 1, 10):
        p = probability_of_death(age)
        assert p >= prev
        prev = p


def test_probability_of_death_at_99_near_max() -> None:
    p = probability_of_death(99)
    assert 0.03 < p < MORTALITY_MAX


def test_probability_of_death_per_day_conversion() -> None:
    p_anno = probability_of_death(42)
    p_giorno = probability_of_death_per_day(42)
    # Identità esatta: (1 - p_giorno)^DAYS_PER_YEAR = 1 - p_anno
    # (la conversione annuale→giornaliera è composta, non lineare).
    from simai.economy.calendar import DAYS_PER_YEAR

    assert abs((1.0 - p_giorno) ** DAYS_PER_YEAR - (1.0 - p_anno)) < 1e-12
    # Sanity: p_giorno è vicino a p_anno/DAYS_PER_YEAR, ma non uguale
    # (compounding). Tolleranza relativa 1% copre l'errore di
    # linearizzazione per p fino a ~5%.
    assert abs(p_giorno * DAYS_PER_YEAR - p_anno) / p_anno < 0.01


def test_death_cause_weights_sum_to_one() -> None:
    assert abs(sum(w for _, w in DEATH_CAUSE_WEIGHTS) - 1.0) < 1e-9


def test_roll_cause_distribution() -> None:
    import random as _random

    rng = _random.Random(12345)
    counts: dict[str, int] = {}
    for _ in range(10000):
        c = _roll_cause(rng).value
        counts[c] = counts.get(c, 0) + 1
    total = sum(counts.values())
    assert 0.57 < counts.get("illness", 0) / total < 0.63
    assert 0.27 < counts.get("accident", 0) / total < 0.33
    assert 0.08 < counts.get("violence", 0) / total < 0.12
    # UNKNOWN non deve mai essere generato
    assert "unknown" not in counts


def test_check_probabilistic_mechanism(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Meccanismo: se p_giorno = 1.0, tutti muoiono in 1 giorno.

    Patch di `probability_of_death_per_day` (punto di chiamata),
    non delle costanti: più robusto, non dipende da come la
    formula legge le globali.
    """
    import simai.npc.death as death_mod

    monkeypatch.setattr(
        death_mod,
        "probability_of_death_per_day",
        lambda _age: 1.0,
    )

    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        chars_before = len(session.scalars(select(Character)).all())
        assert chars_before == 5

    with factory() as session:
        kills = check_probabilistic(session, tick_index=0, master_seed=42)
        session.commit()
    assert len(kills) == 5
    with factory() as session:
        chars_after = session.scalars(select(Character)).all()
    assert chars_after == []


def test_check_probabilistic_skips_age_100(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Chi ha 100+ anni è gestito da OLD_AGE, non da probabilistic."""
    import simai.npc.death as death_mod

    monkeypatch.setattr(
        death_mod,
        "probability_of_death_per_day",
        lambda _age: 1.0,
    )

    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        for char in session.scalars(select(Character)).all():
            char.age_years = MAX_AGE_YEARS
        session.commit()

    with factory() as session:
        kills = check_probabilistic(session, tick_index=0, master_seed=42)
        session.commit()
    assert kills == []


def test_check_probabilistic_deterministic(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Stesso seed, stesse età, stesso tick → stesso esito."""
    import simai.npc.death as death_mod

    # p_giorno a 42 anni è ~1e-6: forzo una probabilità alta per
    # garantire almeno una morte con seed fisso.
    monkeypatch.setattr(
        death_mod,
        "probability_of_death_per_day",
        lambda _age: 0.5,
    )

    results: list[list[str]] = []
    for _ in range(2):
        engine = _seeded(tmp_path / str(len(results)), monkeypatch)
        factory = get_session_factory(engine)
        with factory() as session:
            kills = check_probabilistic(session, tick_index=0, master_seed=42)
            session.commit()
        results.append([k.character_key for k in kills if k.success])
    assert results[0] == results[1]


def test_kill_cancels_pregnancy_when_mother_dies(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Madre morente: la gravidanza non arriva a termine."""
    from simai.world.models import Pregnancy

    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        giulia = session.scalar(select(Character).where(Character.key == "giulia"))
        luca = session.scalar(select(Character).where(Character.key == "luca"))
        assert giulia is not None and luca is not None
        session.add(
            Pregnancy(
                character_id=giulia.id,
                partner_id=luca.id,
                conceived_at_tick=0,
                due_at_tick=8400,
            )
        )
        session.commit()

    with factory() as session:
        kill(session, "giulia", cause=DeathCause.MANUAL, tick_index=0)
        session.commit()

    with factory() as session:
        rows = session.scalars(select(Pregnancy)).all()
    assert rows == []


def test_kill_keeps_pregnancy_when_father_dies(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Padre morente: la gravidanza resta, senza partner."""
    from simai.world.models import Pregnancy

    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        giulia = session.scalar(select(Character).where(Character.key == "giulia"))
        luca = session.scalar(select(Character).where(Character.key == "luca"))
        assert giulia is not None and luca is not None
        session.add(
            Pregnancy(
                character_id=giulia.id,
                partner_id=luca.id,
                conceived_at_tick=0,
                due_at_tick=8400,
            )
        )
        session.commit()

    with factory() as session:
        kill(session, "luca", cause=DeathCause.MANUAL, tick_index=0)
        session.commit()

    with factory() as session:
        rows = session.scalars(select(Pregnancy)).all()
        assert len(rows) == 1
        assert rows[0].partner_id is None
        assert rows[0].character_id is not None
