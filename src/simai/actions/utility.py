import random

from simai.actions.catalog import ActionDef
from simai.needs.enums import NeedKind

JITTER = 5.0
VALUE_MAX = 100.0


def rng_for_decision(master_seed: int, character_id: int, tick: int = 0) -> random.Random:
    """RNG deterministico per una decisione.

    `tick` differenzia le decisioni fra tick successivi. Con default 0
    il comportamento per `actions choose` è invariato.
    """
    return random.Random(f"simai:{master_seed}:{character_id}:{tick}")


def score(action: ActionDef, needs: dict[NeedKind, float]) -> float:
    """Utility = quanto è basso il bisogno soddisfatto, scalato dal peso."""
    value = needs[action.satisfies]
    return (VALUE_MAX - value) * action.weight


def choose_action(
    needs: dict[NeedKind, float],
    available: list[ActionDef],
    rng: random.Random,
) -> ActionDef | None:
    """Sceglie l'azione con utility massima + jitter deterministico.

    Tie-break: ordinamento per `kind.value`, stabile fra piattaforme.
    Ritorna None se il catalogo disponibile è vuoto.
    """
    if not available:
        return None

    scored = [(action, score(action, needs) + rng.uniform(-JITTER, JITTER)) for action in available]
    scored.sort(key=lambda item: (-item[1], item[0].kind.value))
    return scored[0][0]


def filter_by_cooldown(
    available: list[ActionDef],
    current_tick: int,
    last_satisfied: dict[NeedKind, int | None],
) -> list[ActionDef]:
    """Rimuove le azioni ancora in cooldown per il loro bisogno.

    Un'azione senza cooldown o mai eseguita resta disponibile. Un tick
    negativo (last nel futuro) è trattato come "in cooldown".
    """
    result: list[ActionDef] = []
    for action in available:
        if action.cooldown_ticks <= 0:
            result.append(action)
            continue
        last = last_satisfied.get(action.satisfies)
        if last is None:
            result.append(action)
            continue
        if (current_tick - last) >= action.cooldown_ticks:
            result.append(action)
    return result
