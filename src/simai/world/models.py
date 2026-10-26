from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from simai.db.base import Base
from simai.world.enums import LocationKind


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    kind: Mapped[LocationKind] = mapped_column(
        SAEnum(LocationKind, native_enum=False), nullable=False
    )
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=8)

    characters: Mapped[list["Character"]] = relationship(
        back_populates="location",
    )


class Character(Base):
    __tablename__ = "characters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    age_years: Mapped[int] = mapped_column(Integer, nullable=False)
    is_player: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    mood: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)
    low_intimacy_streak: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    balance: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"), nullable=False)
    location: Mapped[Location] = relationship(back_populates="characters")
    home_location_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
