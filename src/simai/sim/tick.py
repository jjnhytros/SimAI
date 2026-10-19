from dataclasses import dataclass

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.actions.catalog import actions_for_location
from simai.actions.enums import ActionKind
from simai.actions.utility import choose_action, rng_for_decision
from simai.needs.enums import NeedKind
from simai.needs.service import apply_decay, apply_effect, needs_of
from simai.relationships.service import boost_social_relationship
from simai.sim.state import get_state
from simai.world.models import Character, Location


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

    Se `tick_index` è None, viene letto e incrementato da `SimState`.
    Se `master_seed` è None, viene letto da `SimState`.
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

    q = select(Character).order_by(Character.id)
    if not include_player:
        q = q.where(Character.is_player.is_(False))
    characters = session.scalars(q).all()

    decisions: list[TickDecision] = []
    for char in characters:
        loc = session.get(Location, char.location_id)
        if loc is None:
            raise RuntimeError(f"Character {char.key} has invalid location_id={char.location_id}")

        apply_decay(session, char.id, minutes)
        needs = needs_of(session, char.id)
        available = actions_for_location(loc.kind)
        rng = rng_for_decision(master_seed, char.id, tick_index)
        choice = choose_action(needs, available, rng)

        if choice is None:
            logger.warning(f"Nessuna azione per {char.key} in {loc.key}; salto il turno.")
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

        before = needs[choice.satisfies]
        after = apply_effect(session, char.id, choice)
        rel_after = boost_social_relationship(session, char.id, choice)
        decisions.append(
            TickDecision(
                character_id=char.id,
                character_key=char.key,
                location_key=loc.key,
                action=choice.kind,
                satisfied=choice.satisfies,
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
