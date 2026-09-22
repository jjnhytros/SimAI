"""Dependencies FastAPI condivise."""

from __future__ import annotations

from collections.abc import Iterator

from fastapi import Request
from sqlalchemy.orm import Session

from simai.db.session import get_session_factory


def get_db() -> Iterator[Session]:
    """Dependency: sessione SQLAlchemy auto-chiusa a fine richiesta."""
    factory = get_session_factory()
    session = factory()
    try:
        yield session
    finally:
        session.close()


def get_current_tick(request: Request) -> int:
    """Dependency: tick corrente della simulazione (letto da query param)."""
    raw = request.query_params.get("at_tick")
    if raw is None:
        return 0
    try:
        return max(0, int(raw))
    except ValueError:
        return 0


__all__ = ["get_current_tick", "get_db"]
