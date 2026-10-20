from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.economy.enums import TransactionKind
from simai.economy.models import Job, Transaction


def job_of(session: Session, character_id: int) -> Job | None:
    return session.scalar(select(Job).where(Job.character_id == character_id))


def all_jobs(session: Session) -> list[Job]:
    return list(session.scalars(select(Job).order_by(Job.id)).all())


def record_transaction(
    session: Session,
    *,
    tick_index: int,
    amount: float,
    kind: TransactionKind,
    from_character_id: int | None = None,
    to_character_id: int | None = None,
    note: str = "",
) -> Transaction:
    """Registra un movimento. Non applica il denaro: il chiamante lo fa.

    `amount` è sempre positivo. `from`/`to` null significano "world".
    """
    if amount <= 0:
        raise ValueError(f"amount must be > 0, got {amount}")
    tx = Transaction(
        tick_index=tick_index,
        from_character_id=from_character_id,
        to_character_id=to_character_id,
        amount=amount,
        kind=kind,
        note=note,
    )
    session.add(tx)
    return tx


def transactions_of(session: Session, character_id: int) -> list[Transaction]:
    return list(
        session.scalars(
            select(Transaction)
            .where(
                (Transaction.from_character_id == character_id)
                | (Transaction.to_character_id == character_id)
            )
            .order_by(Transaction.id)
        ).all()
    )
