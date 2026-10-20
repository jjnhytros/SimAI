TICKS_PER_DAY = 24


def is_payday_tick(tick_index: int) -> bool:
    """Payday alla fine del giorno convenzionale.

    Tick 23, 47, 71, ... (0-based). Con 24 tick eseguiti, il primo
    payday arriva al tick 23.
    """
    return tick_index > 0 and (tick_index + 1) % TICKS_PER_DAY == 0
