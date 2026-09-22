"""Pregnancy model + PregnancyService (concezione, gestazione, parto)."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, Final

from loguru import logger
from sqlalchemy import BigInteger, ForeignKey, String, select
from sqlalchemy.orm import Mapped, Session, mapped_column
from sqlalchemy.types import JSON

from simai.config.anthalys import SECONDS_PER_DAY, SECONDS_PER_YEAR
from simai.core.anthalys_datetime import AnthalysDateTime
from simai.db.base import Base, IdMixin, TimestampMixin
from simai.npc.enums import Sex
from simai.npc.generator import CharacterGenerator
from simai.npc.genetics.inheritance import roll_twins
from simai.npc.lifecycle.enums import PregnancyStatus
from simai.npc.lifestage_service import LifeStageService
from simai.npc.models import Character

#: Durata della gestazione in giorni Anthalys.
GESTATION_DAYS: Final[int] = 300

#: Età minima fertile (in anni Anthalys).
MIN_FERTILE_AGE_YEARS: Final[int] = 14

#: Età massima fertile per una donna (menopausa).
MAX_FEMALE_FERTILE_AGE_YEARS: Final[int] = 70

#: Età massima fertile per un uomo.
MAX_MALE_FERTILE_AGE_YEARS: Final[int] = 100

#: Probabilità di concepimento di default per singolo tentativo.
DEFAULT_CONCEPTION_PROBABILITY: Final[float] = 0.10


class Pregnancy(IdMixin, TimestampMixin, Base):
    """Una gravidanza in corso o completata."""

    __tablename__ = "pregnancy"

    mother_id: Mapped[int] = mapped_column(
        ForeignKey("character.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    father_id: Mapped[int | None] = mapped_column(
        ForeignKey("character.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    conception_total_seconds: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    due_total_seconds: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        index=True,
    )
    completed_total_seconds: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    child_ids_json: Mapped[list[int]] = mapped_column(JSON, default=list, nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    def __repr__(self) -> str:
        return (
            f"Pregnancy(id={self.id}, mother={self.mother_id}, "
            f"father={self.father_id}, status={self.status})"
        )


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ConceptionResult:
    """Esito di un tentativo di concepimento."""

    success: bool
    reason: str
    pregnancy_id: int | None


class PregnancyService:
    """API per concepimento e parto."""

    @staticmethod
    def is_fertile(character: Character, current_dt: AnthalysDateTime) -> bool:
        """``True`` se il Character può procreare al tempo dato."""
        if not character.is_alive:
            return False
        age_secs = LifeStageService.age_seconds_at(character.birth_total_seconds, current_dt)
        age_years = age_secs // SECONDS_PER_YEAR
        if age_years < MIN_FERTILE_AGE_YEARS:
            return False
        if character.sex == Sex.FEMALE.value:
            return age_years <= MAX_FEMALE_FERTILE_AGE_YEARS
        if character.sex == Sex.MALE.value:
            return age_years <= MAX_MALE_FERTILE_AGE_YEARS
        return False

    @staticmethod
    def has_active_pregnancy(session: Session, mother_id: int) -> bool:
        """``True`` se la madre ha già una gravidanza attiva."""
        row = session.scalars(
            select(Pregnancy).where(
                Pregnancy.mother_id == mother_id,
                Pregnancy.status == PregnancyStatus.ACTIVE.value,
            )
        ).first()
        return row is not None

    @staticmethod
    def conceive(
        session: Session,
        *,
        mother: Character,
        father: Character,
        current_dt: AnthalysDateTime,
        rng: random.Random,
        probability: float = DEFAULT_CONCEPTION_PROBABILITY,
    ) -> ConceptionResult:
        """Tenta un concepimento. Ritorna l'esito.

        Validazioni:
          - madre di sesso femminile
          - padre di sesso maschile
          - entrambi fertili
          - nessuna gravidanza attiva
          - `probability` in [0, 1]
        """
        if mother.sex != Sex.FEMALE.value:
            return ConceptionResult(False, "mother_not_female", None)
        if father.sex != Sex.MALE.value:
            return ConceptionResult(False, "father_not_male", None)
        if not (0.0 <= probability <= 1.0):
            raise ValueError(f"probability deve essere in [0, 1], ricevuto {probability}")

        if not PregnancyService.is_fertile(mother, current_dt):
            return ConceptionResult(False, "mother_not_fertile", None)
        if not PregnancyService.is_fertile(father, current_dt):
            return ConceptionResult(False, "father_not_fertile", None)
        if PregnancyService.has_active_pregnancy(session, mother.id):
            return ConceptionResult(False, "already_pregnant", None)

        if rng.random() >= probability:
            return ConceptionResult(False, "no_conception", None)

        conception_secs = current_dt.to_total_seconds()
        due_secs = conception_secs + GESTATION_DAYS * SECONDS_PER_DAY
        preg = Pregnancy(
            mother_id=mother.id,
            father_id=father.id,
            conception_total_seconds=conception_secs,
            due_total_seconds=due_secs,
            status=PregnancyStatus.ACTIVE.value,
            completed_total_seconds=None,
            child_ids_json=[],
            metadata_json={},
        )
        session.add(preg)
        session.flush()
        return ConceptionResult(True, "conceived", preg.id)

    @staticmethod
    def advance(
        session: Session,
        pregnancy: Pregnancy,
        current_dt: AnthalysDateTime,
        rng: random.Random,
        *,
        master_seed: int = 0,
    ) -> list[Character]:
        """Avanza una gravidanza. Se è dovuta, partorisce.

        Ritorna la lista dei figli nati (vuota se non è il momento o se
        la gravidanza è stata interrotta).
        """
        if pregnancy.status != PregnancyStatus.ACTIVE.value:
            return []

        # Verifica madre ancora viva
        mother = session.get(Character, pregnancy.mother_id)
        if mother is None or not mother.is_alive:
            pregnancy.status = PregnancyStatus.ABORTED.value
            pregnancy.completed_total_seconds = current_dt.to_total_seconds()
            logger.warning("Pregnancy {} abortita: madre non viva", pregnancy.id)
            session.flush()
            return []

        current_secs = current_dt.to_total_seconds()
        if current_secs < pregnancy.due_total_seconds:
            return []

        # Parto!
        children = PregnancyService._deliver(
            session,
            pregnancy=pregnancy,
            mother=mother,
            current_dt=current_dt,
            rng=rng,
            master_seed=master_seed,
        )
        return children

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    @staticmethod
    def _deliver(
        session: Session,
        *,
        pregnancy: Pregnancy,
        mother: Character,
        current_dt: AnthalysDateTime,
        rng: random.Random,
        master_seed: int,
    ) -> list[Character]:
        father: Character | None = None
        if pregnancy.father_id is not None:
            father = session.get(Character, pregnancy.father_id)

        is_twin, identical = roll_twins(rng)
        n_children = 2 if is_twin else 1

        gen = CharacterGenerator(master_seed=master_seed)
        children: list[Character] = []

        for _i in range(n_children):
            child_sex = rng.choice([Sex.MALE, Sex.FEMALE])
            # Genoma: ereditato se padre noto, altrimenti random (generator default)
            parents_tuple = (father, mother) if father is not None else None

            child = gen.generate(
                birth_datetime=current_dt,
                current_datetime=current_dt,
                sex=child_sex,
                parents=parents_tuple,
            )
            # Cognome: della madre se padre ignoto
            if father is None:
                child.last_name = mother.last_name
            session.add(child)
            session.flush()
            children.append(child)

        pregnancy.status = PregnancyStatus.DELIVERED.value
        pregnancy.completed_total_seconds = current_dt.to_total_seconds()
        pregnancy.child_ids_json = [c.id for c in children]
        if is_twin:
            pregnancy.metadata_json = {
                **(pregnancy.metadata_json or {}),
                "twin": True,
                "identical": identical,
            }
        session.flush()
        logger.info(
            "Pregnancy {} completata: {} figli (madre={}, padre={})",
            pregnancy.id,
            len(children),
            mother.id,
            father.id if father else "?",
        )
        return children


__all__ = [
    "DEFAULT_CONCEPTION_PROBABILITY",
    "GESTATION_DAYS",
    "MAX_FEMALE_FERTILE_AGE_YEARS",
    "MAX_MALE_FERTILE_AGE_YEARS",
    "MIN_FERTILE_AGE_YEARS",
    "ConceptionResult",
    "Pregnancy",
    "PregnancyService",
]
