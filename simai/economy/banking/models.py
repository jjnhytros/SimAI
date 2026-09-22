"""Modelli SQLAlchemy del dominio banking."""

from __future__ import annotations

from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from simai.db.base import Base, IdMixin, TimestampMixin
from simai.economy.banking.enums import (
    BankAccountKind,
    BankKind,
    LoanStatus,
)


class Bank(IdMixin, TimestampMixin, Base):
    """Una banca."""

    __tablename__ = "bank"

    code: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    kind: Mapped[str] = mapped_column(
        String(16), nullable=False, default=BankKind.COMMERCIAL.value, index=True
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="1", index=True
    )
    owner_character_id: Mapped[int | None] = mapped_column(
        ForeignKey("character.id", ondelete="SET NULL"), nullable=True, index=True
    )
    reserve_ratio: Mapped[float] = mapped_column(Float, nullable=False, default=0.10)
    deposit_interest_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.02)
    loan_interest_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.08)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    def __repr__(self) -> str:
        return f"Bank(id={self.id}, code={self.code!r}, kind={self.kind}, active={self.is_active})"


class BankAccount(IdMixin, TimestampMixin, Base):
    """Conto bancario di un Character presso una Bank.

    Unique su `(bank_id, character_id, kind)`: al massimo un conto per tipo
    per banca per character.
    """

    __tablename__ = "bank_account"

    bank_id: Mapped[int] = mapped_column(
        ForeignKey("bank.id", ondelete="CASCADE"), nullable=False, index=True
    )
    character_id: Mapped[int] = mapped_column(
        ForeignKey("character.id", ondelete="CASCADE"), nullable=False, index=True
    )
    kind: Mapped[str] = mapped_column(
        String(16), nullable=False, default=BankAccountKind.CHECKING.value, index=True
    )
    balance: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0, server_default="0")
    interest_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.02)
    opened_at_total_seconds: Mapped[int] = mapped_column(BigInteger, nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="1", index=True
    )
    is_frozen: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="0", index=True
    )
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    __table_args__ = (
        UniqueConstraint("bank_id", "character_id", "kind", name="uq_bank_account_triple"),
    )

    def __repr__(self) -> str:
        return (
            f"BankAccount(id={self.id}, bank={self.bank_id}, char={self.character_id}, "
            f"kind={self.kind}, balance={self.balance})"
        )


class Loan(IdMixin, TimestampMixin, Base):
    """Un prestito erogato da una Bank a un Character.

    Diversamente da `Mortgage`, il prestito **non è vincolato a un lot**.
    Può essere garantito (`collateral_lot_id`) o puro credito al consumo.
    """

    __tablename__ = "loan"

    bank_id: Mapped[int] = mapped_column(
        ForeignKey("bank.id", ondelete="CASCADE"), nullable=False, index=True
    )
    character_id: Mapped[int] = mapped_column(
        ForeignKey("character.id", ondelete="CASCADE"), nullable=False, index=True
    )
    principal: Mapped[int] = mapped_column(Integer, nullable=False)
    remaining_principal: Mapped[float] = mapped_column(Float, nullable=False)
    annual_interest_rate: Mapped[float] = mapped_column(Float, nullable=False)
    term_months: Mapped[int] = mapped_column(Integer, nullable=False)
    monthly_payment: Mapped[int] = mapped_column(Integer, nullable=False)
    payments_made: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    payments_missed: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    next_payment_at_total_seconds: Mapped[int] = mapped_column(
        BigInteger, nullable=False, index=True
    )
    started_at_total_seconds: Mapped[int] = mapped_column(BigInteger, nullable=False)
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, default=LoanStatus.ACTIVE.value, index=True
    )
    collateral_lot_id: Mapped[int | None] = mapped_column(
        ForeignKey("lot.id", ondelete="SET NULL"), nullable=True, index=True
    )
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    def __repr__(self) -> str:
        return (
            f"Loan(id={self.id}, bank={self.bank_id}, char={self.character_id}, "
            f"principal={self.principal}, rem={self.remaining_principal:.0f}, "
            f"status={self.status})"
        )


class LoanPayment(IdMixin, TimestampMixin, Base):
    """Registro di un tentativo (riuscito o fallito) di pagamento di una rata."""

    __tablename__ = "loan_payment"

    loan_id: Mapped[int] = mapped_column(
        ForeignKey("loan.id", ondelete="CASCADE"), nullable=False, index=True
    )
    amount: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    interest_part: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    principal_part: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    remaining_after: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    paid_at_total_seconds: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="1")
    reason: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    def __repr__(self) -> str:
        return (
            f"LoanPayment(loan={self.loan_id}, amount={self.amount}, "
            f"success={self.success}, reason={self.reason!r})"
        )


class InterestAccrual(IdMixin, TimestampMixin, Base):
    """Audit trail degli interessi accreditati/addebitati su un prestito.

    Creato ad ogni pagamento rata (interesse del periodo). Serve per report
    e per riconciliazione contabile con il ledger.
    """

    __tablename__ = "interest_accrual"

    loan_id: Mapped[int] = mapped_column(
        ForeignKey("loan.id", ondelete="CASCADE"), nullable=False, index=True
    )
    accrued_amount: Mapped[float] = mapped_column(Float, nullable=False)
    at_total_seconds: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    def __repr__(self) -> str:
        return f"InterestAccrual(loan={self.loan_id}, amount={self.accrued_amount:.2f})"


__all__ = ["Bank", "BankAccount", "InterestAccrual", "Loan", "LoanPayment"]
