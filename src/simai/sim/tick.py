from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.economy.payday import process_payday
from simai.mood.enums import MoodletKind
from simai.mood.moodlets import (
    LONELY_STREAK_TRIGGER,
    active_delta_many,
    apply_moodlet,
    cleanup_expired_many,
    refresh_need_moodlets_many,
    update_lonely_streak,
)
from simai.mood.service import update_mood
from simai.needs.enums import NeedKind
from simai.needs.service import apply_decay, needs_of_many
from simai.npc.intimacy.service import apply_intimacy_moodlets_many
from simai.npc.manager import NPCManager, NPCManagerLike
from simai.sim.daily import daily_tick
from simai.sim.reports import TickDecision, TickReport
from simai.sim.state import get_state
from simai.world.models import Character

__all__ = ["TickDecision", "TickReport", "run_tick"]


def run_tick(
    session: Session,
    *,
    minutes: int,
    tick_index: int | None = None,
    master_seed: int | None = None,
    include_player: bool = False,
    npc_manager: NPCManagerLike | None = None,
) -> TickReport:
    """Avanza la simulazione di `minutes`.

    Ordine interno:
      1. payday (fine turno, richiede presenza)
      2. apply_decay (modulato dai tratti)
      3. NPCManager.load → NPCManager.update_all (priorità lavoro →
         priorità casa → choose_intent → esegui)
      4. moodlet (streak, LONELY, need, mood, cleanup)
    """
    if minutes <= 0:
        raise ValueError(f"minutes must be > 0, got {minutes}")

    if tick_index is None or master_seed is None:
        state = get_state(session)
        if tick_index is None:
            tick_index = state.tick_index
            state.tick_index += 1
        if master_seed is None:
            master_seed = state.master_seed

    if tick_index < 0:
        raise ValueError(f"tick_index must be >= 0, got {tick_index}")

    kills, _deliveries = daily_tick(session, tick_index)

    payday_report = process_payday(session, tick_index)

    all_characters = session.scalars(select(Character).order_by(Character.id)).all()

    # Fase 1: decadimento con tratti.
    for char in all_characters:
        apply_decay(
            session,
            char.id,
            minutes,
            traits=list(char.traits),
        )

    # Fase 2: decisioni + esecuzione, delegate al manager.
    manager = npc_manager or NPCManager()
    states = manager.load(session, include_player=include_player)
    decisions = manager.update_all(
        session,
        states,
        tick_index=tick_index,
        master_seed=master_seed,
    )

    # Fase 3: moodlet, mood, cleanup per tutti (player incluso).
    char_ids = [c.id for c in all_characters]
    needs_by_char = needs_of_many(session, char_ids)
    for char in all_characters:
        intimacy = needs_by_char[char.id].get(NeedKind.INTIMACY, 100.0)
        streak = update_lonely_streak(session, char.id, intimacy)
        if streak >= LONELY_STREAK_TRIGGER:
            apply_moodlet(session, char.id, MoodletKind.LONELY, tick_index)
    refresh_need_moodlets_many(session, needs_by_char, tick_index)
    apply_intimacy_moodlets_many(session, char_ids, tick_index)
    deltas_by_char = active_delta_many(session, char_ids, tick_index)
    for char in all_characters:
        update_mood(
            session,
            char.id,
            tick=tick_index,
            needs=needs_by_char[char.id],
            moodlet_delta=deltas_by_char[char.id],
        )
    cleanup_expired_many(session, char_ids, tick_index)

    return TickReport(
        tick_index=tick_index,
        minutes=minutes,
        seed=master_seed,
        decisions=tuple(decisions),
        payday=payday_report,
        deaths=len(kills),
    )
