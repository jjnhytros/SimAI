"""Route: Città (servizi, bilancio, soddisfazione)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session

from simai.city import (
    CityService,
    SatisfactionService,
)
from simai.city.models import TaxPayment
from simai.npc.models import Character
from simai.ui.app import templates
from simai.ui.deps import get_db

router = APIRouter()


@router.get("/city", response_class=HTMLResponse)
def city_dashboard(
    request: Request,
    session: Session = Depends(get_db),
) -> HTMLResponse:
    """Dashboard città."""
    from sqlalchemy import select

    budget = CityService.get_budget(session)
    services = CityService.all_services(session)
    satisfaction = SatisfactionService.compute_all(session)

    # Ultimi pagamenti tasse
    recent_taxes = list(
        session.scalars(select(TaxPayment).order_by(TaxPayment.at_total_seconds.desc()).limit(15))
    )
    tax_rows: list[dict[str, object]] = []
    for p in recent_taxes:
        c = session.get(Character, p.character_id)
        tax_rows.append(
            {
                "id": p.id,
                "character": c.full_name if c else "?",
                "kind": p.kind,
                "amount": p.amount,
            }
        )

    return templates.TemplateResponse(
        request,
        "city.html",
        {
            "budget": budget,
            "services": services,
            "satisfaction": satisfaction,
            "taxes": tax_rows,
        },
    )


@router.get("/api/city/moodlets.json")
def api_city_moodlets(
    session: Session = Depends(get_db),
) -> JSONResponse:
    """Ritorna i moodlet città attivi sui cittadini."""
    from sqlalchemy import select

    from simai.npc.mood import MoodState

    chars = list(session.scalars(select(Character).where(Character.is_alive.is_(True))))
    rows: list[dict[str, object]] = []
    for c in chars:
        mood = MoodState.from_dict(c.mood_json or {})
        for m in mood.moodlets:
            if m.source.startswith("city_"):
                rows.append(
                    {
                        "character_id": c.id,
                        "character_name": c.full_name,
                        "moodlet": m.name,
                        "delta": m.happiness_delta,
                        "remaining_ticks": m.remaining_ticks,
                    }
                )
    return JSONResponse({"moodlets": rows})
