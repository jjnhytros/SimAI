from dataclasses import dataclass, field

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.actions.catalog import ActionDef, actions_for_location
from simai.actions.enums import ActionKind
from simai.actions.intent import choose_intent
from simai.actions.reachability import (
    available_moves,
    filter_moves_by_affordability,
)
from simai.actions.utility import (
    filter_by_affordability,
    filter_by_need_threshold,
    rng_for_decision,
)
from simai.economy.market import buy as market_buy
from simai.economy.market import filter_by_stock
from simai.economy.payday import PaydayReport, process_payday
from simai.economy.service import job_of
from simai.economy.work import (
    should_prioritize_home,
    should_prioritize_work,
    tick_in_day,
)
from simai.mood.enums import MoodletKind
from simai.mood.moodlets import (
    LONELY_STREAK_TRIGGER,
    apply_moodlet,
    cleanup_expired,
    moodlets_for_action,
    update_lonely_streak,
)
from simai.mood.service import update_mood
from simai.needs.enums import NeedKind
from simai.needs.service import (
    apply_decay,
    apply_effect,
    needs_of,
)
from simai.relationships.service import boost_social_relationship
from simai.sim.state import get_state
from simai.world.enums import LocationKind
from simai.world.models import Character, Location
from simai.world.move import move_character


@dataclass(frozen=True)
class TickDecision:
    character_id: int
    character_key: str
    location_key: str
    action: ActionKind | None
    satisfied: NeedKind | None
    value_before: float | None
    value_after: float | None
    relationship_strength_after: float | None = None
    moved_from: str | None = None
    moved_to: str | None = None
    cost_paid: float = 0.0


@dataclass(frozen=True)
class TickReport:
    tick_index: int
    minutes: int
    seed: int
    decisions: tuple[TickDecision, ...]
    payday: PaydayReport = field(default_factory=PaydayReport)


def _all_actions_by_kind() -> dict[LocationKind, list[ActionDef]]:
    return {kind: actions_for_location(kind) for kind in LocationKind}


def run_tick(
    session: Session,
    *,
    minutes: int,
    tick_index: int | None = None,
    master_seed: int | None = None,
    include_player: bool = False,
) -> TickReport:
    """Avanza la simulazione di `minutes`.

    Ordine interno:
      1. payday (fine turno, richiede presenza)
      2. apply_decay (modulato dai tratti)
      3. per ogni decider: priorità lavoro → priorità casa →
         choose_intent (con bonus tratti)
      4. esegui (azione o move), addebita costi
      5. moodlet (streak, azione, mood, cleanup)
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
    needs_by_char: dict[int, dict[NeedKind, float]] = {
        c.id: needs_of(session, c.id) for c in all_characters
    }

    catalog_by_kind = _all_actions_by_kind()
    t_in_day = tick_in_day(tick_index)

    q = select(Character).order_by(Character.id)
    if not include_player:
        q = q.where(Character.is_player.is_(False))
    deciders = session.scalars(q).all()

    decisions: list[TickDecision] = []
    for char in deciders:
        loc = session.get(Location, char.location_id)
        if loc is None:
            raise RuntimeError(f"Character {char.key} has invalid location_id={char.location_id}")

        traits = list(char.traits)
        needs = needs_by_char[char.id]
        actions = actions_for_location(loc.kind)
        local_actions = filter_by_need_threshold(actions, needs)
        local_actions = filter_by_affordability(local_actions, char.balance)
        local_actions = filter_by_stock(session, local_actions, loc.key)
        local_satisfies = {a.satisfies for a in local_actions}

        raw_moves = available_moves(
            session,
            current_location_id=loc.id,
            needs=needs,
        )
        raw_moves = [m for m in raw_moves if m.satisfies not in local_satisfies]
        moves = filter_moves_by_affordability(raw_moves, char.balance, catalog_by_kind)

        job = job_of(session, char.id)
        hunger = needs.get(NeedKind.HUNGER, 100.0)
        if should_prioritize_work(job, t_in_day, hunger):
            assert job is not None
            if loc.key != job.location_key:
                result = move_character(session, char.key, job.location_key)
                if not result.success:
                    raise RuntimeError(f"Move lavoro fallito per {char.key}: {result.error}")
                decisions.append(
                    TickDecision(
                        character_id=char.id,
                        character_key=char.key,
                        location_key=loc.key,
                        action=None,
                        satisfied=None,
                        value_before=None,
                        value_after=None,
                        moved_from=result.from_location_key,
                        moved_to=result.to_location_key,
                    )
                )
                continue
            moves = []

        if job is not None and not should_prioritize_work(job, t_in_day, hunger):
            home_loc = (
                session.get(Location, char.home_location_id)
                if char.home_location_id is not None
                else None
            )
            home_key = home_loc.key if home_loc else None
            intimacy = needs.get(NeedKind.INTIMACY, 100.0)
            fun = needs.get(NeedKind.FUN, 100.0)
            if should_prioritize_home(
                job,
                t_in_day,
                home_key,
                loc.key,
                intimacy,
                fun,
            ):
                assert home_loc is not None
                result = move_character(session, char.key, home_loc.key)
                if not result.success:
                    raise RuntimeError(f"Move casa fallito per {char.key}: {result.error}")
                decisions.append(
                    TickDecision(
                        character_id=char.id,
                        character_key=char.key,
                        location_key=loc.key,
                        action=None,
                        satisfied=None,
                        value_before=None,
                        value_after=None,
                        moved_from=result.from_location_key,
                        moved_to=result.to_location_key,
                    )
                )
                continue

        rng = rng_for_decision(master_seed, char.id, tick_index)
        intent = choose_intent(needs, local_actions, moves, rng, traits)

        if intent.move is not None:
            result = move_character(session, char.key, intent.move.target_location_key)
            if not result.success:
                raise RuntimeError(f"Move fallito per {char.key}: {result.error}")
            decisions.append(
                TickDecision(
                    character_id=char.id,
                    character_key=char.key,
                    location_key=loc.key,
                    action=None,
                    satisfied=None,
                    value_before=None,
                    value_after=None,
                    moved_from=result.from_location_key,
                    moved_to=result.to_location_key,
                )
            )
            continue

        if intent.action is None:
            logger.debug(
                f"Nessuna azione per {char.key} in {loc.key}: nessuna azione o move disponibile."
            )
            decisions.append(
                TickDecision(
                    character_id=char.id,
                    character_key=char.key,
                    location_key=loc.key,
                    action=None,
                    satisfied=None,
                    value_before=None,
                    value_after=None,
                )
            )
            continue

        action = intent.action
        before = needs[action.satisfies]
        after = apply_effect(session, char.id, action)

        cost_paid = 0.0
        if action.cost > 0:
            purchase = market_buy(
                session,
                char,
                loc.key,
                action,
                tick_index=tick_index,
            )
            if not purchase.success:
                logger.warning(
                    f"Acquisto fallito per {char.key} ({action.kind.value} @ "
                    f"{loc.key}): {purchase.error}"
                )
                decisions.append(
                    TickDecision(
                        character_id=char.id,
                        character_key=char.key,
                        location_key=loc.key,
                        action=None,
                        satisfied=None,
                        value_before=None,
                        value_after=None,
                    )
                )
                continue
            cost_paid = purchase.price_paid

        rel_after = boost_social_relationship(session, char.id, action)
        moodlet_kind = moodlets_for_action(action.kind)
        if moodlet_kind is not None:
            apply_moodlet(session, char.id, moodlet_kind, tick_index)

        decisions.append(
            TickDecision(
                character_id=char.id,
                character_key=char.key,
                location_key=loc.key,
                action=action.kind,
                satisfied=action.satisfies,
                value_before=before,
                value_after=after,
                relationship_strength_after=rel_after,
                cost_paid=cost_paid,
            )
        )

    for char in all_characters:
        needs = needs_by_char[char.id]
        intimacy = needs.get(NeedKind.INTIMACY, 100.0)
        streak = update_lonely_streak(session, char.id, intimacy)
        if streak >= LONELY_STREAK_TRIGGER:
            apply_moodlet(session, char.id, MoodletKind.LONELY, tick_index)
        update_mood(session, char.id, tick=tick_index)
        cleanup_expired(session, char.id, tick_index)

    return TickReport(
        tick_index=tick_index,
        minutes=minutes,
        seed=master_seed,
        decisions=tuple(decisions),
        payday=payday_report,
    )
