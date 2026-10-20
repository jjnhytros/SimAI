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


def filter_by_need_threshold(
    available: list[ActionDef],
    needs: dict[NeedKind, float],
) -> list[ActionDef]:
    """Mantiene le azioni il cui bisogno è sotto la soglia di partenza.

    Un'azione è disponibile solo se il bisogno che soddisfa è
    "abbastanza basso" da giustificarla: non mangi quando sei sazio.
    """
    return [a for a in available if needs.get(a.satisfies, 100.0) < a.max_need_to_start]


def filter_by_affordability(available: list[ActionDef], balance: float) -> list[ActionDef]:
    """Mantiene solo le azioni pagabili.

    Azione con `cost <= balance`. `balance` negativo è trattato come 0
    (non dovrebbe succedere, ma per sicurezza).
    """
    effective = max(0.0, balance)
    return [a for a in available if a.cost <= effective]
