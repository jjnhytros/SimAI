"""Enum del dominio intimità."""

from enum import StrEnum


class IntimacyAction(StrEnum):
    """Azioni di intimità (emotive, fisiche, sostitutive, digitali)."""

    # --- Confidenza (esistenti) ---
    CONFIDE = "CONFIDE"
    SHARE_MOMENT = "SHARE_MOMENT"
    INTIMATE_TALK = "INTIMATE_TALK"

    # --- Romantiche (esistenti) ---
    ROMANTIC_GESTURE = "ROMANTIC_GESTURE"
    KISS = "KISS"
    INTIMATE_ENCOUNTER = "INTIMATE_ENCOUNTER"

    # --- Sostitutive (Chunk 3.7b) ---
    HOLD_HANDS = "HOLD_HANDS"
    CUDDLE = "CUDDLE"
    DEEP_TALK = "DEEP_TALK"
    SHARE_MEAL = "SHARE_MEAL"

    # --- Digitali (Chunk 3.7b) ---
    TEXT_MESSAGE = "TEXT_MESSAGE"
    VIRTUAL_CALL = "VIRTUAL_CALL"


class IntimacyOutcome(StrEnum):
    """Esito di un'azione di intimità."""

    SUCCESS = "SUCCESS"
    REJECTED = "REJECTED"
    NOT_ELIGIBLE = "NOT_ELIGIBLE"


__all__ = ["IntimacyAction", "IntimacyOutcome"]
