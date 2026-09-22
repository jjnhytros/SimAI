"""Modello SQLAlchemy `Skill`."""

from __future__ import annotations

from sqlalchemy import (
    BigInteger,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from simai.db.base import Base, IdMixin, TimestampMixin
from simai.npc.skills.enums import SkillType


class Skill(IdMixin, TimestampMixin, Base):
    """Abilità di un Character.

    Unique su `(character_id, skill_type)`: al massimo una riga per skill
    per personaggio. Creazione on-demand: la riga esiste solo dopo la prima
    pratica.

    - `level`    : 0..`MAX_SKILL_LEVEL`
    - `progress` : 0.0..1.0 — frazione verso il prossimo livello
    - `talent`   : 0.5..2.0 — moltiplicatore di apprendimento (3.6c)
    """

    __tablename__ = "skill"

    character_id: Mapped[int] = mapped_column(
        ForeignKey("character.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    skill_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    level: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    progress: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    talent: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    last_used_total_seconds: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)

    __table_args__ = (UniqueConstraint("character_id", "skill_type", name="uq_skill_pair"),)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @property
    def type(self) -> SkillType:
        """Tipo di skill come enum."""
        return SkillType(self.skill_type)

    @property
    def is_maxed(self) -> bool:
        """``True`` se level è a `MAX_SKILL_LEVEL`."""
        from simai.npc.skills.enums import MAX_SKILL_LEVEL

        return self.level >= MAX_SKILL_LEVEL

    def __repr__(self) -> str:
        return (
            f"Skill(char={self.character_id}, type={self.skill_type}, "
            f"lvl={self.level}.{int(self.progress * 100):02d}, "
            f"talent={self.talent:.2f})"
        )


__all__ = ["Skill"]
