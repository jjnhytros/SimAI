from sqlalchemy.orm import Session

from simai.needs.enums import NeedKind
from simai.needs.service import needs_of
from simai.world.models import Character

MOOD_WEIGHTS: dict[NeedKind, float] = {
    NeedKind.HUNGER: 0.25,
    NeedKind.THIRST: 0.20,
    NeedKind.FUN: 0.30,
    NeedKind.INTIMACY: 0.25,
}

MOOD_MIN = 0.0
MOOD_MAX = 100.0


def compute_mood(needs: dict[NeedKind, float]) -> float:
    """Media pesata dei bisogni. Bisogni mancanti valgono 0."""
    total = 0.0
    for kind, weight in MOOD_WEIGHTS.items():
        total += needs.get(kind, 0.0) * weight
    return max(MOOD_MIN, min(MOOD_MAX, total))


def update_mood(session: Session, character_id: int) -> float:
    """Ricalcola il mood del personaggio e lo persiste."""
    char = session.get(Character, character_id)
    if char is None:
        return 0.0
    needs = needs_of(session, character_id)
    mood = compute_mood(needs)
    char.mood = mood
    return mood


def mood_label(mood: float) -> str:
    """Etichetta qualitativa, per output CLI e futuro UI."""
    if mood >= 80:
        return "sereno"
    if mood >= 60:
        return "tranquillo"
    if mood >= 40:
        return "così così"
    if mood >= 20:
        return "giù"
    return "a terra"
