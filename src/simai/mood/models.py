from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from simai.db.base import Base
from simai.mood.enums import MoodletKind
from simai.needs.enums import NeedKind


class Moodlet(Base):
    __tablename__ = "moodlets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    character_id: Mapped[int] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"), nullable=False
    )
    kind: Mapped[MoodletKind] = mapped_column(
        SAEnum(MoodletKind, native_enum=False), nullable=False
    )
    need: Mapped[NeedKind | None] = mapped_column(
        SAEnum(NeedKind, native_enum=False), nullable=True
    )
    started_at_tick: Mapped[int] = mapped_column(Integer, nullable=False)
    expires_at_tick: Mapped[int] = mapped_column(Integer, nullable=False)
