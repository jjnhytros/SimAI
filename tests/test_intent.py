import random

from simai.actions.catalog import actions_for_location
from simai.actions.enums import ActionKind
from simai.actions.intent import (
    DISTANCE_PENALTY,
    choose_intent,
)
from simai.actions.reachability import ReachableMove
from simai.actions.utility import (
    choose_action,
    rng_for_decision,
)
from simai.needs.enums import NeedKind
from simai.world.enums import LocationKind


def _needs(
    hunger: float = 100.0,
    thirst: float = 100.0,
    fun: float = 100.0,
    intimacy: float = 100.0,
) -> dict[NeedKind, float]:
    return {
        NeedKind.HUNGER: hunger,
        NeedKind.THIRST: thirst,
        NeedKind.FUN: fun,
        NeedKind.INTIMACY: intimacy,
    }


def _rng(seed: int) -> random.Random:
    return rng_for_decision(seed, character_id=1, tick=0)


def test_empty_moves_matches_choose_action() -> None:
    needs = _needs(hunger=40.0, thirst=40.0, fun=50.0, intimacy=60.0)
    actions = actions_for_location(LocationKind.LEISURE)
    for seed in range(20):
        a = choose_action(needs, actions, _rng(seed))
        intent = choose_intent(needs, actions, [], _rng(seed))
        assert intent.move is None
        assert intent.action == a


def test_no_actions_but_move_returns_move() -> None:
    needs = _needs(thirst=20.0)
    moves = [
        ReachableMove(
            target_location_key="caffe",
            target_location_kind=LocationKind.LEISURE,
            satisfies=NeedKind.THIRST,
            need_value=20.0,
            action_kind=ActionKind.DRINK,
        )
    ]
    intent = choose_intent(needs, [], moves, _rng(0))
    assert intent.action is None
    assert intent.move is not None
    assert intent.move.target_location_key == "caffe"


def test_local_action_beats_weak_move() -> None:
    # A casa: hunger 5 (EAT locale). Thirst 35 (DRINK al caffè).
    # EAT locale score = 95 + jitter, move score = 65 - 5 + jitter = 60.
    # Vince EAT.
    needs = _needs(hunger=5.0, thirst=35.0)
    actions = actions_for_location(LocationKind.RESIDENTIAL)
    moves = [
        ReachableMove(
            target_location_key="caffe",
            target_location_kind=LocationKind.LEISURE,
            satisfies=NeedKind.THIRST,
            need_value=35.0,
            action_kind=ActionKind.DRINK,
        )
    ]
    intent = choose_intent(needs, actions, moves, _rng(0))
    assert intent.move is None
    assert intent.action is not None
    assert intent.action.kind == ActionKind.EAT


def test_distance_penalty_applied() -> None:
    # Thirst 50 (sopra soglia 40): non dovrebbe essere un move valido,
    # ma se lo fosse lo score sarebbe (100-50) - 5 = 45.
    move = ReachableMove(
        target_location_key="caffe",
        target_location_kind=LocationKind.LEISURE,
        satisfies=NeedKind.THIRST,
        need_value=50.0,
        action_kind=ActionKind.DRINK,
    )
    needs = _needs(thirst=50.0)
    intent = choose_intent(needs, [], [move], _rng(0))
    assert intent.move is not None
    # Con jitter in [-5, +5], lo score sta in [40, 50]
    assert 40.0 <= intent.move.score <= 50.0
    assert DISTANCE_PENALTY == 5.0


def test_determinism_across_rng() -> None:
    needs = _needs(thirst=20.0, hunger=30.0)
    actions = actions_for_location(LocationKind.RESIDENTIAL)
    moves = [
        ReachableMove(
            target_location_key="caffe",
            target_location_kind=LocationKind.LEISURE,
            satisfies=NeedKind.THIRST,
            need_value=20.0,
            action_kind=ActionKind.DRINK,
        )
    ]
    r1 = choose_intent(needs, actions, moves, _rng(42))
    r2 = choose_intent(needs, actions, moves, _rng(42))
    assert r1 == r2
