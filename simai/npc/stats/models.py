"""Modello `PopulationCensus` — snapshot mensile della popolazione."""

from __future__ import annotations

from typing import Any

from sqlalchemy import BigInteger, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from simai.db.base import Base, IdMixin, TimestampMixin


class PopulationCensus(IdMixin, TimestampMixin, Base):
    """Censimento mensile della popolazione Anthalys.

    Unique su `(year, month)`: un solo census per mese. Le chiamate
    ripetute nello stesso mese aggiornano il record (upsert).
    """

    __tablename__ = "population_census"

    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    month: Mapped[int] = mapped_column(Integer, nullable=False)

    total_alive: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_male: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_female: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_intersex: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    births_this_month: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    deaths_this_month: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    pediatric_breakdown_json: Mapped[dict[str, Any]] = mapped_column(
        JSON, default=dict, nullable=False
    )
    psychosocial_breakdown_json: Mapped[dict[str, Any]] = mapped_column(
        JSON, default=dict, nullable=False
    )

    recorded_at_total_seconds: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)

    __table_args__ = (UniqueConstraint("year", "month", name="uq_population_census_month"),)

    def __repr__(self) -> str:
        return (
            f"PopulationCensus({self.year}-{self.month:02d}, "
            f"alive={self.total_alive}, births={self.births_this_month}, "
            f"deaths={self.deaths_this_month})"
        )


__all__ = ["PopulationCensus"]
