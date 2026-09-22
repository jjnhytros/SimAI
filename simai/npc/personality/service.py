"""PersonalityService — trait strength + valori dinamici.

Lo stato vive in `Character.attributes_json`:
  - `trait_strength`: `{trait_name: float in [0, 1]}`
  - `values`: `{value_axis: float in [0, 1]}`

`traits_json` (fonte per AI) è ricalcolato da `trait_strength`: contiene
i tratti con strength >= ACTIVE_THRESHOLD.
"""

from __future__ import annotations

from typing import Any

from simai.npc.ai.enums import ActionType
from simai.npc.background.enums import FormativeEventKind
from simai.npc.models import Character
from simai.npc.personality.enums import (
    ACTION_TRAIT_EFFECTS,
    ACTION_VALUE_EFFECTS,
    ACTIVE_THRESHOLD,
    CANDIDATE_INITIAL_STRENGTH,
    EVENT_SEVERITY_SCALE,
    EVENT_TRAIT_EFFECTS,
    EVENT_VALUE_EFFECTS,
    INITIAL_STRENGTH,
    INITIAL_VALUE,
    MAX_STRENGTH,
    MIN_STRENGTH,
    TRAIT_DECAY_PER_DAY,
    VALUE_MEAN_REVERSION,
    ValueAxis,
)
from simai.npc.traits.derivation import names_to_traits


class PersonalityService:
    """Servizio stateless per la personalità dinamica."""

    # ------------------------------------------------------------------
    # Load / init
    # ------------------------------------------------------------------

    @staticmethod
    def get_trait_strength(character: Character) -> dict[str, float]:
        """Mappa `{trait_name: strength}`. Inizializza se assente."""
        data = (character.attributes_json or {}).get("trait_strength")
        if isinstance(data, dict) and data:
            return {str(k): float(v) for k, v in data.items() if isinstance(v, (int, float))}
        # Fallback: init da traits_json
        current = names_to_traits(character.traits_json or [])
        return {t.value: INITIAL_STRENGTH for t in current}

    @staticmethod
    def get_values(character: Character) -> dict[ValueAxis, float]:
        """Mappa `{axis: value}`. Default 0.5 se assente."""
        data = (character.attributes_json or {}).get("values")
        result: dict[ValueAxis, float] = {}
        raw: dict[str, float] = {}
        if isinstance(data, dict):
            raw = {str(k): float(v) for k, v in data.items() if isinstance(v, (int, float))}
        for axis in ValueAxis:
            result[axis] = max(0.0, min(1.0, raw.get(axis.value, INITIAL_VALUE)))
        return result

    @staticmethod
    def initialize(character: Character) -> None:
        """Inizializza trait_strength e values (idempotente)."""
        attrs = dict(character.attributes_json or {})
        if "trait_strength" not in attrs:
            strength = PersonalityService.get_trait_strength(character)
            attrs["trait_strength"] = strength
        if "values" not in attrs:
            values = PersonalityService.get_values(character)
            attrs["values"] = {k.value: v for k, v in values.items()}
        character.attributes_json = attrs

    # ------------------------------------------------------------------
    # Active traits
    # ------------------------------------------------------------------

    @staticmethod
    def active_traits(trait_strength: dict[str, float]) -> list[str]:
        """Lista di trait (string) con strength >= ACTIVE_THRESHOLD."""
        active = sorted(name for name, s in trait_strength.items() if s >= ACTIVE_THRESHOLD)
        return active

    @staticmethod
    def sync_traits_json(character: Character) -> list[str]:
        """Ricalcola `traits_json` da `trait_strength`. Ritorna la nuova lista."""
        strength = PersonalityService.get_trait_strength(character)
        active = PersonalityService.active_traits(strength)
        character.traits_json = active
        return active

    # ------------------------------------------------------------------
    # Reinforce from action (pure in-memory)
    # ------------------------------------------------------------------

    @staticmethod
    def reinforce_inmemory(
        trait_strength: dict[str, float],
        values: dict[ValueAxis, float],
        action_type: ActionType,
    ) -> None:
        """Applica gli effetti di un'azione con rendimenti decrescenti."""
        trait_effects = ACTION_TRAIT_EFFECTS.get(action_type, {})
        for trait, delta in trait_effects.items():
            current = trait_strength.get(trait.value, 0.0)
            if current <= 0.0:
                trait_strength[trait.value] = CANDIDATE_INITIAL_STRENGTH + delta
            else:
                adjusted = delta * (1.0 - current)
                trait_strength[trait.value] = min(MAX_STRENGTH, current + adjusted)

        value_effects = ACTION_VALUE_EFFECTS.get(action_type, {})
        for axis, delta in value_effects.items():
            current = values.get(axis, INITIAL_VALUE)
            adjusted = delta * (1.0 - current) if delta > 0 else delta * current
            values[axis] = max(0.0, min(1.0, current + adjusted))

    @staticmethod
    def reinforce_character(character: Character, action_type: ActionType) -> None:
        """Wrapper su Character (load/save immediato)."""
        strength = PersonalityService.get_trait_strength(character)
        values = PersonalityService.get_values(character)
        PersonalityService.reinforce_inmemory(strength, values, action_type)
        PersonalityService._write(character, strength, values)

    # ------------------------------------------------------------------
    # Event effects
    # ------------------------------------------------------------------

    @staticmethod
    def apply_event_inmemory(
        trait_strength: dict[str, float],
        values: dict[ValueAxis, float],
        kind: FormativeEventKind,
        severity: float,
    ) -> None:
        """Applica gli effetti di un evento formativo con diminishing returns."""
        if not (0.0 <= severity <= 1.0):
            return
        # Values
        value_effects = EVENT_VALUE_EFFECTS.get(kind, {})
        for axis, delta in value_effects.items():
            scaled = delta * severity * EVENT_SEVERITY_SCALE
            current = values.get(axis, INITIAL_VALUE)
            adjusted = scaled * (1.0 - current) if scaled > 0 else scaled * current
            values[axis] = max(0.0, min(1.0, current + adjusted))

        # Traits
        trait_effects = EVENT_TRAIT_EFFECTS.get(kind, {})
        for trait, delta in trait_effects.items():
            scaled = delta * severity * EVENT_SEVERITY_SCALE
            current = trait_strength.get(trait.value, 0.0)
            if current <= 0.0 and scaled > 0:
                trait_strength[trait.value] = CANDIDATE_INITIAL_STRENGTH + scaled
            elif current > 0.0:
                adjusted = scaled * (1.0 - current) if scaled > 0 else scaled * current
                trait_strength[trait.value] = max(0.0, min(MAX_STRENGTH, current + adjusted))

    @staticmethod
    def apply_event(
        character: Character,
        kind: FormativeEventKind,
        severity: float,
    ) -> None:
        """Wrapper su Character (load/save immediato)."""
        strength = PersonalityService.get_trait_strength(character)
        values = PersonalityService.get_values(character)
        PersonalityService.apply_event_inmemory(strength, values, kind, severity)
        PersonalityService._write(character, strength, values)

    # ------------------------------------------------------------------
    # Decay (daily)
    # ------------------------------------------------------------------

    @staticmethod
    def decay_inmemory(
        trait_strength: dict[str, float],
        values: dict[ValueAxis, float],
    ) -> list[str]:
        """Decay giornaliero. Ritorna i tratti rimossi (sotto MIN)."""
        removed: list[str] = []
        for name in list(trait_strength.keys()):
            new_value = trait_strength[name] - TRAIT_DECAY_PER_DAY
            if new_value <= MIN_STRENGTH:
                del trait_strength[name]
                removed.append(name)
            else:
                trait_strength[name] = max(0.0, new_value)

        for axis in ValueAxis:
            current = values.get(axis, INITIAL_VALUE)
            values[axis] = current + (INITIAL_VALUE - current) * VALUE_MEAN_REVERSION

        return removed

    @staticmethod
    def decay_character(character: Character) -> list[str]:
        """Wrapper su Character."""
        strength = PersonalityService.get_trait_strength(character)
        values = PersonalityService.get_values(character)
        removed = PersonalityService.decay_inmemory(strength, values)
        PersonalityService._write(character, strength, values)
        if removed:
            PersonalityService.sync_traits_json(character)
        return removed

    # ------------------------------------------------------------------
    # Sync / write
    # ------------------------------------------------------------------

    @staticmethod
    def sync_from_state(
        character: Character,
        trait_strength: dict[str, float],
        values: dict[ValueAxis, float],
    ) -> None:
        """Scrive lo stato passato sul Character e ricalcola traits_json."""
        PersonalityService._write(character, trait_strength, values)
        character.traits_json = PersonalityService.active_traits(trait_strength)

    @staticmethod
    def _write(
        character: Character,
        trait_strength: dict[str, float],
        values: dict[ValueAxis, float],
    ) -> None:
        attrs = dict(character.attributes_json or {})
        attrs["trait_strength"] = {k: round(v, 4) for k, v in trait_strength.items()}
        attrs["values"] = {k.value: round(v, 4) for k, v in values.items()}
        character.attributes_json = attrs

    # ------------------------------------------------------------------
    # CLI helpers
    # ------------------------------------------------------------------

    @staticmethod
    def summary(character: Character) -> dict[str, Any]:
        """Riepilogo per CLI."""
        strength = PersonalityService.get_trait_strength(character)
        values = PersonalityService.get_values(character)
        active = PersonalityService.active_traits(strength)
        dormant = sorted(
            name for name, s in strength.items() if MIN_STRENGTH <= s < ACTIVE_THRESHOLD
        )
        return {
            "active": active,
            "dormant": dormant,
            "strength": strength,
            "values": {k.value: v for k, v in values.items()},
        }


__all__ = ["PersonalityService"]
