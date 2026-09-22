"""Modello `CoreVersion` — storia delle versioni di SimAI applicate al DB."""

from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from simai.db.base import Base, IdMixin


class CoreVersion(IdMixin, Base):
    """Versione di SimAI applicata al database.

    Una riga per ogni versione applicata (es. ``0.1.0.dev0``).
    Consente di tracciare la storia delle versioni e validare compatibilità
    con i salvataggi.
    """

    __tablename__ = "core_version"

    version: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        index=True,
    )
    git_sha: Mapped[str | None] = mapped_column(String(40), nullable=True)
    applied_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=func.now(),
        server_default=func.now(),
    )

    def __repr__(self) -> str:
        return f"CoreVersion(id={self.id}, version={self.version!r}, git_sha={self.git_sha!r})"
