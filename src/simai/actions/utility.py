import random

from simai.actions.catalog import ActionDef
from simai.needs.enums import NeedKind
from simai.npc.traits import trait_utility_bonus

JITTER = 5.0
VALUE_MAX = 100.0


def rng_for_decision(master_seed: int, character_id: int, tick: int = 0) -> random.Random:
    """RNG deterministico per una decisione."""
    return random.Random(f"simai:{master_seed}:{character_id}:{tick}")


def score(
    action: ActionDef,
    needs: dict[NeedKind, float],
    traits: list[str] | None = None,
) -> float:
    """Utility = urgenza del bisogno soddisfatto + bonus tratto.

    Il bonus è additivo e piccolo (0.10–0.15) su score tipici
    30–90: sposta la decisione solo quando due opzioni sono vicine.
    """
    value = needs[action.satisfies]
    base = (VALUE_MAX - value) * action.weight
    if traits:
        base += trait_utility_bonus(traits, action.kind)
    return base


def filter_by_need_threshold(
    available: list[ActionDef],
    needs: dict[NeedKind, float],
) -> list[ActionDef]:
    """Mantiene le azioni il cui bisogno è sotto soglia."""
    return [a for a in available if needs.get(a.satisfies, 100.0) < a.max_need_to_start]


def filter_by_affordability(available: list[ActionDef], balance: float) -> list[ActionDef]:
    """Mantiene solo le azioni pagabili."""
    effective = max(0.0, balance)
    return [a for a in available if a.cost <= effective]


def choose_action(
    needs: dict[NeedKind, float],
    available: list[ActionDef],
    rng: random.Random,
    traits: list[str] | None = None,
) -> ActionDef | None:
    """Sceglie l'azione con utility massima + jitter.

    Tie-break stabile su `kind.value`.
    """
    if not available:
        return None

    scored = [
        (
            action,
            score(action, needs, traits) + rng.uniform(-JITTER, JITTER),
        )
        for action in available
    ]
    scored.sort(key=lambda item: (-item[1], item[0].kind.value))
    return scored[0][0]
