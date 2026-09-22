"""SocialAwarenessService — scoperta tratti + awareness culturale."""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from loguru import logger
from sqlalchemy.orm import Session

from simai.npc.identity import IdentityService
from simai.npc.identity.enums import CulturalTradition
from simai.npc.models import Character
from simai.npc.relationships.family_tree import FamilyTreeService
from simai.npc.social_awareness.enums import (
    CONFIDENCE_INCREMENT,
    CULTURAL_LEARN_INCREMENT,
    DISCOVERY_PROBABILITY,
    FAMILY_INITIAL_CONFIDENCE,
    INTENSITY_BY_LEVEL,
    KNOWN_THRESHOLD,
    MAX_CULTURAL_AWARENESS,
    OTHER_CULTURE_AWARENESS,
    OWN_CULTURE_AWARENESS,
    PARTIAL_THRESHOLD,
    TRAIT_VISIBILITY,
)
from simai.npc.traits.derivation import names_to_traits
from simai.npc.traits.enums import Trait


@dataclass(frozen=True, slots=True)
class TraitDiscoveryResult:
    """Esito di un tentativo di scoperta tratti."""

    observer_id: int
    target_id: int
    intensity: float
    newly_discovered: list[Trait] = field(default_factory=list)
    partially_advanced: list[Trait] = field(default_factory=list)


class SocialAwarenessService:
    """Servizio stateless di consapevolezza sociale."""

    # ------------------------------------------------------------------
    # Storage helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _get_known_map(observer: Character) -> dict[str, dict[str, float]]:
        """Ritorna il dict `{target_id_str: {trait_name: confidence}}`."""
        data = (observer.attributes_json or {}).get("known_traits")
        if isinstance(data, dict):
            return {str(k): dict(v) if isinstance(v, dict) else {} for k, v in data.items()}
        return {}

    @staticmethod
    def _write_known_map(observer: Character, mapping: dict[str, dict[str, float]]) -> None:
        attrs = dict(observer.attributes_json or {})
        attrs["known_traits"] = mapping
        observer.attributes_json = attrs

    @staticmethod
    def _get_cultural_map(observer: Character) -> dict[str, float]:
        data = (observer.attributes_json or {}).get("cultural_knowledge")
        if isinstance(data, dict):
            return {str(k): float(v) for k, v in data.items() if isinstance(v, (int, float))}
        return {}

    @staticmethod
    def _write_cultural_map(observer: Character, mapping: dict[str, float]) -> None:
        attrs = dict(observer.attributes_json or {})
        attrs["cultural_knowledge"] = mapping
        observer.attributes_json = attrs

    # ------------------------------------------------------------------
    # Query (public API)
    # ------------------------------------------------------------------

    @staticmethod
    def known_traits(
        observer: Character,
        target_id: int,
        *,
        threshold: float = KNOWN_THRESHOLD,
    ) -> dict[Trait, float]:
        """Ritorna i tratti noti (confidence >= threshold) di `target_id`."""
        mapping = SocialAwarenessService._get_known_map(observer)
        entry = mapping.get(str(target_id), {})
        result: dict[Trait, float] = {}
        for name, conf in entry.items():
            if conf < threshold:
                continue
            try:
                result[Trait(name)] = conf
            except ValueError:
                continue
        return result

    @staticmethod
    def partial_known_traits(
        observer: Character,
        target_id: int,
        *,
        min_threshold: float = PARTIAL_THRESHOLD,
    ) -> dict[Trait, float]:
        """Ritorna i tratti con confidence >= `min_threshold` (anche parziali)."""
        mapping = SocialAwarenessService._get_known_map(observer)
        entry = mapping.get(str(target_id), {})
        result: dict[Trait, float] = {}
        for name, conf in entry.items():
            if conf < min_threshold:
                continue
            try:
                result[Trait(name)] = conf
            except ValueError:
                continue
        return result

    @staticmethod
    def cultural_awareness(observer: Character, tradition: CulturalTradition) -> float:
        """Awareness [0, 1] della tradizione data."""
        mapping = SocialAwarenessService._get_cultural_map(observer)
        return mapping.get(tradition.value, 0.0)

    @staticmethod
    def all_cultural_awareness(
        observer: Character,
    ) -> dict[CulturalTradition, float]:
        """Awareness per tutte le tradizioni (default 0)."""
        mapping = SocialAwarenessService._get_cultural_map(observer)
        return {t: mapping.get(t.value, 0.0) for t in CulturalTradition}

    # ------------------------------------------------------------------
    # Init
    # ------------------------------------------------------------------

    @staticmethod
    def initialize_for(character: Character) -> None:
        """Inizializza awareness culturale (propria = 1.0, altre = 0.1)."""
        own = IdentityService.get_culture(character).tradition
        mapping: dict[str, float] = {}
        for t in CulturalTradition:
            mapping[t.value] = OWN_CULTURE_AWARENESS if t is own else OTHER_CULTURE_AWARENESS
        SocialAwarenessService._write_cultural_map(character, mapping)

    @staticmethod
    def initialize_family_knowledge(
        session: Session,
        child: Character,
        *,
        rng: random.Random,
    ) -> None:
        """I figli conoscono parzialmente i tratti VISIBILI dei genitori."""
        parents = FamilyTreeService.parents_of(session, child.id)
        if not parents:
            return
        mapping = SocialAwarenessService._get_known_map(child)
        for parent in parents:
            parent_traits = names_to_traits(parent.traits_json or [])
            entry = mapping.get(str(parent.id), {})
            for trait in parent_traits:
                visibility = TRAIT_VISIBILITY.get(trait)
                if visibility is None or visibility.value != "VISIBLE":
                    continue
                # confidence iniziale + rumore
                conf = FAMILY_INITIAL_CONFIDENCE + rng.uniform(-0.10, 0.10)
                conf = max(0.0, min(1.0, conf))
                entry[trait.value] = max(entry.get(trait.value, 0.0), conf)
            mapping[str(parent.id)] = entry
        SocialAwarenessService._write_known_map(child, mapping)

    # ------------------------------------------------------------------
    # Discovery via interaction
    # ------------------------------------------------------------------

    @staticmethod
    def record_interaction(
        observer: Character,
        target: Character,
        *,
        action_level: int,
        rng: random.Random,
    ) -> TraitDiscoveryResult:
        """Registra un'interazione e tenta la scoperta di tratti.

        Non tocca il DB: scrive su `observer.attributes_json`.
        """
        if observer.id == target.id:
            return TraitDiscoveryResult(observer.id, target.id, 0.0)

        intensity = INTENSITY_BY_LEVEL.get(action_level, 0.20)
        if intensity <= 0.0:
            return TraitDiscoveryResult(observer.id, target.id, 0.0)

        target_traits = names_to_traits(target.traits_json or [])
        if not target_traits:
            return TraitDiscoveryResult(observer.id, target.id, intensity)

        mapping = SocialAwarenessService._get_known_map(observer)
        entry = mapping.get(str(target.id), {})

        newly: list[Trait] = []
        advanced: list[Trait] = []

        for trait in target_traits:
            current = entry.get(trait.value, 0.0)
            if current >= KNOWN_THRESHOLD:
                continue

            visibility = TRAIT_VISIBILITY.get(trait)
            if visibility is None:
                continue
            base_prob = DISCOVERY_PROBABILITY.get(visibility, 0.05)
            prob = base_prob * intensity

            if rng.random() >= prob:
                continue

            increment = CONFIDENCE_INCREMENT * (0.5 + 0.5 * intensity)
            new_conf = min(KNOWN_THRESHOLD, current + increment)
            entry[trait.value] = new_conf

            if new_conf >= KNOWN_THRESHOLD:
                newly.append(trait)
            else:
                advanced.append(trait)

        mapping[str(target.id)] = entry
        SocialAwarenessService._write_known_map(observer, mapping)

        # Cultural learning
        SocialAwarenessService._maybe_learn_culture(observer, target)

        if newly:
            logger.debug(
                "Discovery: observer={} target={} nuovi tratti={}",
                observer.id,
                target.id,
                [t.value for t in newly],
            )

        return TraitDiscoveryResult(
            observer_id=observer.id,
            target_id=target.id,
            intensity=intensity,
            newly_discovered=newly,
            partially_advanced=advanced,
        )

    # ------------------------------------------------------------------
    # Cultural learning
    # ------------------------------------------------------------------

    @staticmethod
    def _maybe_learn_culture(observer: Character, target: Character) -> bool:
        """Impara la cultura del target se diversa. Ritorna True se appreso."""
        target_tradition = IdentityService.get_culture(target).tradition
        own_tradition = IdentityService.get_culture(observer).tradition
        if target_tradition is own_tradition:
            return False

        mapping = SocialAwarenessService._get_cultural_map(observer)
        current = mapping.get(target_tradition.value, 0.0)
        if current >= MAX_CULTURAL_AWARENESS:
            return False
        new = min(MAX_CULTURAL_AWARENESS, current + CULTURAL_LEARN_INCREMENT)
        mapping[target_tradition.value] = new
        SocialAwarenessService._write_cultural_map(observer, mapping)
        return True

    # ------------------------------------------------------------------
    # CLI helpers
    # ------------------------------------------------------------------

    @staticmethod
    def summary_for(observer: Character, target_id: int) -> dict[str, object]:
        """Riepilogo per CLI: tratti noti + parziali."""
        known = SocialAwarenessService.known_traits(observer, target_id)
        partial = SocialAwarenessService.partial_known_traits(observer, target_id)
        partial_only = {k.value: v for k, v in partial.items() if k not in known}
        return {
            "known": {t.value: c for t, c in known.items()},
            "partial": partial_only,
            "known_count": len(known),
            "partial_count": len(partial_only),
        }


__all__ = ["SocialAwarenessService", "TraitDiscoveryResult"]
