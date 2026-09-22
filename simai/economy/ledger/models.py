"""Modelli SQLAlchemy del ledger double-entry."""

from __future__ import annotations

from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from simai.db.base import Base, IdMixin, TimestampMixin


class Account(IdMixin, TimestampMixin, Base):
    """Un conto del ledger.

    Identificato da un `code` univoco (es. `char:42:athel`, `system:mint`).
    Il `kind` determina la semantica di dare/avere.
    """

    __tablename__ = "ledger_account"

    code: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    kind: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    owner_type: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    owner_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="1", index=True
    )
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    __table_args__ = (Index("ix_ledger_account_owner", "owner_type", "owner_id"),)

    def __repr__(self) -> str:
        return (
            f"Account(id={self.id}, code={self.code!r}, kind={self.kind}, "
            f"owner={self.owner_type}:{self.owner_id}, active={self.is_active})"
        )


class JournalEntry(IdMixin, TimestampMixin, Base):
    """Testata di una registrazione contabile.

    Una entry raggruppa N `Posting` (tipicamente 2) che nel loro insieme
    bilanciano a zero: somma DEBIT == somma CREDIT.
    """

    __tablename__ = "journal_entry"

    kind: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(256), nullable=False)
    at_total_seconds: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    reference_type: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    reference_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    def __repr__(self) -> str:
        return (
            f"JournalEntry(id={self.id}, kind={self.kind}, "
            f"at={self.at_total_seconds}, desc={self.description!r})"
        )


class Posting(IdMixin, TimestampMixin, Base):
    """Riga di registrazione su un conto.

    `amount` è sempre positivo: la direzione (`DEBIT`/`CREDIT`) determina
    se il valore del conto aumenta o diminuisce, in base al `kind` del conto.
    """

    __tablename__ = "posting"

    entry_id: Mapped[int] = mapped_column(
        ForeignKey("journal_entry.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    account_id: Mapped[int] = mapped_column(
        ForeignKey("ledger_account.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    direction: Mapped[str] = mapped_column(String(8), nullable=False, index=True)
    amount: Mapped[int] = mapped_column(BigInteger, nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_posting_amount_positive"),
        UniqueConstraint("entry_id", "account_id", "direction", name="uq_posting_entry_acc_dir"),
    )

    def __repr__(self) -> str:
        return (
            f"Posting(id={self.id}, entry={self.entry_id}, "
            f"account={self.account_id}, {self.direction} {self.amount})"
        )


__all__ = ["Account", "JournalEntry", "Posting"]
