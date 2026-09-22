"""Modelli del dominio città: servizi, budget, pagamenti tasse."""

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


class PublicService(IdMixin, TimestampMixin, Base):
    """Un servizio pubblico attivo in un quartiere."""

    __tablename__ = "public_service"

    district_id: Mapped[int] = mapped_column(
        ForeignKey("district.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    type: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    location_id: Mapped[int | None] = mapped_column(
        ForeignKey("location.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    quality: Mapped[float] = mapped_column(Float, nullable=False, default=0.6)
    daily_cost: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    coverage_radius: Mapped[int] = mapped_column(Integer, nullable=False, default=40)
    staff_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    __table_args__ = (
        UniqueConstraint("district_id", "type", name="uq_public_service_district_type"),
    )

    def __repr__(self) -> str:
        return (
            f"PublicService(id={self.id}, district={self.district_id}, "
            f"type={self.type}, q={self.quality:.2f})"
        )


class CityBudget(IdMixin, TimestampMixin, Base):
    """Bilancio della città (singleton: una sola riga)."""

    __tablename__ = "city_budget"

    balance: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_revenue: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_expenses: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_revenue_at_total_seconds: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0
    )
    last_expense_at_total_seconds: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0
    )
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    def __repr__(self) -> str:
        return (
            f"CityBudget(balance={self.balance}, "
            f"rev={self.total_revenue}, exp={self.total_expenses})"
        )


class TaxPayment(IdMixin, TimestampMixin, Base):
    """Registro di una tassa pagata da un Character alla città."""

    __tablename__ = "tax_payment"

    character_id: Mapped[int] = mapped_column(
        ForeignKey("character.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    kind: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    at_total_seconds: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    def __repr__(self) -> str:
        return f"TaxPayment(char={self.character_id}, kind={self.kind}, amount={self.amount})"


__all__ = ["CityBudget", "PublicService", "TaxPayment"]
