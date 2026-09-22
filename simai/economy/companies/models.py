"""Modelli SQLAlchemy del dominio companies."""

from __future__ import annotations

from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from simai.db.base import Base, IdMixin, TimestampMixin
from simai.economy.companies.enums import (
    CompanyKind,
    CompanyStatus,
    CompanyTransactionKind,
    EmployeeRole,
)


class Company(IdMixin, TimestampMixin, Base):
    """Un'azienda NPC.

    Il campo `athel_balance` è una **cache materializzata** del saldo
    del conto ledger `company:<id>:athel`. Ogni modifica passa da
    `CompanyService`, che posta una `JournalEntry`.
    """

    __tablename__ = "company"

    name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    kind: Mapped[str] = mapped_column(
        String(24), nullable=False, default=CompanyKind.SHOP.value, index=True
    )
    owner_character_id: Mapped[int] = mapped_column(
        ForeignKey("character.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    location_id: Mapped[int | None] = mapped_column(
        ForeignKey("location.id", ondelete="SET NULL"), nullable=True, index=True
    )
    athel_balance: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0, server_default="0"
    )
    base_daily_revenue: Mapped[int] = mapped_column(
        Integer, nullable=False, default=100, server_default="100"
    )
    base_daily_cost: Mapped[int] = mapped_column(
        Integer, nullable=False, default=30, server_default="30"
    )
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, default=CompanyStatus.ACTIVE.value, index=True
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="1", index=True
    )
    founded_at_total_seconds: Mapped[int] = mapped_column(BigInteger, nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    def __repr__(self) -> str:
        return (
            f"Company(id={self.id}, name={self.name!r}, kind={self.kind}, "
            f"balance={self.athel_balance}, status={self.status})"
        )


class CompanyEmployee(IdMixin, TimestampMixin, Base):
    """Un dipendente di un'azienda.

    Unique su `(company_id, character_id)`: al massimo una riga attiva
    per dipendente. Il licenziamento marca `is_active=False` ma conserva
    la riga per storico.
    """

    __tablename__ = "company_employee"

    company_id: Mapped[int] = mapped_column(
        ForeignKey("company.id", ondelete="CASCADE"), nullable=False, index=True
    )
    character_id: Mapped[int] = mapped_column(
        ForeignKey("character.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(
        String(16), nullable=False, default=EmployeeRole.WORKER.value, index=True
    )
    daily_wage: Mapped[int] = mapped_column(
        Integer, nullable=False, default=12, server_default="12"
    )
    hired_at_total_seconds: Mapped[int] = mapped_column(BigInteger, nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="1", index=True
    )
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    __table_args__ = (
        UniqueConstraint("company_id", "character_id", name="uq_company_employee_pair"),
    )

    def __repr__(self) -> str:
        return (
            f"CompanyEmployee(id={self.id}, company={self.company_id}, "
            f"char={self.character_id}, role={self.role}, wage={self.daily_wage})"
        )


class CompanyTransaction(IdMixin, TimestampMixin, Base):
    """Audit trail delle operazioni aziendali.

    `amount` è dal punto di vista dell'azienda:
      - positivo = entrata (revenue, capital)
      - negativo = uscita (expense, salary, dividend, tax)
    """

    __tablename__ = "company_transaction"

    company_id: Mapped[int] = mapped_column(
        ForeignKey("company.id", ondelete="CASCADE"), nullable=False, index=True
    )
    kind: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=CompanyTransactionKind.REVENUE.value,
        index=True,
    )
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    character_id: Mapped[int | None] = mapped_column(
        ForeignKey("character.id", ondelete="SET NULL"), nullable=True, index=True
    )
    at_total_seconds: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(256), nullable=False, default="")
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    def __repr__(self) -> str:
        return (
            f"CompanyTransaction(company={self.company_id}, kind={self.kind}, "
            f"amount={self.amount:+d})"
        )


__all__ = ["Company", "CompanyEmployee", "CompanyTransaction"]
