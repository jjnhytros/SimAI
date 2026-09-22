"""Package `simai.npc.ai` — bisogni → decisioni → azioni (BT + utility)."""

from simai.npc.ai.actions import ACTION_CATALOG, Action, action_of
from simai.npc.ai.bt import (
    ActionLeaf,
    AlwaysFail,
    AlwaysSucceed,
    Blackboard,
    BTNode,
    BTStatus,
    Condition,
    Cooldown,
    Inverter,
    Parallel,
    Repeat,
    Selector,
    Sequence,
    Succeeder,
    WaitLeaf,
    render_tree,
)
from simai.npc.ai.bt_templates import build_bt_for_action
from simai.npc.ai.coordinator import AICoordinator, TickResult
from simai.npc.ai.enums import ActionType
from simai.npc.ai.executor import (
    ActionExecutor,
    ActionProgress,
    BTActionExecutor,
)
from simai.npc.ai.utility import AIDecisionMaker, ScoredAction

__all__ = [
    "ACTION_CATALOG",
    "AICoordinator",
    "AIDecisionMaker",
    "Action",
    "ActionExecutor",
    "ActionLeaf",
    "ActionProgress",
    "ActionType",
    "AlwaysFail",
    "AlwaysSucceed",
    "BTActionExecutor",
    "BTNode",
    "BTStatus",
    "Blackboard",
    "Condition",
    "Cooldown",
    "Inverter",
    "Parallel",
    "Repeat",
    "ScoredAction",
    "Selector",
    "Sequence",
    "Succeeder",
    "TickResult",
    "WaitLeaf",
    "action_of",
    "build_bt_for_action",
    "render_tree",
]
