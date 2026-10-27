from sqlalchemy.orm import Session

from simai.economy.calendar import TICKS_PER_DAY
from simai.economy.seed import restock_all


def daily_tick(session: Session, tick_index: int) -> None:
    """Operazioni giornaliere (una volta ogni TICKS_PER_DAY tick).

    In 1.6.0: solo restock dei negozi. Punto di aggancio futuro per
    `LifecycleManager` (ageing, morte, gravidanza, city tick).
    """
    if tick_index % TICKS_PER_DAY != 0:
        return
    restock_all(session)
