from sqlalchemy.orm import Session

from simai.economy.calendar import is_payday_tick
from simai.economy.enums import TransactionKind
from simai.economy.models import Job
from simai.economy.service import record_transaction
from simai.world.models import Character


def process_payday(session: Session, tick_index: int) -> int:
    """Se `tick_index` è un payday, accredita lo stipendio a chi ha un job.

    Ritorna il numero di personaggi pagati.
    """
    if not is_payday_tick(tick_index):
        return 0

    jobs = session.query(Job).all()
    paid = 0
    for job in jobs:
        if job.daily_wage <= 0:
            continue
        char = session.get(Character, job.character_id)
        if char is None:
            continue
        char.balance += job.daily_wage
        record_transaction(
            session,
            tick_index=tick_index,
            amount=job.daily_wage,
            kind=TransactionKind.SALARY,
            to_character_id=char.id,
            note=f"payday {job.title.value}",
        )
        paid += 1
    return paid
