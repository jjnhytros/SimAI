from sqlalchemy import (
    CheckConstraint,
    Float,
    ForeignKey,
    Integer,
    UniqueConstraint,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from simai.db.base import Base
from simai.relationships.enums import RelationshipKind


class Relationship(Base):
    __tablename__ = "relationships"
    __table_args__ = (
        UniqueConstraint(
            "from_character_id",
            "to_character_id",
            "kind",
            name="uq_relationships_from_to_kind",
        ),
        CheckConstraint(
            "from_character_id != to_character_id",
            name="ck_relationships_distinct",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    from_character_id: Mapped[int] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"), nullable=False
    )
    to_character_id: Mapped[int] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"), nullable=False
    )
    kind: Mapped[RelationshipKind] = mapped_column(
        SAEnum(RelationshipKind, native_enum=False), nullable=False
    )
    strength: Mapped[float] = mapped_column(Float, nullable=False, default=50.0)
