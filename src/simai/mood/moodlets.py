from dataclasses import dataclass

from sqlalchemy import delete, select
from sqlalchemy.engine import CursorResult
from sqlalchemy.orm import Session

from simai.actions.enums import ActionKind
from simai.mood.enums import MoodletKind
from simai.mood.models import Moodlet
from simai.world.models import Character

LONELY_THRESHOLD = 20.0
LONELY_STREAK_TRIGGER = 3


@dataclass(frozen=True)
class MoodletSpec:
    kind: MoodletKind
    duration_ticks: int
    delta_per_tick: float


SPECS: dict[MoodletKind, MoodletSpec] = {
    MoodletKind.ATE_WELL: MoodletSpec(
        kind=MoodletKind.ATE_WELL,
        duration_ticks=4,
        delta_per_tick=+2.0,
    ),
    MoodletKind.SOCIALIZED: MoodletSpec(
        kind=MoodletKind.SOCIALIZED,
        duration_ticks=4,
        delta_per_tick=+2.0,
    ),
    MoodletKind.LONELY: MoodletSpec(
        kind=MoodletKind.LONELY,
        duration_ticks=6,
        delta_per_tick=-3.0,
    ),
}


def _active(session: Session, character_id: int, kind: MoodletKind) -> Moodlet | None:
    return session.scalar(
        select(Moodlet).where(
            Moodlet.character_id == character_id,
            Moodlet.kind == kind,
        )
    )


def apply_moodlet(session: Session, character_id: int, kind: MoodletKind, tick: int) -> Moodlet:
    """Applica o rinfresca un moodlet.

    Rinfrescare significa: se esiste già un moodlet dello stesso tipo,
    ne sposto la scadenza a `tick + duration`, non sommo. Un solo
    moodlet per tipo per personaggio.
    """
    spec = SPECS[kind]
    existing = _active(session, character_id, kind)
    expires = tick + spec.duration_ticks
    if existing is not None:
        existing.started_at_tick = tick
        existing.expires_at_tick = expires
        return existing
    fresh = Moodlet(
        character_id=character_id,
        kind=kind,
        started_at_tick=tick,
        expires_at_tick=expires,
    )
    session.add(fresh)
    return fresh


def active_delta(session: Session, character_id: int, tick: int) -> float:
    """Somma i delta_per_tick dei moodlet attivi al tick corrente."""
    moodlets = session.scalars(
        select(Moodlet).where(
            Moodlet.character_id == character_id,
            Moodlet.started_at_tick < tick,
            Moodlet.expires_at_tick >= tick,
        )
    ).all()
    return sum(SPECS[m.kind].delta_per_tick for m in moodlets)


def cleanup_expired(session: Session, character_id: int, tick: int) -> int:
    """Rimuove i moodlet la cui `expires_at_tick` è < tick."""
    result = session.execute(
        delete(Moodlet).where(
            Moodlet.character_id == character_id,
            Moodlet.expires_at_tick < tick,
        )
    )
    assert isinstance(result, CursorResult)
    return int(result.rowcount or 0)


def moodlets_for_action(action: ActionKind) -> MoodletKind | None:
    if action == ActionKind.EAT:
        return MoodletKind.ATE_WELL
    if action == ActionKind.SOCIALIZE:
        return MoodletKind.SOCIALIZED
    return None


def update_lonely_streak(session: Session, character_id: int, intimacy: float) -> int:
    """Aggiorna lo streak di intimacy bassa e ritorna il valore corrente."""
    char = session.get(Character, character_id)
    if char is None:
        return 0
    if intimacy < LONELY_THRESHOLD:
        char.low_intimacy_streak += 1
    else:
        char.low_intimacy_streak = 0
    return char.low_intimacy_streak
