from sqlalchemy import Enum as SAEnum
from sqlalchemy import Float, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from simai.db.base import Base
from simai.needs.enums import NeedKind


class Need(Base):
    __tablename__ = "needs"
    __table_args__ = (UniqueConstraint("character_id", "kind", name="uq_needs_character_kind"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    character_id: Mapped[int] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"), nullable=False
    )
    kind: Mapped[NeedKind] = mapped_column(SAEnum(NeedKind, native_enum=False), nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)
