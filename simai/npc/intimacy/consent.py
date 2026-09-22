"""ConsentService — modello di consenso attivo per azioni di intimità.

La willingness del partner è calcolata come prodotto di fattori:

    willingness = base × action × relationship × mood × needs × traits × recency

Decisione: `rng.random() < willingness`. Deterministico dato il seed.

Fattori e range:
  - base               : 0.50
  - action_factor      : 1.0 - 0.15 × action_level  (0.25..1.0)
  - relationship_factor: 0.50 + rel.strength        (0.50..1.50)
  - mood_factor        : da happiness partner       (0.30..1.30)
  - needs_factor       : CRITICAL -> 0.5; HIGH -> 1.2; altrimenti 1.0
  - trait_factor       : da tratti partner          (0.30..1.50)
  - recency_factor     : cooldown rifiuto -> 0.30; novelty -> 0.70; else 1.0

Il valore finale è clampato in [0, 1].
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Final

from sqlalchemy.orm import Session

from simai.config.anthalys import SECONDS_PER_DAY  # noqa: F401  (per futuro)
from simai.core.anthalys_datetime import AnthalysDateTime
from simai.npc.intimacy.actions import IntimacyActionDef
from simai.npc.models import Character
from simai.npc.mood import MoodState
from simai.npc.needs.enums import NeedState, NeedType
from simai.npc.needs.needs import Needs
from simai.npc.relationships.models import Relationship
from simai.npc.traits.enums import Trait

#: Willingness di base.
BASE_WILLINGNESS: Final[float] = 0.50

#: Riduzione per livello di azione (per unità di level).
ACTION_LEVEL_PENALTY: Final[float] = 0.15

#: Cooldown dopo un rifiuto (in tick Anthalys). ~30 min Anthalys.
REJECTION_COOLDOWN_TICKS: Final[int] = 100

#: Finestra di "novelty": ripetere la stessa azione entro questi tick
#: riduce la willingness.
NOVELTY_WINDOW_TICKS: Final[int] = 30

#: Fattori di penalità.
REJECTION_PENALTY: Final[float] = 0.30
NOVELTY_PENALTY: Final[float] = 0.70

#: Modificatori di tratti della willingness del partner.
TRAIT_WILLINGNESS_MODIFIERS: Final[dict[Trait, float]] = {
    Trait.EMOTIONALLY_EXPRESSIVE: 0.10,
    Trait.EMPATICO: 0.15,
    Trait.GENTILE: 0.10,
    Trait.IMPULSIVO: 0.05,
    Trait.PESSIMISTA: -0.10,
    Trait.PRUDENTE: -0.10,
    Trait.RIBELLE: -0.05,
    Trait.RISERVATO: -0.15,
    Trait.SEXUALLY_EXPLORATIVE: 0.15,
    Trait.SOCIALE: 0.10,
    Trait.SPENSIERATO: 0.10,
    Trait.TIMIDO: -0.20,
}


@dataclass(frozen=True, slots=True)
class ConsentResult:
    """Esito di una verifica di consenso."""

    accepted: bool
    willingness: float
    factors: dict[str, float] = field(default_factory=dict)


class ConsentService:
    """Servizio stateless di consenso attivo."""

    # ------------------------------------------------------------------
    # API pubblica
    # ------------------------------------------------------------------

    @staticmethod
    def check(
        session: Session,
        *,
        initiator: Character,
        partner: Character,
        action_def: IntimacyActionDef,
        rel: Relationship,
        current_dt: AnthalysDateTime,
        rng: random.Random,
    ) -> ConsentResult:
        """Verifica il consenso. Tira il dado se i fattori lo consentono."""
        willingness, factors = ConsentService.compute_willingness(
            session,
            initiator=initiator,
            partner=partner,
            action_def=action_def,
            rel=rel,
            current_dt=current_dt,
        )
        accepted = rng.random() < willingness
        return ConsentResult(accepted=accepted, willingness=willingness, factors=factors)

    @staticmethod
    def compute_willingness(
        session: Session,
        *,
        initiator: Character,
        partner: Character,
        action_def: IntimacyActionDef,
        rel: Relationship,
        current_dt: AnthalysDateTime,
    ) -> tuple[float, dict[str, float]]:
        factors: dict[str, float] = {}
        w = BASE_WILLINGNESS
        factors["base"] = w

        # Action level penalty
        action_factor = 1.0 - ACTION_LEVEL_PENALTY * action_def.level
        w *= action_factor
        factors["action"] = action_factor

        # Relationship strength
        rel_factor = 0.5 + float(rel.strength)
        w *= rel_factor
        factors["relationship"] = rel_factor

        # Mood del partner
        mood_factor = ConsentService._mood_factor(partner)
        w *= mood_factor
        factors["mood"] = mood_factor

        # Needs del partner
        needs_factor = ConsentService._needs_factor(partner)
        w *= needs_factor
        factors["needs"] = needs_factor

        # Traits del partner
        trait_factor = ConsentService._trait_factor(partner)
        w *= trait_factor
        factors["traits"] = trait_factor

        # Cultural factor (Chunk 3.6a)
        cultural_factor = ConsentService._cultural_factor(partner, action_def)
        w *= cultural_factor
        factors["culture"] = cultural_factor

        # Compatibility factor (Chunk 3.9c)
        from simai.npc.relationships.compatibility import CompatibilityService

        compat = CompatibilityService.compute(initiator, partner)
        compat_factor = 0.60 + 0.40 * compat  # range [0.60, 1.00]
        w *= compat_factor
        factors["compatibility"] = compat_factor

        # Connection factor (Chunk 3.9c)
        from simai.npc.relationships.connection import ConnectionService

        conn = ConnectionService.get(rel)
        conn_factor = 0.80 + 0.40 * conn  # range [0.80, 1.20]
        w *= conn_factor
        factors["connection"] = conn_factor

        # Libido asymmetry (Chunk 3.9c)
        from simai.npc.relationships.libido import LibidoService

        libido_factor = LibidoService.asymmetry_factor(initiator, partner, rel)
        w *= libido_factor
        factors["libido"] = libido_factor

        # Taboo consanguineità (Chunk 3.9a)
        from simai.npc.reputation import ReputationService

        consang_severity = ReputationService.consanguinity_severity(session, initiator, partner)
        if consang_severity > 0.0:
            consang_factor = max(0.0, 1.0 - consang_severity)
            w *= consang_factor
            factors["consanguinity"] = consang_factor

        # LGBTQ acceptance (Chunk 3.9e)
        from simai.npc.identity.lgbtq import LGBTQService

        lgbtq_factor = LGBTQService.pair_acceptance_factor(session, initiator, partner)
        w *= lgbtq_factor
        factors["lgbtq"] = lgbtq_factor

        # Teen dynamics (Chunk 3.9e)
        from simai.npc.relationships.teen import TeenDynamicsService

        teen_factor = TeenDynamicsService.willingness_modifier(
            initiator,
            partner,
            current_dt=current_dt,
            action_level=action_def.level,
        )
        w *= teen_factor
        factors["teen"] = teen_factor

        if action_def.level >= 3:
            parental_factor, _opposing = TeenDynamicsService.parental_opposition_factor(
                session, initiator, partner, current_dt=current_dt
            )
            w *= parental_factor
            factors["parental"] = parental_factor

        # SEP factor (Chunk 3.6a)
        sep_factor = ConsentService._sep_factor(partner)
        w *= sep_factor
        factors["sep"] = sep_factor

        # Stress factor (Chunk 3.7a)
        stress_factor = ConsentService._stress_factor(session, partner, current_dt)
        w *= stress_factor
        factors["stress"] = stress_factor

        # Desire factor (solo per azioni level >= 3)
        if action_def.level >= 3:
            desire_factor = ConsentService._desire_factor(partner)
            w *= desire_factor
            factors["desire"] = desire_factor

        # Recency (rifiuto + novelty)
        recency_factor = ConsentService._recency_factor(
            rel=rel,
            initiator_id=initiator.id,
            action_def=action_def,
            current_dt=current_dt,
        )
        w *= recency_factor
        factors["recency"] = recency_factor

        w = max(0.0, min(1.0, w))
        return w, factors

    # ------------------------------------------------------------------
    # Fattori
    # ------------------------------------------------------------------

    @staticmethod
    def _mood_factor(partner: Character) -> float:
        mood = MoodState.from_dict(partner.mood_json or {})
        happiness = mood.happiness
        if happiness < 0.3:
            return 0.30
        if happiness < 0.5:
            return 0.60
        if happiness < 0.7:
            return 1.00
        return 1.30

    @staticmethod
    def _needs_factor(partner: Character) -> float:
        needs = Needs.from_dict(partner.needs_json or {})
        # SOCIAL o FUN critici -> bassa willingness
        for need in (NeedType.SOCIAL, NeedType.FUN):
            if needs.state(need) is NeedState.CRITICAL:
                return 0.50
        # SOCIAL o FUN alti -> alta willingness
        high_count = sum(
            1 for need in (NeedType.SOCIAL, NeedType.FUN) if needs.state(need) is NeedState.HIGH
        )
        if high_count == 2:
            return 1.20
        return 1.00

    @staticmethod
    def _trait_factor(partner: Character) -> float:
        total = 0.0
        for trait_name in partner.traits_json or []:
            try:
                trait = Trait(trait_name)
            except ValueError:
                continue
            total += TRAIT_WILLINGNESS_MODIFIERS.get(trait, 0.0)
        # Base 1.0 + somma modifiers, clamp [0.3, 1.5]
        return max(0.30, min(1.50, 1.0 + total))

    @staticmethod
    def _sep_factor(partner: Character) -> float:
        """Fattore SEP: comfort × (1 - inhibition) mappato a [0.5, 1.5]."""
        from simai.npc.identity import IdentityService

        sep = IdentityService.get_sep(partner)
        raw = sep.comfort * (1.0 - sep.inhibition)
        # raw in [0, 1], mappiamo a [0.5, 1.5]
        return 0.5 + raw

    @staticmethod
    def _cultural_factor(partner: Character, action_def: IntimacyActionDef) -> float:
        """Fattore cultura: penalità per azioni ad alta intensità in culture
        modeste, bonus per azioni ad alta intensità in culture permissive.
        """
        from simai.npc.identity import IdentityService, TabooReaction

        culture = IdentityService.get_culture(partner)
        # Modestia riduce willingness per azioni level >= 3
        modesty_penalty = 0.0
        if action_def.level >= 3:
            modesty_penalty = culture.modesty * 0.30  # max -30%
        # Permissività aumenta willingness per azioni level >= 3
        permissiveness_bonus = 0.0
        if action_def.level >= 3:
            permissiveness_bonus = (culture.permissiveness - 0.5) * 0.20
        # Taboo: severo penalizza, lenient premia
        taboo_mod = 0.0
        if culture.reaction_to_taboo is TabooReaction.SEVERE:
            taboo_mod = -0.10
        elif culture.reaction_to_taboo is TabooReaction.LENIENT:
            taboo_mod = 0.10
        factor = 1.0 - modesty_penalty + permissiveness_bonus + taboo_mod

        return max(0.40, min(1.30, factor))

    @staticmethod
    def _stress_factor(session: Session, partner: Character, current_dt: AnthalysDateTime) -> float:
        """`1 - 0.5 × stress`, range [0.5, 1.0]."""
        from simai.npc.stress import StressService

        stress, _ = StressService.compute(session, partner, current_dt)
        return 1.0 - 0.5 * stress

    @staticmethod
    def _desire_factor(partner: Character) -> float:
        """`0.5 + 0.5 × desire`, range [0.5, 1.0]."""
        from simai.npc.desire import DesireService

        desire = DesireService.get_current(partner)
        return 0.5 + 0.5 * desire

    @staticmethod
    def _recency_factor(
        *,
        rel: Relationship,
        initiator_id: int,
        action_def: IntimacyActionDef,
        current_dt: AnthalysDateTime,
    ) -> float:
        """Fattore che considera cooldown rifiuto e novelty."""
        current_secs = current_dt.to_total_seconds()
        md = rel.metadata_json or {}

        # Cooldown rifiuto
        last_rejection = md.get("last_rejection_at")
        if isinstance(last_rejection, (int, float)):
            elapsed = current_secs - int(last_rejection)
            if 0 <= elapsed < REJECTION_COOLDOWN_TICKS * 100:  # 100 tick = 100*28*60/12 = ... min
                # Cooldown attivo
                return REJECTION_PENALTY

        # Novelty: stessa azione recente
        last_action = md.get("last_intimacy_action")
        last_at = md.get("last_intimacy_at")
        if last_action == action_def.action.value and isinstance(last_at, (int, float)):
            elapsed = current_secs - int(last_at)
            if 0 <= elapsed < NOVELTY_WINDOW_TICKS * 100:
                return NOVELTY_PENALTY

        return 1.0

    # ------------------------------------------------------------------
    # Aggiornamento metadata relazione (side-effect)
    # ------------------------------------------------------------------

    @staticmethod
    def record_rejection(
        rel: Relationship,
        *,
        current_dt: AnthalysDateTime,
    ) -> None:
        """Registra un rifiuto sulla relazione (metadata)."""
        md = dict(rel.metadata_json or {})
        md["last_rejection_at"] = current_dt.to_total_seconds()
        rel.metadata_json = md

    @staticmethod
    def record_action(
        rel: Relationship,
        *,
        action_def: IntimacyActionDef,
        current_dt: AnthalysDateTime,
    ) -> None:
        """Registra l'ultima azione eseguita sulla relazione (metadata)."""
        md = dict(rel.metadata_json or {})
        md["last_intimacy_action"] = action_def.action.value
        md["last_intimacy_at"] = current_dt.to_total_seconds()
        rel.metadata_json = md


__all__ = [
    "BASE_WILLINGNESS",
    "NOVELTY_PENALTY",
    "NOVELTY_WINDOW_TICKS",
    "REJECTION_COOLDOWN_TICKS",
    "REJECTION_PENALTY",
    "TRAIT_WILLINGNESS_MODIFIERS",
    "ConsentResult",
    "ConsentService",
]
