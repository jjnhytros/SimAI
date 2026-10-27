from sqlalchemy import (
    Enum as SAEnum,
)
from sqlalchemy import (
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from simai.actions.enums import ActionKind
from simai.db.base import Base
from simai.economy.enums import JobTitle, TransactionKind


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    character_id: Mapped[int] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    title: Mapped[JobTitle] = mapped_column(SAEnum(JobTitle, native_enum=False), nullable=False)
    location_key: Mapped[str] = mapped_column(String(32), nullable=False)
    daily_wage: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    schedule_start_tick: Mapped[int] = mapped_column(Integer, nullable=False, default=8)
    schedule_end_tick: Mapped[int] = mapped_column(Integer, nullable=False, default=16)
    break_start_tick: Mapped[int | None] = mapped_column(Integer, nullable=True)
    break_end_tick: Mapped[int | None] = mapped_column(Integer, nullable=True)


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tick_index: Mapped[int] = mapped_column(Integer, nullable=False)
    from_character_id: Mapped[int | None] = mapped_column(
        ForeignKey("characters.id", ondelete="SET NULL"),
        nullable=True,
    )
    to_character_id: Mapped[int | None] = mapped_column(
        ForeignKey("characters.id", ondelete="SET NULL"),
        nullable=True,
    )
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    kind: Mapped[TransactionKind] = mapped_column(
        SAEnum(TransactionKind, native_enum=False), nullable=False
    )
    note: Mapped[str] = mapped_column(String(128), nullable=False, default="")


class ShopItem(Base):
    __tablename__ = "shop_items"
    __table_args__ = (
        UniqueConstraint(
            "location_key",
            "action_kind",
            name="uq_shop_items_location_action",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    location_key: Mapped[str] = mapped_column(String(32), nullable=False)
    action_kind: Mapped[ActionKind] = mapped_column(
        SAEnum(ActionKind, native_enum=False), nullable=False
    )
    price: Mapped[float] = mapped_column(Float, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=-1)
