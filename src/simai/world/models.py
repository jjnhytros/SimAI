from sqlalchemy import Enum as SAEnum
from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
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
    is_player: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    location_id: Mapped[int] = mapped_column(
        ForeignKey("locations.id"), nullable=False
    )

    location: Mapped[Location] = relationship(back_populates="characters")