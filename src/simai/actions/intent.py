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


def _move_score(move: ReachableMove, jitter: float) -> float:
    raw = (VALUE_MAX - move.need_value) - DISTANCE_PENALTY
    return raw + jitter


def choose_intent(
    needs: dict[NeedKind, float],
    available_actions: list[ActionDef],
    available_moves: list[ReachableMove],
    rng: random.Random,
) -> Intent:
    """Sceglie fra azione locale e movimento verso un'altra location.

    Con `available_moves` vuoto, il comportamento è identico a
    `choose_action` (stesso seed, stessa scelta). Il test di equivalenza
    è il contratto che protegge da divergenze.
    """
    if not available_moves:
        return Intent(action=choose_action(needs, available_actions, rng))

    # Valuta ogni move con lo stesso jitter di choose_action (stessa
    # forma: uniform(-JITTER, +JITTER)), poi confronta il migliore con
    # la migliore azione locale.
    move_evals = [
        (
            m,
            _move_score(m, rng.uniform(-JITTER, JITTER)),
        )
        for m in available_moves
    ]
    best_move, best_move_score = min(move_evals, key=lambda x: (-x[1], x[0].target_location_key))

    if available_actions:
        action_evals = [
            (a, score(a, needs) + rng.uniform(-JITTER, JITTER)) for a in available_actions
        ]
        best_action, best_action_score = min(action_evals, key=lambda x: (-x[1], x[0].kind.value))
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
