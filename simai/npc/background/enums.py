"""Enum e costanti del dominio background narrativo."""

from __future__ import annotations

from enum import StrEnum
from typing import Final


class FormativeEventKind(StrEnum):
    """Tipi di evento formativo."""

    PARENT_LOST = "PARENT_LOST"  # genitore morto in infanzia/adolescenza
    SIBLING_BORN = "SIBLING_BORN"  # nascita di un fratello
    BULLIED = "BULLIED"  # bullismo subito
    MOVED = "MOVED"  # trasloco importante
    FIRST_LOVE = "FIRST_LOVE"  # primo amore
    MENTORSHIP = "MENTORSHIP"  # incontro con mentore
    ILLNESS = "ILLNESS"  # malattia seria
    BETRAYAL = "BETRAYAL"  # tradimento da persona cara
    ACHIEVEMENT = "ACHIEVEMENT"  # successo importante
    TRAUMA = "TRAUMA"  # evento traumatico generico


#: Range di severity per ogni kind: (min, max).
SEVERITY_RANGES: Final[dict[FormativeEventKind, tuple[float, float]]] = {
    FormativeEventKind.PARENT_LOST: (0.70, 1.00),
    FormativeEventKind.SIBLING_BORN: (0.10, 0.30),
    FormativeEventKind.BULLIED: (0.30, 0.80),
    FormativeEventKind.MOVED: (0.20, 0.50),
    FormativeEventKind.FIRST_LOVE: (0.40, 0.70),
    FormativeEventKind.MENTORSHIP: (0.30, 0.60),
    FormativeEventKind.ILLNESS: (0.40, 0.90),
    FormativeEventKind.BETRAYAL: (0.50, 0.90),
    FormativeEventKind.ACHIEVEMENT: (0.30, 0.70),
    FormativeEventKind.TRAUMA: (0.60, 1.00),
}

#: Valence emotiva di default (-1..+1).
EVENT_VALENCE: Final[dict[FormativeEventKind, float]] = {
    FormativeEventKind.PARENT_LOST: -0.90,
    FormativeEventKind.SIBLING_BORN: +0.60,
    FormativeEventKind.BULLIED: -0.70,
    FormativeEventKind.MOVED: -0.20,
    FormativeEventKind.FIRST_LOVE: +0.80,
    FormativeEventKind.MENTORSHIP: +0.50,
    FormativeEventKind.ILLNESS: -0.60,
    FormativeEventKind.BETRAYAL: -0.80,
    FormativeEventKind.ACHIEVEMENT: +0.85,
    FormativeEventKind.TRAUMA: -0.95,
}

#: Testo descrittivo di default (per kind).
DEFAULT_TEXTS: Final[dict[FormativeEventKind, str]] = {
    FormativeEventKind.PARENT_LOST: "Perso un genitore",
    FormativeEventKind.SIBLING_BORN: "Nascita di un fratello o sorella",
    FormativeEventKind.BULLIED: "Preso di mira dai coetanei",
    FormativeEventKind.MOVED: "Trasferimento in una nuova casa",
    FormativeEventKind.FIRST_LOVE: "Prima esperienza romantica",
    FormativeEventKind.MENTORSHIP: "Incontrato un mentore importante",
    FormativeEventKind.ILLNESS: "Superata una malattia seria",
    FormativeEventKind.BETRAYAL: "Tradito da una persona cara",
    FormativeEventKind.ACHIEVEMENT: "Raggiunto un traguardo importante",
    FormativeEventKind.TRAUMA: "Vissuto un evento traumatico",
}

#: Soglia sopra cui viene creata una memoria dell'evento.
MEMORY_THRESHOLD: Final[float] = 0.50

#: Soglia di bullismo sopra cui viene forzato il tratto `TIMIDO`.
BULLY_TIMID_THRESHOLD: Final[float] = 0.60

#: Età massima (anni Anthalys) per considerare un evento "formativo".
MAX_FORMATIVE_AGE_YEARS: Final[int] = 25

#: Numero massimo di eventi formativi per NPC al seed.
MAX_SEED_EVENTS: Final[int] = 3


__all__ = [
    "BULLY_TIMID_THRESHOLD",
    "DEFAULT_TEXTS",
    "EVENT_VALENCE",
    "MAX_FORMATIVE_AGE_YEARS",
    "MAX_SEED_EVENTS",
    "MEMORY_THRESHOLD",
    "SEVERITY_RANGES",
    "FormativeEventKind",
]
