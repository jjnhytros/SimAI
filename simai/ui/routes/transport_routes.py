"""Route: Trasporti (veicoli, linee)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.city.transport import (
    TransitService,
    TransportService,
    Vehicle,
)
from simai.config.settings import get_settings
from simai.core.anthalys_datetime import AnthalysDateTime
from simai.core.time_manager import TimeManager
from simai.npc.models import Character
from simai.ui.app import templates
from simai.ui.deps import get_db
from simai.world.models import Location

router = APIRouter()


@router.get("/transport", response_class=HTMLResponse)
def transport_dashboard(
    request: Request,
    session: Session = Depends(get_db),
) -> HTMLResponse:
    """Dashboard trasporti."""
    routes = TransportService.all_routes(session)
    route_rows: list[dict[str, object]] = []
    for r in routes:
        stops = TransportService.stops_of(session, r.id)
        stop_names = []
        for s in stops:
            loc = session.get(Location, s.location_id)
            if loc is not None:
                stop_names.append(loc.name)
        route_rows.append(
            {
                "id": r.id,
                "name": r.name,
                "route_type": r.route_type,
                "base_fare": r.base_fare,
                "speed": r.speed_cells_per_tick,
                "stops": stop_names,
            }
        )

    vehicles = list(session.scalars(select(Vehicle).order_by(Vehicle.id)))
    vehicle_rows: list[dict[str, object]] = []
    for v in vehicles:
        c = session.get(Character, v.owner_id)
        loc = session.get(Location, v.location_id) if v.location_id else None
        vehicle_rows.append(
            {
                "id": v.id,
                "owner": c.full_name if c else "?",
                "owner_id": v.owner_id,
                "type": v.vehicle_type,
                "fuel": v.fuel,
                "condition": v.condition,
                "location": loc.name if loc else "—",
            }
        )

    return templates.TemplateResponse(
        request,
        "transport.html",
        {"routes": route_rows, "vehicles": vehicle_rows},
    )


@router.get("/api/transport/plan.json")
def api_transport_plan(
    character_id: int,
    from_location_id: int,
    to_location_id: int,
    session: Session = Depends(get_db),
) -> dict[str, object]:
    """Ritorna i piani di viaggio tra due location."""
    c = session.get(Character, character_id)
    if c is None:
        raise HTTPException(status_code=404, detail=f"Character {character_id} non trovato")
    plans = TransportService.plan_all(
        session,
        c,
        from_location_id=from_location_id,
        to_location_id=to_location_id,
    )
    plans.sort(key=lambda p: (p.duration_ticks, p.cost))
    return {
        "plans": [
            {
                "mode": p.mode.value,
                "distance": p.distance,
                "duration_ticks": p.duration_ticks,
                "cost": p.cost,
                "fuel_needed": p.fuel_needed,
                "description": p.description,
                "route_id": p.route_id,
            }
            for p in plans
        ]
    }


# ---------------------------------------------------------------------------
# Live transits (Chunk 4.10c)
# ---------------------------------------------------------------------------


def _current_seconds_from_tick(at_tick: int) -> int:
    """Converte un tick Anthalys in secondi totali."""
    settings = get_settings()
    start = AnthalysDateTime(
        settings.starting_year,
        settings.starting_month,
        settings.starting_day,
    )
    tm = TimeManager(start=start, tick_minutes=settings.tick_minutes)
    tm.advance_ticks(at_tick)
    return tm.current.to_total_seconds()


@router.get("/transport/transits", response_class=HTMLResponse)
def transits_page(
    request: Request,
    session: Session = Depends(get_db),
) -> HTMLResponse:
    """Pagina live dei transiti."""
    routes = TransportService.all_routes(session)
    route_rows = []
    for r in routes:
        stops = TransportService.stops_of(session, r.id)
        points: list[dict[str, object]] = []
        for s in stops:
            loc = session.get(Location, s.location_id)
            if loc is not None:
                cx, cy = loc.center()
                points.append({"x": cx, "y": cy, "name": loc.name, "id": loc.id})
        route_rows.append(
            {
                "id": r.id,
                "name": r.name,
                "route_type": r.route_type,
                "points": points,
            }
        )
    return templates.TemplateResponse(
        request,
        "transits.html",
        {"routes": route_rows},
    )


@router.get("/api/transport/transits.json")
def api_transits_live(
    at_tick: int = 0,
    session: Session = Depends(get_db),
) -> JSONResponse:
    """Ritorna i transiti attivi con progresso calcolato."""
    now_seconds = _current_seconds_from_tick(at_tick)
    jobs = TransitService.all_active(session)
    items = []
    for j in jobs:
        c = session.get(Character, j.character_id)
        from_loc = session.get(Location, j.from_location_id)
        to_loc = session.get(Location, j.to_location_id)
        progress = TransitService.compute_progress(j, now_seconds=now_seconds)
        items.append(
            {
                "job_id": j.id,
                "character_id": j.character_id,
                "character_name": c.full_name if c else "?",
                "mode": j.mode,
                "from_id": j.from_location_id,
                "from_name": from_loc.name if from_loc else "?",
                "from_xy": list(from_loc.center()) if from_loc else None,
                "to_id": j.to_location_id,
                "to_name": to_loc.name if to_loc else "?",
                "to_xy": list(to_loc.center()) if to_loc else None,
                "started_at": j.started_at_total_seconds,
                "arrives_at": j.arrives_at_total_seconds,
                "progress": progress["progress"],
                "current_leg_index": progress["current_leg_index"],
                "legs": progress["legs"],
                "cost_paid": j.cost_paid,
            }
        )
    return JSONResponse(
        {
            "now_seconds": now_seconds,
            "count": len(items),
            "transits": items,
        }
    )


@router.get("/api/transport/routes.json")
def api_routes_geometry(
    session: Session = Depends(get_db),
) -> JSONResponse:
    """Geometria delle linee (per canvas): punti (x,y) e metadati."""
    routes = TransportService.all_routes(session)
    items: list[dict[str, object]] = []
    for r in routes:
        stops = TransportService.stops_of(session, r.id)
        points: list[list[float]] = []
        for s in stops:
            loc = session.get(Location, s.location_id)
            if loc is not None:
                cx, cy = loc.center()
                points.append([cx, cy])
        items.append(
            {
                "id": r.id,
                "name": r.name,
                "route_type": r.route_type,
                "points": points,
            }
        )
    return JSONResponse({"routes": items})
