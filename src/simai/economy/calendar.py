TICKS_PER_DAY = 28
DAYS_PER_YEAR = 432  # Anthalys: 432 giorni per anno
TICKS_PER_YEAR = TICKS_PER_DAY * DAYS_PER_YEAR  # 12096


def is_payday_tick(tick_index: int) -> bool:
    """Payday alla fine del giorno convenzionale.

    Tick 27, 55, 83, ... (0-based). Con 28 tick eseguiti, il primo
    payday arriva al tick 27.
    """
    return tick_index > 0 and (tick_index + 1) % TICKS_PER_DAY == 0
