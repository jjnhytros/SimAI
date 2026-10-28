from sqlalchemy.orm import Session

from simai.economy.calendar import TICKS_PER_DAY
from simai.economy.seed import restock_all
from simai.npc.lifecycle import LifecycleManager
from simai.sim.state import get_state


def daily_tick(session: Session, tick_index: int) -> None:
    if tick_index % TICKS_PER_DAY != 0:
        return
    restock_all(session)
    seed = get_state(session).master_seed
    LifecycleManager().daily_tick(session, tick_index, master_seed=seed)
