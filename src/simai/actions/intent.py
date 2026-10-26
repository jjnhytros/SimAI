import random
from dataclasses import dataclass

from simai.actions.catalog import ActionDef
from simai.actions.reachability import ReachableMove
from simai.actions.utility import (
    JITTER,
    VALUE_MAX,
    choose_action,
    score,
)
from simai.needs.enums import NeedKind
from simai.npc.traits import trait_move_penalty
from simai.world.enums import LocationKind

DISTANCE_PENALTY = 5.0


@dataclass(frozen=True)
class MoveIntent:
    target_location_key: str
    target_location_kind: LocationKind
    satisfies: NeedKind
    need_value: float
    score: float


@dataclass(frozen=True)
class Intent:
    action: ActionDef | None = None
    move: MoveIntent | None = None


def _move_score(
    move: ReachableMove,
    jitter: float,
    traits: list[str] | None = None,
) -> float:
    raw = (VALUE_MAX - move.need_value) - DISTANCE_PENALTY
    if traits:
        raw += trait_move_penalty(traits)
    return raw + jitter


def choose_intent(
    needs: dict[NeedKind, float],
    available_actions: list[ActionDef],
    available_moves: list[ReachableMove],
    rng: random.Random,
    traits: list[str] | None = None,
) -> Intent:
    """Sceglie fra azione locale e movimento.

    Con `available_moves` vuoto, il comportamento è identico a
    `choose_action` (stesso seed, stessa scelta).
    """
    if not available_moves:
        return Intent(action=choose_action(needs, available_actions, rng, traits))

    move_evals = [
        (
            m,
            _move_score(m, rng.uniform(-JITTER, JITTER), traits),
        )
        for m in available_moves
    ]
    best_move, best_move_score = min(
        move_evals,
        key=lambda x: (-x[1], x[0].target_location_key),
    )

    if available_actions:
        action_evals = [
            (
                a,
                score(a, needs, traits) + rng.uniform(-JITTER, JITTER),
            )
            for a in available_actions
        ]
        best_action, best_action_score = min(
            action_evals,
            key=lambda x: (-x[1], x[0].kind.value),
        )
        if best_action_score >= best_move_score:
            return Intent(action=best_action)

    return Intent(
        move=MoveIntent(
            target_location_key=best_move.target_location_key,
            target_location_kind=best_move.target_location_kind,
            satisfies=best_move.satisfies,
            need_value=best_move.need_value,
            score=best_move_score,
        )
    )
