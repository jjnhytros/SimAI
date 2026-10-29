from sqlalchemy import CheckConstraint, Float, ForeignKey, Integer, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from simai.db.base import Base
from simai.skills.enums import SkillKind


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    character_id: Mapped[int] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"), nullable=False
    )
    kind: Mapped[SkillKind] = mapped_column(SAEnum(SkillKind, native_enum=False), nullable=False)
    level: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    __table_args__ = (
        UniqueConstraint("character_id", "kind", name="uq_skills_character_kind"),
        CheckConstraint("level >= 0.0 AND level <= 100.0", name="ck_skills_level"),
    )
