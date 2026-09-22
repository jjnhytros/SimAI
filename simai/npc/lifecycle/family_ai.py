"""FamilyAI — decide il concepimento in modo rule-based.

Non è un LLM né un behaviour tree: un modello interpretabile con
fattori pesati (età, relazione, aspirazione, tratti, mood, bisogni,
gap tra figli).

Punti d'ingresso:
  - `evaluate_couple(mother, father, current_dt) -> ConceptionEvaluation`
  - `try_conceive(...) -> ConceptionResult` (tira il dado, crea Pregnancy)
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Final

from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.config.anthalys import SECONDS_PER_DAY, SECONDS_PER_YEAR
from simai.core.anthalys_datetime import AnthalysDateTime
from simai.npc.lifecycle.pregnancy import (
    ConceptionResult,
    PregnancyService,
)
from simai.npc.models import Character
from simai.npc.mood import MoodState
from simai.npc.needs.enums import NeedState, NeedType
from simai.npc.needs.needs import Needs
from simai.npc.relationships.enums import RelationshipKind
from simai.npc.relationships.family_tree import FamilyTreeService
from simai.npc.relationships.models import Relationship
from simai.npc.traits.enums import Aspiration, Trait

# ---------------------------------------------------------------------------
# Parametri
# ---------------------------------------------------------------------------

#: Probabilità base di concepimento per giorno di tentativo.
BASE_DAILY_PROBABILITY: Final[float] = 0.05

#: Forza minima della relazione di coppia per considerare il concepimento.
MIN_COUPLE_STRENGTH: Final[float] = 0.5

#: Età (anni Anthalys) sotto cui il concepimento è scoraggiato ma possibile.
TEEN_AGE_YEARS: Final[int] = 18

#: Età (anni) oltre cui la fertilità femminile declina.
FEMALE_DECLINE_AGE_YEARS: Final[int] = 60

#: Gap minimo (giorni) tra la nascita di un figlio e il prossimo concepimento.
MIN_BIRTH_GAP_DAYS: Final[int] = 400

#: Tratti che aumentano la propensione al concepimento.
FAMILY_TRAITS: frozenset[Trait] = frozenset(
    {Trait.GENTILE, Trait.EMPATICO, Trait.LEALE, Trait.GENEROSO}
)

#: Relazioni di coppia che abilitano il concepimento.
COUPLE_KINDS: frozenset[RelationshipKind] = frozenset(
    {RelationshipKind.SPOUSE_OF, RelationshipKind.PARTNER_OF}
)


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ConceptionEvaluation:
    """Esito della valutazione di una coppia."""

    eligible: bool
    probability: float
    reason: str
    factors: dict[str, float]


# ---------------------------------------------------------------------------
# FamilyAI
# ---------------------------------------------------------------------------


class FamilyAI:
    """AI di pianificazione familiare."""

    def __init__(self, seed: int = 0, master_seed: int = 0) -> None:
        self._seed = seed
        self._master_seed = master_seed
        self._rng = random.Random(seed)

    @property
    def seed(self) -> int:
        return self._seed

    # ------------------------------------------------------------------
    # API pubblica
    # ------------------------------------------------------------------

    def evaluate_couple(
        self,
        session: Session,
        mother: Character,
        father: Character,
        current_dt: AnthalysDateTime,
    ) -> ConceptionEvaluation:
        """Valuta se la coppia può concepire. Non tira il dado."""
        factors: dict[str, float] = {}
        current_secs = current_dt.to_total_seconds()

        # 1. Vitalità
        if not mother.is_alive or not father.is_alive:
            return ConceptionEvaluation(False, 0.0, "not_alive", factors)

        # 2. Fertilità biologica
        if not PregnancyService.is_fertile(mother, current_dt):
            return ConceptionEvaluation(False, 0.0, "mother_not_fertile", factors)
        if not PregnancyService.is_fertile(father, current_dt):
            return ConceptionEvaluation(False, 0.0, "father_not_fertile", factors)

        # 3. Relazione di coppia
        rel = self._find_couple_relation(session, mother.id, father.id)
        if rel is None or rel.strength < MIN_COUPLE_STRENGTH:
            return ConceptionEvaluation(False, 0.0, "not_a_couple", factors)

        # 4. Gravidanza attiva
        if PregnancyService.has_active_pregnancy(session, mother.id):
            return ConceptionEvaluation(False, 0.0, "already_pregnant", factors)

        # 5. Gap tra figli
        days_since_youngest = self._days_since_youngest_child(session, mother.id, current_secs)
        if days_since_youngest is not None and days_since_youngest < MIN_BIRTH_GAP_DAYS:
            return ConceptionEvaluation(
                False, 0.0, f"recent_child ({days_since_youngest:.0f}d)", factors
            )

        # 6. Probabilità
        p = BASE_DAILY_PROBABILITY
        factors["base"] = p

        # 6a. Aspirazione
        asp_boost = 1.0
        if Aspiration.FAMILY.value in (mother.aspirations_json or []):
            asp_boost *= 2.0
        if Aspiration.FAMILY.value in (father.aspirations_json or []):
            asp_boost *= 1.5
        p *= asp_boost
        factors["aspiration"] = asp_boost

        # 6b. Tratti
        trait_boost = 0.0
        for trait_name in (mother.traits_json or []) + (father.traits_json or []):
            try:
                if Trait(trait_name) in FAMILY_TRAITS:
                    trait_boost += 0.15
            except ValueError:
                continue
        trait_factor = 1.0 + min(trait_boost, 0.5)
        p *= trait_factor
        factors["traits"] = trait_factor

        # 6c. Mood
        mood_factor = self._mood_factor(mother, father)
        p *= mood_factor
        factors["mood"] = mood_factor

        # 6d. Bisogni critici
        needs_factor = self._needs_factor(mother, father)
        p *= needs_factor
        factors["needs"] = needs_factor

        # 6e. Età
        age_factor = self._age_factor(mother, current_secs)
        p *= age_factor
        factors["age"] = age_factor

        # 6f. Strenght della relazione
        rel_factor = 0.5 + rel.strength  # [0.5, 1.5]
        p *= rel_factor
        factors["relationship_strength"] = rel_factor

        return ConceptionEvaluation(True, min(p, 1.0), "ok", factors)

    def try_conceive(
        self,
        session: Session,
        mother: Character,
        father: Character,
        current_dt: AnthalysDateTime,
    ) -> ConceptionResult:
        """Valuta + tira il dado. Se OK, crea `Pregnancy` e ritorna successo."""
        eval_ = self.evaluate_couple(session, mother, father, current_dt)
        if not eval_.eligible:
            return ConceptionResult(False, eval_.reason, None)

        if self._rng.random() >= eval_.probability:
            return ConceptionResult(False, "no_conception", None)

        return PregnancyService.conceive(
            session,
            mother=mother,
            father=father,
            current_dt=current_dt,
            rng=self._rng,
            probability=1.0,  # già filtrato sopra
        )

    def reset_rng(self, seed: int | None = None) -> None:
        if seed is not None:
            self._seed = seed
        self._rng = random.Random(self._seed)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _find_couple_relation(session: Session, a_id: int, b_id: int) -> Relationship | None:
        """Cerca una relazione di coppia tra `a` e `b` (in qualsiasi direzione)."""
        kinds = [k.value for k in COUPLE_KINDS]
        row = session.scalars(
            select(Relationship).where(
                Relationship.from_id == a_id,
                Relationship.to_id == b_id,
                Relationship.kind.in_(kinds),
            )
        ).first()
        return row

    @staticmethod
    def _days_since_youngest_child(
        session: Session, mother_id: int, current_secs: int
    ) -> float | None:
        """Giorni dall'ultima nascita di un figlio della madre. ``None`` se nessuno."""
        children = FamilyTreeService.children_of(session, mother_id)
        if not children:
            return None
        # Trova il più giovane (birth_total_seconds massimo)
        youngest_birth = max(c.birth_total_seconds for c in children)
        return (current_secs - youngest_birth) / SECONDS_PER_DAY

    @staticmethod
    def _mood_factor(mother: Character, father: Character) -> float:
        """Fattore di mood: basso se tristi, alto se felici."""
        m1 = MoodState.from_dict(mother.mood_json or {}).happiness
        m2 = MoodState.from_dict(father.mood_json or {}).happiness
        avg = (m1 + m2) / 2.0
        if avg < 0.4:
            return 0.5
        if avg > 0.7:
            return 1.3
        return 1.0

    @staticmethod
    def _needs_factor(mother: Character, father: Character) -> float:
        """Fattore di bisogni: critico se qualcuno ha un bisogno CRITICAL."""
        for c in (mother, father):
            needs = Needs.from_dict(c.needs_json or {})
            for need in NeedType:
                if needs.state(need) is NeedState.CRITICAL:
                    return 0.2
        return 1.0

    @staticmethod
    def _age_factor(mother: Character, current_secs: int) -> float:
        """Fattore età della madre."""
        age_secs = current_secs - mother.birth_total_seconds
        age_years = age_secs / SECONDS_PER_YEAR
        if age_years < TEEN_AGE_YEARS:
            return 0.3
        if age_years < 25:
            return 1.0
        if age_years < FEMALE_DECLINE_AGE_YEARS:
            return 1.0
        # Declino lineare 60→70, azzerato oltre 70 (ma già filtrato sopra)
        return max(0.1, 1.0 - (age_years - FEMALE_DECLINE_AGE_YEARS) / 10.0)


__all__ = [
    "BASE_DAILY_PROBABILITY",
    "COUPLE_KINDS",
    "FAMILY_TRAITS",
    "FEMALE_DECLINE_AGE_YEARS",
    "MIN_BIRTH_GAP_DAYS",
    "MIN_COUPLE_STRENGTH",
    "TEEN_AGE_YEARS",
    "ConceptionEvaluation",
    "FamilyAI",
]
