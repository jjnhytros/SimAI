"""Route: World (districts, lots, location)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from simai.npc.models import Character
from simai.ui.app import templates
from simai.ui.deps import get_db
from simai.world.location_service import (
    get_location,
    list_locations,
    list_objects_in,
)
from simai.world.lot_service import (
    district_summaries,
    get_district,
    lot_summaries,
)

router = APIRouter()


@router.get("/world", response_class=HTMLResponse)
def world_overview(
    request: Request,
    session: Session = Depends(get_db),
) -> HTMLResponse:
    """Overview: districts + lots + location."""
    districts = district_summaries(session)
    lots = lot_summaries(session)
    locations = list_locations(session)
    return templates.TemplateResponse(
        request,
        "world_list.html",
        {
            "districts": districts,
            "lots": lots,
            "locations": locations,
        },
    )


@router.get("/world/districts", response_class=HTMLResponse)
def districts_list(
    request: Request,
    session: Session = Depends(get_db),
) -> HTMLResponse:
    """Lista quartieri."""
    districts = district_summaries(session)
    return templates.TemplateResponse(
        request,
        "districts_list.html",
        {"districts": districts},
    )


@router.get("/world/districts/{district_id}", response_class=HTMLResponse)
def district_detail(
    request: Request,
    district_id: int,
    session: Session = Depends(get_db),
) -> HTMLResponse:
    """Dettaglio quartiere + lotti."""
    d = get_district(session, district_id)
    if d is None:
        raise HTTPException(status_code=404, detail=f"District {district_id} non trovato")
    lots = lot_summaries(session, district_id=district_id)
    return templates.TemplateResponse(
        request,
        "district_detail.html",
        {"d": d, "lots": lots},
    )


@router.get("/world/lots", response_class=HTMLResponse)
def lots_list(
    request: Request,
    district_id: int | None = None,
    session: Session = Depends(get_db),
) -> HTMLResponse:
    """Lista lotti."""
    lots = lot_summaries(session, district_id=district_id)
    return templates.TemplateResponse(
        request,
        "lots_list.html",
        {"lots": lots, "district_id": district_id},
    )


@router.get("/world/locations/{location_id}", response_class=HTMLResponse)
def location_detail(
    request: Request,
    location_id: int,
    session: Session = Depends(get_db),
) -> HTMLResponse:
    """Dettaglio location."""
    loc = get_location(session, location_id)
    if loc is None:
        raise HTTPException(status_code=404, detail=f"Location {location_id} non trovata")
    objects = list_objects_in(session, location_id)
    npcs_here = list(
        session.query(Character).filter(
            Character.location_id == location_id,
            Character.is_alive.is_(True),
        )
    )
    return templates.TemplateResponse(
        request,
        "world_detail.html",
        {"loc": loc, "objects": objects, "npcs_here": npcs_here},
    )
