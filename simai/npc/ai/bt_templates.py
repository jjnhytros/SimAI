"""Template BT per ActionType.

Le azioni "semplici" del `ACTION_CATALOG` sono mappate a un albero
triviale: `Sequence[WaitLeaf(duration, on_tick=apply_effects)]`.

Le azioni complesse (futuro) possono avere alberi multi-step.
"""

from __future__ import annotations

from functools import partial

from simai.npc.ai.actions import Action
from simai.npc.ai.bt import Blackboard, BTNode, Sequence, WaitLeaf
from simai.npc.needs.enums import NeedType
from simai.npc.needs.needs import Needs


def _apply_effects(bb: Blackboard, *, action: Action) -> None:
    """Callback eseguita ogni tick dal WaitLeaf: distribuisce effetti."""
    needs = bb.get("needs")
    if not isinstance(needs, Needs):
        return
    updated = needs
    for need in NeedType:
        delta = action.effect_per_tick(need)
        if delta != 0.0:
            updated = updated.with_delta(need, delta)
    bb.set("needs", updated)


def build_bt_for_action(action: Action) -> BTNode:
    """Costruisce un BT per l'azione `action`.

    Ritorna un albero *fresco* (non riusabile tra esecuzioni).
    """
    on_tick = partial(_apply_effects, action=action)
    return Sequence(
        WaitLeaf(
            ticks=action.duration_ticks,
            on_tick=on_tick,
            name=f"wait_{action.type.value}",
        ),
        name=f"bt_{action.type.value}",
    )


__all__ = ["build_bt_for_action"]
