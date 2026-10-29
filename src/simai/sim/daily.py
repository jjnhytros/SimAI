from sqlalchemy.orm import Session

from simai.economy.calendar import TICKS_PER_DAY
from simai.economy.seed import restock_all
from simai.npc.death import KillResult
from simai.npc.lifecycle import LifecycleManager
from simai.npc.pregnancy import DeliverResult


def daily_tick(session: Session, tick_index: int) -> tuple[list[KillResult], list[DeliverResult]]:
    if tick_index % TICKS_PER_DAY == 0:
        restock_all(session)
    return LifecycleManager().daily_tick(session, tick_index)
