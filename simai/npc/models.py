"""Modello SQLAlchemy di Character."""

from __future__ import annotations

from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from simai.db.base import Base, IdMixin, TimestampMixin


class Character(IdMixin, TimestampMixin, Base):
    """Un personaggio di Anthalys (giocatore o NPC).

    Campi tipizzati per query/indici; campi JSON per attributi estensibili
    (aspetto, tratti, aspirazioni, genoma futuro).

    L'età non è memorizzata: si calcola da `birth_total_seconds` e dal tempo
    corrente della simulazione. `life_stage_*` sono cache ricalcolabili.
    """

    __tablename__ = "character"

    # --- Identità ---
    first_name: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    last_name: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    sex: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    gender: Mapped[str] = mapped_column(String(32), nullable=False, default="unspecified")

    # --- Nascita / morte ---
    birth_total_seconds: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    birth_iso: Mapped[str] = mapped_column(String(20), nullable=False)
    death_total_seconds: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True)
    death_iso: Mapped[str | None] = mapped_column(String(20), nullable=True)
    death_cause: Mapped[str | None] = mapped_column(String(16), nullable=True, index=True)

    # --- Stato corrente ---
    is_alive: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    life_stage_pediatric: Mapped[str] = mapped_column(String(24), nullable=False, index=True)
    life_stage_psychosocial: Mapped[str] = mapped_column(String(24), nullable=False, index=True)

    # --- Posizione ---
    location_id: Mapped[int | None] = mapped_column(
        ForeignKey("location.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # --- Riproducibilità ---
    master_seed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # --- Attributi estensibili (JSON) ---
    appearance_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    traits_json: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    aspirations_json: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    genome_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    attributes_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    # --- Economia (Chunk 3.4c) ---
    athel_balance: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0, server_default="0"
    )

    # --- Bisogni / Umore / Azione corrente (Chunk 3.2) ---
    needs_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    mood_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    current_action_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    last_ai_tick: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __repr__(self) -> str:
        return (
            f"Character(id={self.id}, name={self.full_name!r}, "
            f"sex={self.sex!r}, alive={self.is_alive})"
        )


__all__ = ["Character"]
