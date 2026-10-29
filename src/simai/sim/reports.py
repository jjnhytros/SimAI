from dataclasses import dataclass, field

from simai.actions.enums import ActionKind
from simai.economy.payday import PaydayReport
from simai.needs.enums import NeedKind


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
    deaths: int = 0
