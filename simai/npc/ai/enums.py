"""Enum del dominio AI."""

from enum import StrEnum


class ActionType(StrEnum):
    """Tipi di azione che un NPC può eseguire."""

    EAT = "EAT"
    DRINK = "DRINK"
    USE_TOILET = "USE_TOILET"
    SLEEP = "SLEEP"
    NAP = "NAP"
    SHOWER = "SHOWER"
    SOCIALIZE = "SOCIALIZE"
    RELAX = "RELAX"

    # --- Training actions (Chunk 3.6b) ---
    PRACTICE_COMBAT = "PRACTICE_COMBAT"
    STUDY = "STUDY"
    PRACTICE_ART = "PRACTICE_ART"
    COOK = "COOK"

    # --- Training actions per skill dei job (Chunk 3.6d) ---
    PRACTICE_CRAFT = "PRACTICE_CRAFT"
    PRACTICE_TRADE = "PRACTICE_TRADE"
    PRACTICE_SERVICE = "PRACTICE_SERVICE"

    # --- Addiction actions (Chunk 3.6b) ---
    CONSUME_ALCOHOL = "CONSUME_ALCOHOL"
    SMOKE = "SMOKE"
    GAMBLE = "GAMBLE"
    DRINK_COFFEE = "DRINK_COFFEE"

    # --- Bisogni avanzati (Chunk 3.7a) ---
    BE_ALONE = "BE_ALONE"
    SELF_CARE = "SELF_CARE"


__all__ = ["ActionType"]
