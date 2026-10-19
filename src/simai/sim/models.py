from sqlalchemy import BigInteger, Integer
from sqlalchemy.orm import Mapped, mapped_column

from simai.db.base import Base


class SimState(Base):
    __tablename__ = "sim_state"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tick_index: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        nullable=False,
        default=0,
    )
    master_seed: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        nullable=False,
        default=42,
    )
