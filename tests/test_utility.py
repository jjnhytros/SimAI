import random

from simai.actions.catalog import actions_for_location
from simai.actions.enums import ActionKind
from simai.actions.utility import (
    choose_action,
    rng_for_decision,
    score,
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


def test_actions_for_residential() -> None:
    kinds = {a.kind for a in actions_for_location(LocationKind.RESIDENTIAL)}
    assert kinds == {
        ActionKind.EAT,
        ActionKind.DRINK,
        ActionKind.PLAY,
        ActionKind.SOCIALIZE,
        ActionKind.STUDY,
    }


def test_actions_for_social() -> None:
    kinds = {a.kind for a in actions_for_location(LocationKind.SOCIAL)}
    assert kinds == {
        ActionKind.EAT,
        ActionKind.DRINK,
        ActionKind.PLAY,
        ActionKind.SOCIALIZE,
    }


def test_actions_for_leisure() -> None:
    kinds = {a.kind for a in actions_for_location(LocationKind.LEISURE)}
    assert kinds == {
        ActionKind.EAT,
        ActionKind.DRINK,
        ActionKind.PLAY,
        ActionKind.SOCIALIZE,
    }


def test_score_higher_for_lower_need() -> None:
    eat = next(a for a in actions_for_location(LocationKind.LEISURE) if a.kind == ActionKind.EAT)
    assert score(eat, _needs(hunger=10.0)) > score(eat, _needs())


def test_score_zero_for_full_need() -> None:
    eat = next(a for a in actions_for_location(LocationKind.LEISURE) if a.kind == ActionKind.EAT)
    assert score(eat, _needs()) == 0.0


def test_choose_action_returns_none_when_empty() -> None:
    assert choose_action(_needs(), [], random.Random(0)) is None


def test_choose_action_picks_most_urgent() -> None:
    needs = _needs(hunger=5.0, thirst=90.0, fun=90.0, intimacy=90.0)
    available = actions_for_location(LocationKind.LEISURE)
    for seed in range(10):
        choice = choose_action(needs, available, rng_for_decision(seed, 1))
        assert choice is not None
        assert choice.kind == ActionKind.EAT


def test_same_seed_same_choice() -> None:
    needs = _needs(hunger=50.0, thirst=50.0)
    available = actions_for_location(LocationKind.LEISURE)
    for seed in range(5):
        c1 = choose_action(needs, available, rng_for_decision(seed, 1))
        c2 = choose_action(needs, available, rng_for_decision(seed, 1))
        assert c1 == c2


def test_different_seeds_can_differ() -> None:
    needs = _needs(hunger=50.0, thirst=50.0)
    available = actions_for_location(LocationKind.LEISURE)
    chosen: set[ActionKind] = set()
    for seed in range(50):
        c = choose_action(needs, available, rng_for_decision(seed, 1))
        assert c is not None
        chosen.add(c.kind)
    assert ActionKind.EAT in chosen
    assert ActionKind.DRINK in chosen
