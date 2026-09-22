"""Route: Live (SSE-like polling con htmx)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from simai.core.anthalys_datetime import AnthalysDateTime
from simai.core.time_manager import TimeManager
from simai.economy.ledger import JournalEntry
from simai.npc.models import Character
from simai.npc.reflection.models import ReflectionEntry
from simai.ui.app import templates
from simai.ui.deps import get_db

router = APIRouter()


def _current_datetime(tick: int) -> AnthalysDateTime:
    from simai.config.settings import get_settings

    settings = get_settings()
    start = AnthalysDateTime(
        settings.starting_year,
        settings.starting_month,
        settings.starting_day,
    )
    tm = TimeManager(start=start, tick_minutes=settings.tick_minutes)
    tm.advance_ticks(tick)
    return tm.current


@router.get("/live", response_class=HTMLResponse)
def live_page(
    request: Request,
    session: Session = Depends(get_db),
) -> HTMLResponse:
    """Pagina live (auto-refresh via htmx)."""
    return templates.TemplateResponse(request, "live.html", {})


@router.get("/live/fragment", response_class=HTMLResponse)
def live_fragment(
    request: Request,
    session: Session = Depends(get_db),
) -> HTMLResponse:
    """Frammento HTML aggiornato (polled da htmx)."""
    max_tick = int(session.scalar(select(func.max(Character.last_ai_tick))) or 0)
    current_dt = _current_datetime(max_tick)

    alive = int(
        session.scalar(
            select(func.count()).select_from(Character).where(Character.is_alive.is_(True))
        )
        or 0
    )

    recent_reflections = list(
        session.scalars(
            select(ReflectionEntry).order_by(ReflectionEntry.at_total_seconds.desc()).limit(8)
        )
    )

    # Ultime entry del ledger (sostituiscono le vecchie Transaction)
    recent_entries = list(
        session.scalars(
            select(JournalEntry).order_by(JournalEntry.at_total_seconds.desc()).limit(8)
        )
    )

    return templates.TemplateResponse(
        request,
        "partials/live_fragment.html",
        {
            "current_dt": str(current_dt),
            "current_tick": max_tick,
            "alive": alive,
            "reflections": recent_reflections,
            "transactions": recent_entries,
        },
    )
