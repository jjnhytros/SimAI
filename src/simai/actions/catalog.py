from dataclasses import dataclass

from simai.actions.enums import ActionKind
from simai.needs.enums import NeedKind
from simai.world.enums import LocationKind


@dataclass(frozen=True)
class ActionDef:
    kind: ActionKind
    satisfies: NeedKind
    amount: float
    allowed_at: frozenset[LocationKind]
    max_need_to_start: float
    weight: float = 1.0


CATALOG: tuple[ActionDef, ...] = (
    ActionDef(
        kind=ActionKind.EAT,
        satisfies=NeedKind.HUNGER,
        amount=40.0,
        allowed_at=frozenset({LocationKind.RESIDENTIAL, LocationKind.LEISURE}),
        max_need_to_start=30.0,
    ),
    ActionDef(
        kind=ActionKind.DRINK,
        satisfies=NeedKind.THIRST,
        amount=30.0,
        allowed_at=frozenset({LocationKind.LEISURE}),
        max_need_to_start=40.0,
    ),
    ActionDef(
        kind=ActionKind.PLAY,
        satisfies=NeedKind.FUN,
        amount=35.0,
        allowed_at=frozenset(
            {
                LocationKind.RESIDENTIAL,
                LocationKind.SOCIAL,
                LocationKind.LEISURE,
            }
        ),
        max_need_to_start=70.0,
    ),
    ActionDef(
        kind=ActionKind.SOCIALIZE,
        satisfies=NeedKind.INTIMACY,
        amount=25.0,
        allowed_at=frozenset({LocationKind.SOCIAL, LocationKind.LEISURE}),
        max_need_to_start=70.0,
    ),
)


def actions_for_location(loc_kind: LocationKind) -> list[ActionDef]:
    return [a for a in CATALOG if loc_kind in a.allowed_at]
