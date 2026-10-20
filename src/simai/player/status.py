from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.actions.catalog import actions_for_location
from simai.actions.utility import filter_by_cooldown
from simai.needs.enums import NeedKind
from simai.needs.service import last_satisfied_map, needs_of
from simai.relationships.enums import RelationshipKind
from simai.relationships.models import Relationship
from simai.sim.state import get_state
from simai.world.models import Character, Location


@dataclass(frozen=True)
class PlayerStatus:
    tick_index: int
    master_seed: int
    character_key: str
    name: str
    age_years: int
    mood: float
    location_key: str
    location_name: str
    location_kind: str
    needs: dict[NeedKind, float]
    relationships: dict[str, float]
    available_actions: list[str]
    other_characters_here: list[str]
    cooldowns: dict[str, int]
    available_locations: list[dict[str, Any]]


def build_player_status(session: Session) -> PlayerStatus | None:
    player = session.scalar(select(Character).where(Character.is_player.is_(True)))
    if player is None:
        return None

    loc = session.get(Location, player.location_id)
    if loc is None:
        return None

    state = get_state(session)

    rels = session.scalars(
        select(Relationship).where(
            Relationship.from_character_id == player.id,
            Relationship.kind == RelationshipKind.FRIEND,
        )
    ).all()
    rel_map: dict[str, float] = {}
    for rel in rels:
        target = session.get(Character, rel.to_character_id)
        if target is not None:
            rel_map[target.key] = rel.strength

    here = session.scalars(
        select(Character).where(
            Character.location_id == loc.id,
            Character.id != player.id,
        )
    ).all()

    actions = actions_for_location(loc.kind)

    now = state.tick_index
    last = last_satisfied_map(session, player.id)
    available_now = filter_by_cooldown(actions, now, last)
    available_kinds = {a.kind for a in available_now}
    cooldowns: dict[str, int] = {}
    for action in actions:
        if action.kind in available_kinds:
            continue
        last_tick = last.get(action.satisfies)
        if last_tick is None or action.cooldown_ticks <= 0:
            continue
        remaining = action.cooldown_ticks - (now - last_tick)
        if remaining > 0:
            cooldowns[action.kind.value] = remaining

    locations = session.scalars(select(Location).order_by(Location.id)).all()

    return PlayerStatus(
        tick_index=state.tick_index,
        master_seed=state.master_seed,
        character_key=player.key,
        name=player.name,
        age_years=player.age_years,
        mood=float(player.mood),
        location_key=loc.key,
        location_name=loc.name,
        location_kind=loc.kind.value,
        needs=needs_of(session, player.id),
        relationships=rel_map,
        available_actions=[a.kind.value for a in available_now],
        other_characters_here=[c.key for c in here],
        cooldowns=cooldowns,
        available_locations=[
            {"key": l.key, "name": l.name, "kind": l.kind.value} for l in locations
        ],
    )
