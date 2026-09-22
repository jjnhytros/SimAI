"""Route: dashboard principale."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from simai.core.anthalys_datetime import AnthalysDateTime
from simai.core.time_manager import TimeManager
from simai.npc.models import Character
from simai.npc.skills.models import Skill
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


@router.get("/", response_class=HTMLResponse)
def dashboard(
    request: Request,
    session: Session = Depends(get_db),
) -> HTMLResponse:
    """Dashboard: stato attuale della simulazione."""
    max_tick = int(session.scalar(select(func.max(Character.last_ai_tick))) or 0)
    current_dt = _current_datetime(max_tick)

    alive = int(
        session.scalar(
            select(func.count()).select_from(Character).where(Character.is_alive.is_(True))
        )
        or 0
    )
    dead = int(
        session.scalar(
            select(func.count()).select_from(Character).where(Character.is_alive.is_(False))
        )
        or 0
    )
    n_skills = int(session.scalar(select(func.count()).select_from(Skill)) or 0)
    total_balance = int(
        session.scalar(
            select(func.coalesce(func.sum(Character.athel_balance), 0)).where(
                Character.is_alive.is_(True)
            )
        )
        or 0
    )

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "current_dt": str(current_dt),
            "current_tick": max_tick,
            "stats": {
                "alive": alive,
                "dead": dead,
                "skills": n_skills,
                "total_balance": total_balance,
            },
        },
    )
