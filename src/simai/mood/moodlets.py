from dataclasses import dataclass

from sqlalchemy import delete, select
from sqlalchemy.engine import CursorResult
from sqlalchemy.orm import Session

from simai.actions.enums import ActionKind
from simai.mood.enums import MoodletKind
from simai.mood.models import Moodlet
from simai.needs.enums import NeedKind
from simai.world.models import Character

LONELY_THRESHOLD = 20.0
LONELY_STREAK_TRIGGER = 3

# Durata dei moodlet need-based: un giorno Anthalys. Il moodlet viene
# rinfrescato periodicamente, non ad ogni tick (vedi
# refresh_need_moodlets_many). Hardcoded per evitare dipendenza
# mood→economy; allineare a TICKS_PER_DAY se cambia il calendario.
NEED_MOODLET_DURATION = 28
REFRESH_THRESHOLD_TICKS = NEED_MOODLET_DURATION // 2  # 14


@dataclass(frozen=True)
class MoodletSpec:
    kind: MoodletKind
    duration_ticks: int
    delta_per_tick: float


SPECS: dict[MoodletKind, MoodletSpec] = {
    MoodletKind.ADORED: MoodletSpec(MoodletKind.ADORED, NEED_MOODLET_DURATION, +0.5),
    MoodletKind.ATE_WELL: MoodletSpec(
        kind=MoodletKind.ATE_WELL,
        duration_ticks=4,
        delta_per_tick=+2.0,
    ),
    MoodletKind.BECAME_CHILD: MoodletSpec(MoodletKind.BECAME_CHILD, 10, +0.5),
    MoodletKind.BECAME_SENIOR: MoodletSpec(MoodletKind.BECAME_SENIOR, 10, +0.5),
    MoodletKind.BECAME_YOUNG_ADULT: MoodletSpec(MoodletKind.BECAME_YOUNG_ADULT, 10, +0.5),
    MoodletKind.BLISSFUL: MoodletSpec(MoodletKind.BLISSFUL, NEED_MOODLET_DURATION, +0.5),
    MoodletKind.BORED: MoodletSpec(MoodletKind.BORED, NEED_MOODLET_DURATION, -5.0),
    MoodletKind.CLOSE: MoodletSpec(MoodletKind.CLOSE, NEED_MOODLET_DURATION, +0.5),
    MoodletKind.CONNECTED: MoodletSpec(MoodletKind.CONNECTED, NEED_MOODLET_DURATION, +0.5),
    MoodletKind.CONTENT: MoodletSpec(MoodletKind.CONTENT, NEED_MOODLET_DURATION, +0.5),
    MoodletKind.DEHYDRATED: MoodletSpec(MoodletKind.DEHYDRATED, NEED_MOODLET_DURATION, -15.0),
    MoodletKind.DEVOTED: MoodletSpec(MoodletKind.DEVOTED, 2, +1.0),
    MoodletKind.ENTERTAINED: MoodletSpec(MoodletKind.ENTERTAINED, NEED_MOODLET_DURATION, +0.5),
    MoodletKind.HUNGRY: MoodletSpec(MoodletKind.HUNGRY, NEED_MOODLET_DURATION, -6.0),
    MoodletKind.HYDRATED: MoodletSpec(MoodletKind.HYDRATED, NEED_MOODLET_DURATION, +0.5),
    MoodletKind.INTIMATE: MoodletSpec(MoodletKind.INTIMATE, NEED_MOODLET_DURATION, +0.5),
    MoodletKind.LONELY: MoodletSpec(
        kind=MoodletKind.LONELY,
        duration_ticks=6,
        delta_per_tick=-3.0,
    ),
    MoodletKind.MISERABLE: MoodletSpec(MoodletKind.MISERABLE, NEED_MOODLET_DURATION, -12.0),
    MoodletKind.OVERHYDRATED: MoodletSpec(MoodletKind.OVERHYDRATED, NEED_MOODLET_DURATION, +0.5),
    MoodletKind.REFRESHED: MoodletSpec(MoodletKind.REFRESHED, NEED_MOODLET_DURATION, +0.5),
    MoodletKind.ROMANTIC: MoodletSpec(MoodletKind.ROMANTIC, 2, +0.5),
    MoodletKind.SATISFIED: MoodletSpec(MoodletKind.SATISFIED, NEED_MOODLET_DURATION, +0.5),
    MoodletKind.SOCIALIZED: MoodletSpec(
        kind=MoodletKind.SOCIALIZED,
        duration_ticks=4,
        delta_per_tick=+2.0,
    ),
    MoodletKind.STARVING: MoodletSpec(MoodletKind.STARVING, NEED_MOODLET_DURATION, -15.0),
    MoodletKind.STUFFED: MoodletSpec(MoodletKind.STUFFED, NEED_MOODLET_DURATION, +0.5),
    MoodletKind.THIRSTY: MoodletSpec(MoodletKind.THIRSTY, NEED_MOODLET_DURATION, -6.0),
    MoodletKind.WELL_FED: MoodletSpec(MoodletKind.WELL_FED, NEED_MOODLET_DURATION, +0.5),
}


NEED_MOODLETS: dict[NeedKind, tuple[MoodletKind, ...]] = {
    NeedKind.HUNGER: (
        MoodletKind.STARVING,
        MoodletKind.HUNGRY,
        MoodletKind.SATISFIED,
        MoodletKind.WELL_FED,
        MoodletKind.STUFFED,
    ),
    NeedKind.THIRST: (
        MoodletKind.DEHYDRATED,
        MoodletKind.THIRSTY,
        MoodletKind.HYDRATED,
        MoodletKind.REFRESHED,
        MoodletKind.OVERHYDRATED,
    ),
    NeedKind.FUN: (
        MoodletKind.MISERABLE,
        MoodletKind.BORED,
        MoodletKind.CONTENT,
        MoodletKind.ENTERTAINED,
        MoodletKind.BLISSFUL,
    ),
    NeedKind.INTIMACY: (
        MoodletKind.INTIMATE,
        MoodletKind.CONNECTED,
        MoodletKind.CLOSE,
        MoodletKind.ADORED,
    ),
}


_NEED_MOODLET_THRESHOLDS: dict[NeedKind, tuple[tuple[float, MoodletKind | None], ...]] = {
    NeedKind.HUNGER: (
        (10.0, MoodletKind.STARVING),
        (30.0, MoodletKind.HUNGRY),
        (70.0, MoodletKind.SATISFIED),
        (90.0, MoodletKind.WELL_FED),
        (100.0, MoodletKind.STUFFED),
    ),
    NeedKind.THIRST: (
        (10.0, MoodletKind.DEHYDRATED),
        (40.0, MoodletKind.THIRSTY),
        (70.0, MoodletKind.HYDRATED),
        (90.0, MoodletKind.REFRESHED),
        (100.0, MoodletKind.OVERHYDRATED),
    ),
    NeedKind.FUN: (
        (10.0, MoodletKind.MISERABLE),
        (40.0, MoodletKind.BORED),
        (70.0, MoodletKind.CONTENT),
        (90.0, MoodletKind.ENTERTAINED),
        (100.0, MoodletKind.BLISSFUL),
    ),
    NeedKind.INTIMACY: (
        (LONELY_THRESHOLD, None),
        (50.0, MoodletKind.INTIMATE),
        (70.0, MoodletKind.CONNECTED),
        (90.0, MoodletKind.CLOSE),
        (100.0, MoodletKind.ADORED),
    ),
}


def moodlet_for_need(need: NeedKind, value: float) -> MoodletKind | None:
    """Moodlet per lo stato del need. Pura, deterministica.

    `None` per INTIMACY sotto `LONELY_THRESHOLD`: quello stato è coperto
    da LONELY, applicato in tick.py via streak.
    """
    thresholds = _NEED_MOODLET_THRESHOLDS.get(need)
    if thresholds is None:
        return None
    for upper, kind in thresholds:
        if value < upper:
            return kind
    return thresholds[-1][1]


def _active(session: Session, character_id: int, kind: MoodletKind) -> Moodlet | None:
    return session.scalar(
        select(Moodlet).where(
            Moodlet.character_id == character_id,
            Moodlet.kind == kind,
        )
    )


def apply_moodlet(session: Session, character_id: int, kind: MoodletKind, tick: int) -> Moodlet:
    """Applica o rinfresca un moodlet (non need-based).

    Rinfrescare significa: se esiste già un moodlet dello stesso tipo,
    ne sposto la scadenza a `tick + duration`, non sommo. Un solo
    moodlet per tipo per personaggio.

    Per i moodlet need-based si usa `refresh_need_moodlets_many`, che
    aggiorna `need` e gestisce la transizione senza DELETE+INSERT.
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
        need=None,
        started_at_tick=tick,
        expires_at_tick=expires,
    )
    session.add(fresh)
    return fresh


def refresh_need_moodlets_many(
    session: Session,
    needs_by_char: dict[int, dict[NeedKind, float]],
    tick: int,
) -> None:
    """Allinea i moodlet-need allo stato corrente dei bisogni, in batch.

    - 1 SELECT per tutti i char in `needs_by_char`.
    - Stato invariato e lontano dalla scadenza: nessuna scrittura.
    - Stato invariato e vicino alla scadenza (≤ REFRESH_THRESHOLD_TICKS):
      UPDATE (refresh in-place).
    - Stato cambiato: UPDATE del `kind` (grazie a `need` popolato),
      non DELETE+INSERT.
    - `desired=None` (INTIMACY bassa, coperta da LONELY): DELETE.

    Non tocca LONELY, ATE_WELL, SOCIALIZED, BECAME_* (hanno
    `need = None`).
    """
    if not needs_by_char:
        return
    char_ids = list(needs_by_char.keys())
    active = session.scalars(
        select(Moodlet).where(
            Moodlet.character_id.in_(char_ids),
            Moodlet.need.isnot(None),
            Moodlet.expires_at_tick > tick,
        )
    ).all()
    active_by_key: dict[tuple[int, NeedKind], Moodlet] = {}
    for moodlet in active:
        assert moodlet.need is not None
        active_by_key[(moodlet.character_id, moodlet.need)] = moodlet
    for char_id, needs in needs_by_char.items():
        for need, value in needs.items():
            desired = moodlet_for_need(need, value)
            current = active_by_key.get((char_id, need))
            if current is not None and current.kind == desired:
                if current.expires_at_tick - tick <= REFRESH_THRESHOLD_TICKS:
                    spec = SPECS[current.kind]
                    current.started_at_tick = tick
                    current.expires_at_tick = tick + spec.duration_ticks
                continue
            if current is not None:
                if desired is None:
                    session.delete(current)
                else:
                    spec = SPECS[desired]
                    current.kind = desired
                    current.started_at_tick = tick
                    current.expires_at_tick = tick + spec.duration_ticks
                continue
            if desired is not None:
                spec = SPECS[desired]
                session.add(
                    Moodlet(
                        character_id=char_id,
                        kind=desired,
                        need=need,
                        started_at_tick=tick,
                        expires_at_tick=tick + spec.duration_ticks,
                    )
                )


def active_delta(session: Session, character_id: int, tick: int) -> float:
    """Somma i delta_per_tick dei moodlet attivi al tick corrente.

    Finestra: `[started_at_tick, expires_at_tick)` — il moodlet
    contribuisce dal tick in cui è applicato fino al tick prima della
    scadenza.
    """
    moodlets = session.scalars(
        select(Moodlet).where(
            Moodlet.character_id == character_id,
            Moodlet.started_at_tick <= tick,
            Moodlet.expires_at_tick > tick,
        )
    ).all()
    return sum(SPECS[m.kind].delta_per_tick for m in moodlets)


def cleanup_expired(session: Session, character_id: int, tick: int) -> int:
    """Rimuove i moodlet la cui `expires_at_tick` è <= tick."""
    result = session.execute(
        delete(Moodlet).where(
            Moodlet.character_id == character_id,
            Moodlet.expires_at_tick <= tick,
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


def active_delta_many(
    session: Session,
    char_ids: list[int],
    tick: int,
) -> dict[int, float]:
    """Somma i `delta_per_tick` dei moodlet attivi, per tutti i char.

    1 SELECT invece di N. Stessa finestra `[started_at, expires_at)`.
    """
    if not char_ids:
        return {}
    moodlets = session.scalars(
        select(Moodlet).where(
            Moodlet.character_id.in_(char_ids),
            Moodlet.started_at_tick <= tick,
            Moodlet.expires_at_tick > tick,
        )
    ).all()
    result: dict[int, float] = {cid: 0.0 for cid in char_ids}
    for m in moodlets:
        result[m.character_id] += SPECS[m.kind].delta_per_tick
    return result


def cleanup_expired_many(
    session: Session,
    char_ids: list[int],
    tick: int,
) -> int:
    """Rimuove i moodlet scaduti per tutti i char, 1 DELETE."""
    if not char_ids:
        return 0
    result = session.execute(
        delete(Moodlet).where(
            Moodlet.character_id.in_(char_ids),
            Moodlet.expires_at_tick <= tick,
        )
    )
    assert isinstance(result, CursorResult)
    return int(result.rowcount or 0)
