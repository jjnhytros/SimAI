from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.economy.calendar import TICKS_PER_DAY
from simai.npc.death import KillResult, check_age
from simai.npc.pregnancy import DeliverResult, deliver, due_pregnancies
from simai.world.models import Character

AGE_DAYS_PER_YEAR = 432


def apply_aging(session: Session) -> int:
    characters = session.scalars(select(Character)).all()
    birthdays = 0
    for char in characters:
        char.age_days += 1
        if char.age_days > AGE_DAYS_PER_YEAR - 1:
            char.age_days = 0
            char.age_years += 1
            birthdays += 1
    return birthdays


class LifecycleManager:
    def daily_tick(
        self,
        session: Session,
        tick_index: int,
        *,
        master_seed: int = 42,
    ) -> tuple[list[KillResult], list[DeliverResult]]:
        if tick_index % TICKS_PER_DAY != 0:
            return [], []
        birthdays = apply_aging(session)
        if birthdays:
            logger.debug(f"Lifecycle tick {tick_index}: {birthdays} compleanni")

        kills = check_age(session, tick_index)
        if kills:
            logger.info(f"Lifecycle tick {tick_index}: {len(kills)} morti per età")

        deliveries: list[DeliverResult] = []
        for pregnancy in due_pregnancies(session, tick_index):
            result = deliver(session, pregnancy, master_seed=master_seed)
            deliveries.append(result)

        return kills, deliveries
