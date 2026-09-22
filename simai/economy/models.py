"""Modelli SQLAlchemy del dominio economia."""

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


class Job(IdMixin, TimestampMixin, Base):
    """Impiego di un Character. Uno solo per personaggio (unique su character_id)."""

    __tablename__ = "job"

    character_id: Mapped[int] = mapped_column(
        ForeignKey("character.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    workplace_id: Mapped[int | None] = mapped_column(
        ForeignKey("location.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    job_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(64), nullable=False)
    daily_wage: Mapped[int] = mapped_column(Integer, nullable=False)
    since_total_seconds: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)

    # --- Skill requirements (Chunk 3.6c) ---
    required_skill_type: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    min_skill_level: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    #: Scala del wage per skill level: `effective = wage * (1 + scale * level)`.
    wage_skill_scale: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0, server_default="0.0"
    )
    #: Promozione automatica a questo livello (0 = disabilitata).
    promotion_skill_level: Mapped[int] = mapped_column(
        Integer, nullable=False, default=10, server_default="10"
    )
    #: Titolo promosso (se `promotion_skill_level > 0`).
    promoted_title: Mapped[str | None] = mapped_column(String(64), nullable=True)

    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    __table_args__ = (UniqueConstraint("character_id", name="uq_job_character"),)

    def effective_daily_wage(self, skill_level: int) -> int:
        """Wage effettivo dato il livello della skill richiesta."""
        base = int(self.daily_wage)
        scale = float(self.wage_skill_scale)
        if scale <= 0 or skill_level <= 0:
            return base
        return int(base * (1.0 + scale * skill_level))

    def __repr__(self) -> str:
        return (
            f"Job(char={self.character_id}, type={self.job_type}, "
            f"wage={self.daily_wage}/day, active={self.is_active})"
        )


class ShopItem(IdMixin, TimestampMixin, Base):
    """Voce di catalogo di un negozio (Location di tipo SHOP)."""

    __tablename__ = "shop_item"

    location_id: Mapped[int] = mapped_column(
        ForeignKey("location.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    item_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    item_name: Mapped[str] = mapped_column(String(128), nullable=False)
    base_price: Mapped[int] = mapped_column(Integer, nullable=False)
    current_price: Mapped[int] = mapped_column(Integer, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=-1)  # -1 = illimitato
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    __table_args__ = (UniqueConstraint("location_id", "item_type", name="uq_shop_item_pair"),)

    def __repr__(self) -> str:
        stock_str = "∞" if self.stock < 0 else str(self.stock)
        return (
            f"ShopItem(loc={self.location_id}, type={self.item_type}, "
            f"price={self.current_price}, stock={stock_str})"
        )


__all__ = ["Job", "ShopItem"]
