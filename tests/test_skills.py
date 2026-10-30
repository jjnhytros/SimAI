from pathlib import Path

import pytest
from alembic import command
from sqlalchemy import select
from sqlalchemy.engine import Engine

from simai.db.alembic_utils import get_alembic_config
from simai.db.session import get_engine, get_session_factory
from simai.economy.payday import process_payday
from simai.needs.enums import NeedKind
from simai.needs.models import Need
from simai.skills.enums import SkillKind
from simai.skills.models import Skill
from simai.skills.service import level_of, skill_of, skills_of, wage_with_skill
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


def _char_id(session, key: str) -> int:
    c = session.scalar(select(Character).where(Character.key == key))
    assert c is not None
    return c.id


def test_seed_creates_five_skills(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        skills = session.scalars(select(Skill)).all()
    assert len(skills) == 5


def test_skill_of_returns_expected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        luca_id = _char_id(session, "luca")
        skill = skill_of(session, luca_id, SkillKind.BARISTA)
        assert skill is not None
        assert skill.level == 40.0


def test_skill_of_missing_returns_none(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        luca_id = _char_id(session, "luca")
        assert skill_of(session, luca_id, SkillKind.INSEGNANTE) is None


def test_level_of_missing_returns_zero(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        luca_id = _char_id(session, "luca")
        assert level_of(session, luca_id, SkillKind.INSEGNANTE) == 0.0


def test_skills_of_orders_by_kind(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        # giulia ha una sola skill (INSEGNANTE)
        giulia_id = _char_id(session, "giulia")
        skills = skills_of(session, giulia_id)
        assert len(skills) == 1
        assert skills[0].kind == SkillKind.INSEGNANTE


def test_wage_with_skill_levels() -> None:
    assert wage_with_skill(25.0, 0.0) == 25.0
    assert wage_with_skill(25.0, 50.0) == 31.25
    assert wage_with_skill(25.0, 100.0) == 37.5
    assert wage_with_skill(25.0, 200.0) == 37.5  # clip
    assert wage_with_skill(25.0, -10.0) == 25.0  # clip


def test_payday_uses_skill(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        luca = session.scalar(select(Character).where(Character.key == "luca"))
        assert luca is not None
        caffe = session.scalar(select(Character).where(Character.key == "luca"))
        assert caffe is not None
        # luca è al caffè (seed), turno 14-21 -> payday al tick 20.
        # Forzo tick_index = 20 (t_in_day = 20, schedule_end_tick = 21,
        # t_in_day == 20 == 21-1).
        balance_before = luca.balance
        session.commit()

    with factory() as session:
        report = process_payday(session, tick_index=20)
        session.commit()

    assert report.paid >= 1
    with factory() as session:
        luca = session.scalar(select(Character).where(Character.key == "luca"))
        assert luca is not None
        # 25 * (1 + 40/200) = 30.0
        assert luca.balance == balance_before + 30.0


def test_skill_check_constraint(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Il CHECK su level blocca valori fuori range."""
    from sqlalchemy.exc import IntegrityError

    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        luca_id = _char_id(session, "luca")
        with pytest.raises(IntegrityError):
            session.add(Skill(character_id=luca_id, kind=SkillKind.COMMESSO, level=150.0))
            session.flush()
        session.rollback()


def test_train_skill_increases(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from simai.skills.service import train_skill

    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        luca_id = _char_id(session, "luca")
        before = level_of(session, luca_id, SkillKind.BARISTA)
        new = train_skill(session, luca_id, SkillKind.BARISTA, 0.5)
        session.commit()
    assert new == before + 0.5


def test_train_skill_caps_at_100(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from simai.skills.service import train_skill

    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        luca_id = _char_id(session, "luca")
        new = train_skill(session, luca_id, SkillKind.BARISTA, 200.0)
        session.commit()
    assert new == 100.0


def test_train_skill_creates_if_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from simai.skills.service import train_skill

    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        luca_id = _char_id(session, "luca")
        assert skill_of(session, luca_id, SkillKind.INSEGNANTE) is None
        new = train_skill(session, luca_id, SkillKind.INSEGNANTE, 5.0)
        session.commit()
        assert new == 5.0
        assert skill_of(session, luca_id, SkillKind.INSEGNANTE) is not None


def test_skill_for_job_title_mapping() -> None:
    from simai.economy.enums import JobTitle
    from simai.skills.service import skill_for_job_title

    assert skill_for_job_title(JobTitle.BARISTA.value) == SkillKind.BARISTA
    assert skill_for_job_title(JobTitle.INSEGNANTE.value) == SkillKind.INSEGNANTE
    assert skill_for_job_title(JobTitle.COMMESSO.value) == SkillKind.COMMESSO
    assert skill_for_job_title(JobTitle.STUDENTE.value) == SkillKind.STUDENTE


def test_working_tick_increases_skill(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Tick WORKING: +0.001 (training) + 0.00005 (opportunistico, idle)."""
    from simai.sim.tick import run_tick

    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    # tick 14 -> t_in_day 14, luca 14-21 -> WORKING. Luca è già al caffè.
    with factory() as session:
        luca_id = _char_id(session, "luca")
        before = level_of(session, luca_id, SkillKind.BARISTA)
    with factory() as session:
        run_tick(session, minutes=60, tick_index=14, master_seed=42)
        session.commit()
    with factory() as session:
        luca_id = _char_id(session, "luca")
        after = level_of(session, luca_id, SkillKind.BARISTA)
    assert after == pytest.approx(before + 0.001 + 0.00005)


def test_non_working_tick_trains_opportunistically_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Tick fuori orario: niente training WORKING, solo opportunistico."""
    from simai.sim.tick import run_tick

    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    # tick 5 -> t_in_day 5, luca BEFORE_WORK
    with factory() as session:
        luca_id = _char_id(session, "luca")
        before = level_of(session, luca_id, SkillKind.BARISTA)
    with factory() as session:
        run_tick(session, minutes=60, tick_index=5, master_seed=42)
        session.commit()
    with factory() as session:
        luca_id = _char_id(session, "luca")
        after = level_of(session, luca_id, SkillKind.BARISTA)
    assert after == pytest.approx(before + 0.00005)


def test_study_in_catalog(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from simai.actions.catalog import actions_for_location
    from simai.actions.enums import ActionKind
    from simai.world.enums import LocationKind

    actions = actions_for_location(LocationKind.RESIDENTIAL)
    assert any(a.kind == ActionKind.STUDY for a in actions)


def test_study_trains_skill_in_tick(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Quando STUDY è scelto, la skill del job cresce di 0.01.

    Forza la scelta via monkeypatch di `choose_intent`: con FUN=0
    PLAY e STUDY sono entrambi disponibili, PLAY (score 100) vince
    su STUDY (score 80). Il branch idle non viene raggiunto, quindi
    ci si aspetta solo +0.01 (STUDY), niente opportunistico.
    """
    import simai.npc.manager as manager_module
    from simai.actions.catalog import CATALOG
    from simai.actions.enums import ActionKind
    from simai.actions.intent import Intent
    from simai.sim.tick import run_tick
    from simai.skills.enums import SkillKind

    study_action = next(a for a in CATALOG if a.kind == ActionKind.STUDY)

    def fake_choose_intent(needs, available_actions, available_moves, rng, traits=None):
        return Intent(action=study_action)

    monkeypatch.setattr(manager_module, "choose_intent", fake_choose_intent)

    engine = _seeded(tmp_path, monkeypatch)
    factory = get_session_factory(engine)
    with factory() as session:
        erika = session.scalar(select(Character).where(Character.key == "erika"))
        assert erika is not None
        for need in session.scalars(select(Need).where(Need.character_id == erika.id)).all():
            need.value = 100.0
        fun = session.scalar(
            select(Need).where(Need.character_id == erika.id, Need.kind == NeedKind.FUN)
        )
        assert fun is not None
        fun.value = 0.0
        session.commit()
        before = level_of(session, erika.id, SkillKind.STUDENTE)

    with factory() as session:
        run_tick(session, minutes=60, tick_index=0, master_seed=42)
        session.commit()

    with factory() as session:
        erika = session.scalar(select(Character).where(Character.key == "erika"))
        assert erika is not None
        after = level_of(session, erika.id, SkillKind.STUDENTE)
    assert after == pytest.approx(before + 0.01)
