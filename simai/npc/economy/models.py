"""Modelli SQLAlchemy del dominio economico."""

from __future__ import annotations

from sqlalchemy import BigInteger, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from simai.db.base import Base, IdMixin, TimestampMixin


class CharacterOwnedLocation(IdMixin, TimestampMixin, Base):
    """Possesso di una Location da parte di un Character.

    `share` è la frazione di proprietà (default 1.0). Supporta quote
    future (es. comproprietà tra coniugi, soci).
    """

    __tablename__ = "character_owned_location"

    character_id: Mapped[int] = mapped_column(
        ForeignKey("character.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    location_id: Mapped[int] = mapped_column(
        ForeignKey("location.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    share: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    since_total_seconds: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    __table_args__ = (
        UniqueConstraint("character_id", "location_id", name="uq_owned_location_pair"),
    )

    def __repr__(self) -> str:
        return (
            f"CharacterOwnedLocation(char={self.character_id}, "
            f"loc={self.location_id}, share={self.share:.2f})"
        )


__all__ = ["CharacterOwnedLocation"]
