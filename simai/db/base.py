"""Base dichiarativa SQLAlchemy 2.0 e mixin comuni."""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base per tutti i modelli SimAI.

    Convenzioni:
      - PK: `id` BIGINT autoincrement (IdMixin).
      - Timestamps: `created_at`, `updated_at` UTC naive (TimestampMixin).
    """


class IdMixin:
    """Mixin che aggiunge una PK autoincrementale.

    Usa `BigInteger` su PostgreSQL e `Integer` su SQLite: SQLite richiede
    esattamente `INTEGER PRIMARY KEY` per l'autoincrement nativo (una
    colonna dichiarata `BIGINT` non riceve l'AUTOINCREMENT implicito).
    """

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )


class TimestampMixin:
    """Mixin che aggiunge `created_at` / `updated_at` UTC naive."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=func.now(),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
        server_default=func.now(),
    )
