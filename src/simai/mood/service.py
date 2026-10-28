from sqlalchemy.orm import Session

from simai.mood.moodlets import active_delta
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


def compute_mood(needs: dict[NeedKind, float], moodlet_delta: float = 0.0) -> float:
    total = 0.0
    for kind, weight in MOOD_WEIGHTS.items():
        total += needs.get(kind, 0.0) * weight
    return max(MOOD_MIN, min(MOOD_MAX, total + moodlet_delta))


def update_mood(
    session: Session,
    character_id: int,
    tick: int | None = None,
    needs: dict[NeedKind, float] | None = None,
) -> float:
    """Ricalcola il mood applicando i moodlet attivi al tick.

    Se `tick` è None, i moodlet non contribuiscono (utile per test o
    contesti senza contesto temporale). Se `needs` è passato, evita la
    query interna: utile in `run_tick`, dove i bisogni sono già
    calcolati.
    """
    char = session.get(Character, character_id)
    if char is None:
        return 0.0
    if needs is None:
        needs = needs_of(session, character_id)
    delta = active_delta(session, character_id, tick) if tick is not None else 0.0
    mood = compute_mood(needs, delta)
    char.mood = mood
    return mood


def mood_label(mood: float) -> str:
    if mood >= 80:
        return "sereno"
    if mood >= 60:
        return "tranquillo"
    if mood >= 40:
        return "così così"
    if mood >= 20:
        return "giù"
    return "a terra"
