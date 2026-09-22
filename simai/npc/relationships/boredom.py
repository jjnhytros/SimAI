"""BoredomService — noia relazionale e freshness."""

from __future__ import annotations

from typing import Final

from sqlalchemy.orm import Session

from simai.config.anthalys import SECONDS_PER_DAY
from simai.core.anthalys_datetime import AnthalysDateTime
from simai.npc.relationships.models import Relationship

#: Incremento giornaliero di boredom se la relazione è stabile.
DAILY_BOREDOM_GROWTH: Final[float] = 0.005

#: Decremento quando arriva un'azione "nuova".
NOVELTY_REDUCTION: Final[float] = 0.05

#: Decremento quando arriva un'azione "conosciuta" ma recente.
FAMILIAR_REDUCTION: Final[float] = 0.015

#: Soglia sopra cui scatta warning.
WARNING_THRESHOLD: Final[float] = 0.70

#: Soglia sopra cui la relazione è "stale" (a rischio).
STALE_THRESHOLD: Final[float] = 0.90

#: Finestra (giorni) oltre cui una ripetizione è considerata "nuova" di nuovo.
NOVELTY_WINDOW_DAYS: Final[int] = 15


class BoredomService:
    """Servizio stateless per il tracking della noia relazionale."""

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    @staticmethod
    def get_boredom(rel: Relationship) -> float:
        md = rel.metadata_json or {}
        try:
            return max(0.0, min(1.0, float(md.get("boredom", 0.0))))
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def is_stale(rel: Relationship) -> bool:
        return BoredomService.get_boredom(rel) >= STALE_THRESHOLD

    @staticmethod
    def is_warning(rel: Relationship) -> bool:
        b = BoredomService.get_boredom(rel)
        return WARNING_THRESHOLD <= b < STALE_THRESHOLD

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    @staticmethod
    def tick_daily(
        session: Session,
        rel: Relationship,
        *,
        strength: float,
    ) -> float:
        """Applica un giorno di crescita boredom. Ritorna il nuovo valore.

        Cresce solo se la relazione è stabile (strength >= 0.5).
        """
        if strength < 0.5:
            return BoredomService.get_boredom(rel)

        md = dict(rel.metadata_json or {})
        current = BoredomService.get_boredom(rel)
        new_value = min(1.0, current + DAILY_BOREDOM_GROWTH)
        md["boredom"] = new_value
        rel.metadata_json = md
        session.flush()
        return new_value

    @staticmethod
    def register_action(
        rel: Relationship,
        *,
        action_value: str,
        current_dt: AnthalysDateTime,
    ) -> float:
        """Registra un'azione: riduce boredom se nuova o non recente.

        Ritorna il nuovo valore di boredom.
        """
        md = dict(rel.metadata_json or {})
        seen: list[str] = list(md.get("actions_seen", []))
        last_novelty = int(md.get("last_novelty_at", 0))
        current_secs = current_dt.to_total_seconds()

        days_since = (current_secs - last_novelty) / SECONDS_PER_DAY
        is_new = action_value not in seen
        is_fresh_repeat = days_since >= NOVELTY_WINDOW_DAYS

        current = BoredomService.get_boredom(rel)
        if is_new:
            current = max(0.0, current - NOVELTY_REDUCTION)
            seen.append(action_value)
            md["last_novelty_at"] = current_secs
        elif is_fresh_repeat:
            current = max(0.0, current - NOVELTY_REDUCTION * 0.7)
            md["last_novelty_at"] = current_secs
        else:
            current = max(0.0, current - FAMILIAR_REDUCTION)

        md["boredom"] = current
        md["actions_seen"] = seen[-50:]  # cap
        rel.metadata_json = md
        return current

    @staticmethod
    def force_set(rel: Relationship, value: float) -> None:
        """Imposta boredom a un valore specifico (dev tool)."""
        md = dict(rel.metadata_json or {})
        md["boredom"] = max(0.0, min(1.0, value))
        rel.metadata_json = md


__all__ = [
    "DAILY_BOREDOM_GROWTH",
    "FAMILIAR_REDUCTION",
    "NOVELTY_REDUCTION",
    "NOVELTY_WINDOW_DAYS",
    "STALE_THRESHOLD",
    "WARNING_THRESHOLD",
    "BoredomService",
]
