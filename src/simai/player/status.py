from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.actions.catalog import actions_for_location
from simai.actions.utility import filter_by_need_threshold
from simai.needs.enums import NeedKind
from simai.needs.service import needs_of
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
    unnecessary_actions: list[str]
    other_characters_here: list[str]
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

    needs = needs_of(session, player.id)
    actions = actions_for_location(loc.kind)
    available_now = filter_by_need_threshold(actions, needs)
    available_kinds = {a.kind for a in available_now}
    unnecessary = [a.kind.value for a in actions if a.kind not in available_kinds]

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
        needs=needs,
        relationships=rel_map,
        available_actions=[a.kind.value for a in available_now],
        unnecessary_actions=unnecessary,
        other_characters_here=[c.key for c in here],
        available_locations=[
            {"key": l.key, "name": l.name, "kind": l.kind.value} for l in locations
        ],
    )
