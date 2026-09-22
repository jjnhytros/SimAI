"""MentorshipService — relazione mentore-apprendista.

La relazione `MENTOR_OF` esiste già (RelationshipKind). Qui aggiungiamo:
  - tracking `sessions_completed` in metadata_json
  - mentoring_boost al talent apprendimento dello studente
  - graduation quando sessions >= threshold
  - trasmissione valori culturali
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Final

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.config.anthalys import SECONDS_PER_YEAR
from simai.core.anthalys_datetime import AnthalysDateTime
from simai.npc.identity.models import CulturalProfile
from simai.npc.memory.enums import MemoryKind
from simai.npc.memory.service import MemoryService
from simai.npc.models import Character
from simai.npc.relationships.enums import RelationshipKind
from simai.npc.relationships.models import Relationship
from simai.npc.skills.enums import SkillType
from simai.npc.skills.service import SkillService
from simai.npc.traits.derivation import names_to_traits, traits_to_names
from simai.npc.traits.enums import Trait

#: Gap minimo di età (anni) tra mentore e studente.
MIN_AGE_GAP: Final[int] = 8

#: Età minima del mentore.
MIN_MENTOR_AGE: Final[int] = 25

#: Età massima dello studente.
MAX_STUDENT_AGE: Final[int] = 30

#: Skill minima del mentore per poter insegnare.
MIN_MENTOR_SKILL_LEVEL: Final[int] = 5

#: Numero di sessioni per la "laurea" (graduation).
SESSIONS_TO_GRADUATE: Final[int] = 20

#: Boost di apprendimento per lo studente.
MENTOR_TALENT_BOOST: Final[float] = 0.20

#: Tratti trasmissibili da mentore a studente (con probabilità).
TRANSFERABLE_TRAITS: Final[tuple[Trait, ...]] = (
    Trait.INTELLETTUALE,
    Trait.CURIOSO,
    Trait.RIFLESSIVO,
    Trait.ORDINATO,
    Trait.PRATICO,
    Trait.AMBIZIOSO,
    Trait.ARTISTICO,
)

#: Probabilità di trasmissione tratto per sessione.
TRAIT_TRANSFER_PROBABILITY: Final[float] = 0.03


@dataclass(frozen=True, slots=True)
class MentorshipEvaluation:
    """Esito della valutazione di un possibile mentoring."""

    eligible: bool
    reason: str
    skill_type: SkillType | None


@dataclass(frozen=True, slots=True)
class MentorshipSession:
    """Esito di una sessione di mentoring."""

    completed: bool
    sessions_total: int
    graduated: bool
    trait_transferred: Trait | None
    culture_shifted: bool


class MentorshipService:
    """Servizio stateless di mentoring."""

    # ------------------------------------------------------------------
    # Eligibility
    # ------------------------------------------------------------------

    @staticmethod
    def evaluate(
        session: Session,
        mentor: Character,
        student: Character,
        *,
        current_dt: AnthalysDateTime,
    ) -> MentorshipEvaluation:
        """Valuta se il mentor può insegnare allo studente."""
        if mentor.id == student.id:
            return MentorshipEvaluation(False, "self", None)
        if not mentor.is_alive or not student.is_alive:
            return MentorshipEvaluation(False, "not_alive", None)

        mentor_age = MentorshipService._age_years(mentor, current_dt)
        student_age = MentorshipService._age_years(student, current_dt)

        if mentor_age < MIN_MENTOR_AGE:
            return MentorshipEvaluation(False, f"mentor_too_young ({mentor_age})", None)
        if student_age > MAX_STUDENT_AGE:
            return MentorshipEvaluation(False, f"student_too_old ({student_age})", None)
        if mentor_age - student_age < MIN_AGE_GAP:
            return MentorshipEvaluation(False, f"gap_too_small ({mentor_age - student_age})", None)

        # Trova la skill più alta del mentor
        mentor_skills = SkillService.all_skills(session, mentor.id)
        if not mentor_skills:
            return MentorshipEvaluation(False, "mentor_no_skills", None)

        best = max(mentor_skills, key=lambda s: s.level)
        if best.level < MIN_MENTOR_SKILL_LEVEL:
            return MentorshipEvaluation(False, f"mentor_low_skill ({best.level})", None)

        try:
            skill_type = SkillType(best.skill_type)
        except ValueError:
            return MentorshipEvaluation(False, "invalid_skill", None)

        return MentorshipEvaluation(True, "ok", skill_type)

    # ------------------------------------------------------------------
    # Sessioni
    # ------------------------------------------------------------------

    @staticmethod
    def register_session(
        session: Session,
        rel: Relationship,
        *,
        mentor: Character,
        student: Character,
        skill_type: SkillType,
        current_dt: AnthalysDateTime,
        rng: random.Random,
    ) -> MentorshipSession:
        """Registra una sessione di mentoring completata."""
        md = dict(rel.metadata_json or {})
        sessions = int(md.get("sessions_completed", 0)) + 1
        already_graduated = bool(md.get("graduated", False))

        md["sessions_completed"] = sessions
        md["skill_type"] = skill_type.value
        md["last_session_at"] = current_dt.to_total_seconds()

        # Trait transfer
        trait_transferred: Trait | None = None
        if rng.random() < TRAIT_TRANSFER_PROBABILITY:
            candidate = MentorshipService._pick_transferable_trait(mentor, student, rng)
            if candidate is not None:
                traits = names_to_traits(student.traits_json or [])
                if candidate not in traits:
                    traits.append(candidate)
                    student.traits_json = traits_to_names(traits)
                    trait_transferred = candidate

        # Culture shift (piccolo)
        culture_shifted = False
        if sessions % 5 == 0:
            culture_shifted = MentorshipService._shift_culture(mentor, student)

        # Graduation
        graduated = False
        if not already_graduated and sessions >= SESSIONS_TO_GRADUATE:
            md["graduated"] = True
            md["graduated_at"] = current_dt.to_total_seconds()
            graduated = True
            MentorshipService._on_graduation(session, mentor, student, skill_type, current_dt)

        rel.metadata_json = md
        session.flush()

        return MentorshipSession(
            completed=True,
            sessions_total=sessions,
            graduated=graduated,
            trait_transferred=trait_transferred,
            culture_shifted=culture_shifted,
        )

    # ------------------------------------------------------------------
    # Talent boost
    # ------------------------------------------------------------------

    @staticmethod
    def talent_boost_for(
        rel: Relationship | None,
        skill_type: SkillType,
    ) -> float:
        """Ritorna il boost di talent dall'essere studente in mentoring attivo.

        Range: [0, MENTOR_TALENT_BOOST]. Zero se non mentorato o skill diversa.
        """
        if rel is None:
            return 0.0
        md = rel.metadata_json or {}
        if md.get("graduated", False):
            return 0.0
        tracked_skill = md.get("skill_type")
        if tracked_skill != skill_type.value:
            return 0.0
        return MENTOR_TALENT_BOOST

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    @staticmethod
    def _age_years(character: Character, current_dt: AnthalysDateTime) -> int:
        age_secs = current_dt.to_total_seconds() - character.birth_total_seconds
        return int(age_secs // SECONDS_PER_YEAR)

    @staticmethod
    def _pick_transferable_trait(
        mentor: Character,
        student: Character,
        rng: random.Random,
    ) -> Trait | None:
        mentor_traits = set(names_to_traits(mentor.traits_json or []))
        student_traits = set(names_to_traits(student.traits_json or []))
        candidates = [
            t for t in TRANSFERABLE_TRAITS if t in mentor_traits and t not in student_traits
        ]
        if not candidates:
            return None
        return rng.choice(candidates)

    @staticmethod
    def _shift_culture(mentor: Character, student: Character) -> bool:
        """Sposta la cultura dello studente verso quella del mentore."""
        from simai.npc.identity import IdentityService

        c_mentor = IdentityService.get_culture(mentor)
        c_student = IdentityService.get_culture(student)

        # Blend 5%
        def _blend(a: float, b: float) -> float:
            return max(0.0, min(1.0, a * 0.95 + b * 0.05))

        new_profile = CulturalProfile(
            permissiveness=_blend(c_student.permissiveness, c_mentor.permissiveness),
            modesty=_blend(c_student.modesty, c_mentor.modesty),
            gender_role_strict=_blend(c_student.gender_role_strict, c_mentor.gender_role_strict),
            reaction_to_taboo=c_student.reaction_to_taboo,
            tradition=c_student.tradition,
        )
        attrs = dict(student.attributes_json or {})
        attrs["cultural_profile"] = new_profile.to_dict()
        student.attributes_json = attrs
        return True

    @staticmethod
    def _on_graduation(
        session: Session,
        mentor: Character,
        student: Character,
        skill_type: SkillType,
        current_dt: AnthalysDateTime,
    ) -> None:
        """Memoria + opinion boost reciproco alla laurea."""
        from simai.npc.reputation import ReputationService

        text = (
            f"{student.full_name} ha completato il percorso con "
            f"{mentor.full_name} in {skill_type.value}"
        )
        for owner, other in ((mentor, student), (student, mentor)):
            MemoryService.record(
                session,
                owner_id=owner.id,
                kind=MemoryKind.EMOTIONAL,
                text=text,
                current_dt=current_dt,
                valence=0.85,
                saliency=0.70,
                participants=[other.id],
                tags=["mentorship", "graduation"],
                lifecycle_event=True,
            )

        ReputationService.update_opinion(
            session,
            observer_id=mentor.id,
            target_id=student.id,
            delta=+20.0,
            current_dt=current_dt,
        )
        ReputationService.update_opinion(
            session,
            observer_id=student.id,
            target_id=mentor.id,
            delta=+30.0,
            current_dt=current_dt,
        )
        logger.info(
            "Mentorship graduation: mentor={} student={} skill={}",
            mentor.id,
            student.id,
            skill_type.value,
        )

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    @staticmethod
    def active_mentor_of(session: Session, student_id: int) -> Relationship | None:
        """Ritorna la relazione MENTOR_OF attiva per lo studente (se esiste)."""
        rel = session.scalars(
            select(Relationship).where(
                Relationship.to_id == student_id,
                Relationship.kind == RelationshipKind.MENTOR_OF.value,
            )
        ).first()
        if rel is None:
            return None
        md = rel.metadata_json or {}
        if md.get("graduated", False):
            return None
        return rel

    @staticmethod
    def all_mentorships(session: Session) -> list[Relationship]:
        return list(
            session.scalars(
                select(Relationship).where(Relationship.kind == RelationshipKind.MENTOR_OF.value)
            )
        )


__all__ = [
    "MAX_STUDENT_AGE",
    "MENTOR_TALENT_BOOST",
    "MIN_AGE_GAP",
    "MIN_MENTOR_AGE",
    "MIN_MENTOR_SKILL_LEVEL",
    "SESSIONS_TO_GRADUATE",
    "TRAIT_TRANSFER_PROBABILITY",
    "TRANSFERABLE_TRAITS",
    "MentorshipEvaluation",
    "MentorshipService",
    "MentorshipSession",
]
