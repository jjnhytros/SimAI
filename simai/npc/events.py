"""Costanti event type per il dominio NPC."""

from typing import Final

# --- Azioni / bisogni / mood ---
EVENT_NPC_ACTION_STARTED: Final[str] = "npc.action.started"
EVENT_NPC_ACTION_COMPLETED: Final[str] = "npc.action.completed"
EVENT_NPC_NEED_CRITICAL: Final[str] = "npc.need.critical"
EVENT_NPC_MOOD_CHANGED: Final[str] = "npc.mood.changed"

# --- Ciclo vita ---
EVENT_NPC_BORN: Final[str] = "npc.born"
EVENT_NPC_DIED: Final[str] = "npc.died"
EVENT_NPC_LIFESTAGE_CHANGED: Final[str] = "npc.lifestage.changed"
EVENT_PREGNANCY_CONCEIVED: Final[str] = "pregnancy.conceived"
EVENT_PREGNANCY_COMPLETED: Final[str] = "pregnancy.completed"

# --- Memoria / Intimità (Chunk 3.2c) ---
EVENT_MEMORY_RECORDED: Final[str] = "memory.recorded"
EVENT_INTIMACY_PERFORMED: Final[str] = "intimacy.performed"
EVENT_INTIMACY_REJECTED: Final[str] = "intimacy.rejected"

# --- Famiglia attiva (Chunk 3.4b) ---
EVENT_FAMILY_CONCEPTION_ATTEMPT: Final[str] = "family.conception_attempt"
EVENT_FAMILY_ORPHAN_REGISTERED: Final[str] = "family.orphan_registered"
EVENT_FAMILY_GUARDIAN_ASSIGNED: Final[str] = "family.guardian_assigned"

# --- Transport / Transit (Chunk 4.10b) ---
EVENT_NPC_ARRIVED: Final[str] = "npc.arrived"

__all__ = [
    "EVENT_FAMILY_CONCEPTION_ATTEMPT",
    "EVENT_FAMILY_GUARDIAN_ASSIGNED",
    "EVENT_FAMILY_ORPHAN_REGISTERED",
    "EVENT_INTIMACY_PERFORMED",
    "EVENT_INTIMACY_REJECTED",
    "EVENT_MEMORY_RECORDED",
    "EVENT_NPC_ACTION_COMPLETED",
    "EVENT_NPC_ACTION_STARTED",
    "EVENT_NPC_ARRIVED",
    "EVENT_NPC_BORN",
    "EVENT_NPC_DIED",
    "EVENT_NPC_LIFESTAGE_CHANGED",
    "EVENT_NPC_MOOD_CHANGED",
    "EVENT_NPC_NEED_CRITICAL",
    "EVENT_PREGNANCY_COMPLETED",
    "EVENT_PREGNANCY_CONCEIVED",
]
