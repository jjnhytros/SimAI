from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.economy.calendar import TICKS_PER_DAY
from simai.mood.enums import MoodletKind
from simai.mood.moodlets import apply_moodlet
from simai.npc.death import KillResult, check_age, check_probabilistic
from simai.npc.lifestage import life_stage_for
from simai.npc.pregnancy import DeliverResult, deliver, due_pregnancies
from simai.world.enums import LifeStage
from simai.world.models import Character

AGE_DAYS_PER_YEAR = 432

# Solo 3 transizioni hanno un moodlet: le altre 5 (12, 15, 25, 40, 50)
# non sono considerate abbastanza significative in 1.10.0.
LIFESTAGE_TRANSITION_MOODLETS: dict[LifeStage, MoodletKind] = {
    LifeStage.CHILDHOOD: MoodletKind.BECAME_CHILD,
    LifeStage.YOUNG_ADULT: MoodletKind.BECAME_YOUNG_ADULT,
    LifeStage.SENIORITY: MoodletKind.BECAME_SENIOR,
}


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


def _apply_lifestage_moodlets(session: Session, tick_index: int) -> None:
    """Applica moodlet alle transizioni di LifeStage.

    `life_stage_for` è per anno (ignora `age_days`), quindi la
    transizione si rileva confrontando lo stage di oggi con quello
    calcolato su `age_years - 1`. Chiamata dopo `apply_aging`, così
    `age_years` riflette il compleanno appena passato.
    """
    characters = session.scalars(select(Character)).all()
    for char in characters:
        stage_now = life_stage_for(char.age_years)
        stage_prev = life_stage_for(char.age_years - 1)
        if stage_now == stage_prev:
            continue
        kind = LIFESTAGE_TRANSITION_MOODLETS.get(stage_now)
        if kind is not None:
            apply_moodlet(session, char.id, kind, tick_index)


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

        _apply_lifestage_moodlets(session, tick_index)

        kills = check_age(session, tick_index)
        kills.extend(check_probabilistic(session, tick_index, master_seed=master_seed))
        if kills:
            causes: dict[str, int] = {}
            for k in kills:
                causes[k.cause.value] = causes.get(k.cause.value, 0) + 1
            logger.info(f"Lifecycle tick {tick_index}: {len(kills)} morti ({causes})")

        deliveries: list[DeliverResult] = []
        for pregnancy in due_pregnancies(session, tick_index):
            result = deliver(session, pregnancy, master_seed=master_seed)
            deliveries.append(result)

        return kills, deliveries
