from dataclasses import dataclass

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.actions.catalog import actions_for_location
from simai.actions.enums import ActionKind
from simai.actions.intent import choose_intent
from simai.actions.reachability import available_moves
from simai.actions.utility import (
    filter_by_need_threshold,
    rng_for_decision,
)
from simai.mood.service import update_mood
from simai.needs.enums import NeedKind
from simai.needs.service import apply_decay, apply_effect, needs_of
from simai.relationships.service import boost_social_relationship
from simai.sim.state import get_state
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


@dataclass(frozen=True)
class TickReport:
    tick_index: int
    minutes: int
    seed: int
    decisions: tuple[TickDecision, ...]


def run_tick(
    session: Session,
    *,
    minutes: int,
    tick_index: int | None = None,
    master_seed: int | None = None,
    include_player: bool = False,
) -> TickReport:
    """Avanza la simulazione di `minutes`.

    Il decadimento viene applicato a tutti i personaggi, incluso il
    player. La decisione di azione o movimento viene presa solo per gli
    NPC, a meno di `include_player=True`.

    Ordine interno:
      1. apply_decay + update_mood per tutti
      2. per ogni decider: choose_intent fra azione locale e movimento
      3. esegui (azione o move)
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

    all_characters = session.scalars(select(Character).order_by(Character.id)).all()
    needs_by_char: dict[int, dict[NeedKind, float]] = {}
    for char in all_characters:
        apply_decay(session, char.id, minutes)
        update_mood(session, char.id)
        needs_by_char[char.id] = needs_of(session, char.id)

    q = select(Character).order_by(Character.id)
    if not include_player:
        q = q.where(Character.is_player.is_(False))
    deciders = session.scalars(q).all()

    decisions: list[TickDecision] = []
    for char in deciders:
        loc = session.get(Location, char.location_id)
        if loc is None:
            raise RuntimeError(f"Character {char.key} has invalid location_id={char.location_id}")

        needs = needs_by_char[char.id]
        actions = actions_for_location(loc.kind)
        local_actions = filter_by_need_threshold(actions, needs)
        moves = available_moves(
            session,
            current_location_id=loc.id,
            needs=needs,
        )
        rng = rng_for_decision(master_seed, char.id, tick_index)
        intent = choose_intent(needs, local_actions, moves, rng)

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
                f"Nessuna azione per {char.key} in {loc.key}: "
                f"tutti i bisogni sopra soglia o catalogo vuoto."
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
        rel_after = boost_social_relationship(session, char.id, action)
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
            )
        )

    return TickReport(
        tick_index=tick_index,
        minutes=minutes,
        seed=master_seed,
        decisions=tuple(decisions),
    )
