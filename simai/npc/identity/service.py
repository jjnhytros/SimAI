"""IdentityService — inizializzazione, drift, eredità, query."""

from __future__ import annotations

import random
from typing import Final

from simai.npc.identity.enums import (
    TRADITION_RANGES,
    CulturalTradition,
)
from simai.npc.identity.models import (
    SEP,
    CulturalProfile,
    IdentityProfile,
    Sexuality,
)
from simai.npc.models import Character

#: Deviazione standard del drift mensile dell'orientamento.
FLUIDITY_SIGMA: Final[float] = 0.03

#: Età (anni Anthalys) sotto cui la fluidità è attiva.
FLUIDITY_MAX_AGE_YEARS: Final[int] = 40

#: Peso dell'eredità culturale (0.5 = media genitori + 0.5 rumore).
CULTURE_INHERITANCE_WEIGHT: Final[float] = 0.7


class IdentityService:
    """Servizio stateless per il dominio identità."""

    # ------------------------------------------------------------------
    # Inizializzazione
    # ------------------------------------------------------------------

    @staticmethod
    def initialize_sexuality(rng: random.Random) -> Sexuality:
        """Genera un orientamento iniziale.

        70% etichette standard (etero/omo/bi), 30% sfumature.
        """
        roll = rng.random()
        if roll < 0.70:
            # Distribuzione etichette
            choice = rng.choice(["androphilic", "gynephilic", "bisexual"])
            if choice == "androphilic":
                return Sexuality(
                    attraction_to_male=rng.uniform(0.75, 1.0),
                    attraction_to_female=rng.uniform(0.0, 0.20),
                    attraction_to_nonbinary=rng.uniform(0.0, 0.30),
                    romantic_vs_sexual=rng.uniform(0.3, 0.7),
                )
            if choice == "gynephilic":
                return Sexuality(
                    attraction_to_male=rng.uniform(0.0, 0.20),
                    attraction_to_female=rng.uniform(0.75, 1.0),
                    attraction_to_nonbinary=rng.uniform(0.0, 0.30),
                    romantic_vs_sexual=rng.uniform(0.3, 0.7),
                )
            return Sexuality(
                attraction_to_male=rng.uniform(0.5, 0.9),
                attraction_to_female=rng.uniform(0.5, 0.9),
                attraction_to_nonbinary=rng.uniform(0.3, 0.7),
                romantic_vs_sexual=rng.uniform(0.3, 0.7),
            )
        # Distribuzione continua
        return Sexuality(
            attraction_to_male=rng.random(),
            attraction_to_female=rng.random(),
            attraction_to_nonbinary=rng.random(),
            romantic_vs_sexual=rng.random(),
        )

    @staticmethod
    def initialize_sep(rng: random.Random, age_years: int) -> SEP:
        """SEP iniziale: dipende dall'età."""
        if age_years < 6:
            return SEP(
                knowledge=rng.uniform(0.0, 5.0),
                comfort=rng.uniform(0.3, 0.6),
                inhibition=rng.uniform(0.5, 0.8),
                received_at_age=None,
            )
        if age_years < 12:
            return SEP(
                knowledge=rng.uniform(5.0, 20.0),
                comfort=rng.uniform(0.3, 0.7),
                inhibition=rng.uniform(0.4, 0.7),
                received_at_age=None,
            )
        if age_years < 18:
            return SEP(
                knowledge=rng.uniform(20.0, 45.0),
                comfort=rng.uniform(0.4, 0.8),
                inhibition=rng.uniform(0.3, 0.6),
                received_at_age=rng.randint(10, 14),
            )
        # Adulto
        return SEP(
            knowledge=rng.uniform(40.0, 75.0),
            comfort=rng.uniform(0.5, 0.9),
            inhibition=rng.uniform(0.2, 0.6),
            received_at_age=rng.randint(10, 16),
        )

    @staticmethod
    def initialize_culture(
        rng: random.Random,
        tradition: CulturalTradition | None = None,
        *,
        parents: tuple[Character, Character] | None = None,
    ) -> CulturalProfile:
        """Cultura iniziale: da tradizione o eredità dai genitori."""
        if parents is not None:
            return IdentityService._inherit_culture(parents, rng)
        chosen = tradition or rng.choice(list(CulturalTradition))
        permiss, modesty, gender_strict, taboo = TRADITION_RANGES[chosen]
        # Jitter ±0.10
        return CulturalProfile(
            permissiveness=_jitter_clamp(permiss, rng, 0.10),
            modesty=_jitter_clamp(modesty, rng, 0.10),
            gender_role_strict=_jitter_clamp(gender_strict, rng, 0.10),
            reaction_to_taboo=taboo,
            tradition=chosen,
        )

    @staticmethod
    def _inherit_culture(
        parents: tuple[Character, Character],
        rng: random.Random,
    ) -> CulturalProfile:
        """Media pesata dei genitori + rumore."""
        profiles: list[CulturalProfile] = []
        for p in parents:
            data = (p.attributes_json or {}).get("cultural_profile")
            if isinstance(data, dict):
                profiles.append(CulturalProfile.from_dict(data))
        if not profiles:
            return IdentityService.initialize_culture(rng)
        if len(profiles) == 1:
            base = profiles[0]
        else:
            a, b = profiles
            base = CulturalProfile(
                permissiveness=(a.permissiveness + b.permissiveness) / 2.0,
                modesty=(a.modesty + b.modesty) / 2.0,
                gender_role_strict=(a.gender_role_strict + b.gender_role_strict) / 2.0,
                reaction_to_taboo=a.reaction_to_taboo,
                tradition=a.tradition,
            )
        # Jitter minore per l'eredità
        return CulturalProfile(
            permissiveness=_blend(
                base.permissiveness,
                rng.uniform(0.3, 0.7),
                CULTURE_INHERITANCE_WEIGHT,
            ),
            modesty=_blend(base.modesty, rng.uniform(0.3, 0.7), CULTURE_INHERITANCE_WEIGHT),
            gender_role_strict=_blend(
                base.gender_role_strict,
                rng.uniform(0.3, 0.7),
                CULTURE_INHERITANCE_WEIGHT,
            ),
            reaction_to_taboo=base.reaction_to_taboo,
            tradition=base.tradition,
        )

    @staticmethod
    def initialize(
        character: Character,
        rng: random.Random,
        *,
        age_years: int,
        parents: tuple[Character, Character] | None = None,
    ) -> IdentityProfile:
        """Inizializza il profilo identità completo di un character."""
        return IdentityProfile(
            sexuality=IdentityService.initialize_sexuality(rng),
            sep=IdentityService.initialize_sep(rng, age_years),
            culture=IdentityService.initialize_culture(rng, parents=parents),
        )

    @staticmethod
    def apply_to_character(
        character: Character,
        profile: IdentityProfile,
    ) -> None:
        """Scrive il profilo in `attributes_json` (side-effect)."""
        attrs = dict(character.attributes_json or {})
        attrs["sexuality"] = profile.sexuality.to_dict()
        attrs["sep"] = profile.sep.to_dict()
        attrs["cultural_profile"] = profile.culture.to_dict()
        character.attributes_json = attrs

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    @staticmethod
    def get_sexuality(character: Character) -> Sexuality:
        data = (character.attributes_json or {}).get("sexuality")
        return Sexuality.from_dict(data) if isinstance(data, dict) else Sexuality()

    @staticmethod
    def get_sep(character: Character) -> SEP:
        data = (character.attributes_json or {}).get("sep")
        return SEP.from_dict(data) if isinstance(data, dict) else SEP()

    @staticmethod
    def get_culture(character: Character) -> CulturalProfile:
        data = (character.attributes_json or {}).get("cultural_profile")
        return CulturalProfile.from_dict(data) if isinstance(data, dict) else CulturalProfile()

    @staticmethod
    def get_profile(character: Character) -> IdentityProfile:
        return IdentityProfile(
            sexuality=IdentityService.get_sexuality(character),
            sep=IdentityService.get_sep(character),
            culture=IdentityService.get_culture(character),
        )

    # ------------------------------------------------------------------
    # Drift / update
    # ------------------------------------------------------------------

    @staticmethod
    def apply_sexuality_drift(
        character: Character,
        rng: random.Random,
        *,
        age_years: int,
    ) -> bool:
        """Applica drift mensile alla sessualità. Ritorna True se applicato."""
        if age_years > FLUIDITY_MAX_AGE_YEARS:
            return False
        current = IdentityService.get_sexuality(character)
        jitter = {
            "male": rng.gauss(0.0, FLUIDITY_SIGMA),
            "female": rng.gauss(0.0, FLUIDITY_SIGMA),
            "nonbinary": rng.gauss(0.0, FLUIDITY_SIGMA),
            "romantic_vs_sexual": rng.gauss(0.0, FLUIDITY_SIGMA * 0.5),
        }
        new = current.with_drift(jitter)
        attrs = dict(character.attributes_json or {})
        attrs["sexuality"] = new.to_dict()
        character.attributes_json = attrs
        return True

    @staticmethod
    def add_sep_knowledge(character: Character, delta: float) -> SEP:
        sep = IdentityService.get_sep(character)
        new = sep.with_knowledge_delta(delta)
        attrs = dict(character.attributes_json or {})
        attrs["sep"] = new.to_dict()
        character.attributes_json = attrs
        return new

    @staticmethod
    def add_sep_comfort(character: Character, delta: float) -> SEP:
        sep = IdentityService.get_sep(character)
        new = sep.with_comfort_delta(delta)
        attrs = dict(character.attributes_json or {})
        attrs["sep"] = new.to_dict()
        character.attributes_json = attrs
        return new

    @staticmethod
    def add_sep_inhibition(character: Character, delta: float) -> SEP:
        sep = IdentityService.get_sep(character)
        new = sep.with_inhibition_delta(delta)
        attrs = dict(character.attributes_json or {})
        attrs["sep"] = new.to_dict()
        character.attributes_json = attrs
        return new


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _jitter_clamp(base: float, rng: random.Random, spread: float) -> float:
    return max(0.0, min(1.0, base + rng.uniform(-spread, spread)))


def _blend(base: float, noise: float, weight_base: float) -> float:
    """`weight_base × base + (1 - weight_base) × noise`, clampato."""
    v = weight_base * base + (1.0 - weight_base) * noise
    return max(0.0, min(1.0, v))


__all__ = [
    "CULTURE_INHERITANCE_WEIGHT",
    "FLUIDITY_MAX_AGE_YEARS",
    "FLUIDITY_SIGMA",
    "IdentityService",
]
