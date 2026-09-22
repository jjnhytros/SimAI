"""Route: Infrastrutture (strade, lampioni) — editor griglia mondiale."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session

from simai.city.infrastructure import (
    LIGHT_COSTS,
    LIGHT_RADII,
    ROAD_COSTS,
    InfrastructureError,
    InfrastructureService,
    LightType,
    RoadType,
)
from simai.ui.app import templates
from simai.ui.deps import get_db

router = APIRouter()


@router.get("/world/infrastructure", response_class=HTMLResponse)
def infrastructure_page(
    request: Request,
    session: Session = Depends(get_db),
) -> HTMLResponse:
    """Editor infrastrutture (canvas)."""
    return templates.TemplateResponse(request, "infrastructure.html", {})


@router.get("/api/infrastructure/layout.json")
def api_infra_layout(
    x0: int = 0,
    y0: int = 0,
    x1: int = 50,
    y1: int = 50,
    session: Session = Depends(get_db),
) -> JSONResponse:
    """Layout infrastruttura in un bbox."""
    roads = InfrastructureService.roads_in_bbox(session, x0=x0, y0=y0, x1=x1, y1=y1)
    lights = InfrastructureService.lights_in_bbox(session, x0=x0, y0=y0, x1=x1, y1=y1)
    return JSONResponse(
        {
            "bounds": {"x0": x0, "y0": y0, "x1": x1, "y1": y1},
            "roads": [
                {
                    "x": r.x,
                    "y": r.y,
                    "road_type": r.road_type,
                    "condition": r.condition,
                }
                for r in roads
            ],
            "lights": [
                {
                    "x": light.x,
                    "y": light.y,
                    "light_type": light.light_type,
                    "radius": light.radius,
                    "condition": light.condition,
                    "is_active": light.is_active,
                }
                for light in lights
            ],
        }
    )


@router.post("/api/infrastructure/road")
def api_place_road(
    payload: dict[str, Any] = Body(...),
    session: Session = Depends(get_db),
) -> JSONResponse:
    try:
        x = int(payload["x"])
        y = int(payload["y"])
        road_type = RoadType(str(payload.get("road_type", "STREET")))
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=f"Payload non valido: {exc}") from exc
    try:
        result = InfrastructureService.place_road(session, x=x, y=y, road_type=road_type)
    except InfrastructureError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not result.ok:
        raise HTTPException(status_code=400, detail=result.reason)
    session.commit()
    return JSONResponse({"ok": True})


@router.delete("/api/infrastructure/road/{x}/{y}")
def api_remove_road(x: int, y: int, session: Session = Depends(get_db)) -> JSONResponse:
    ok = InfrastructureService.remove_road(session, x=x, y=y)
    session.commit()
    return JSONResponse({"ok": ok})


@router.post("/api/infrastructure/light")
def api_place_light(
    payload: dict[str, Any] = Body(...),
    session: Session = Depends(get_db),
) -> JSONResponse:
    try:
        x = int(payload["x"])
        y = int(payload["y"])
        lt = LightType(str(payload.get("light_type", "STANDARD")))
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=f"Payload non valido: {exc}") from exc
    try:
        result = InfrastructureService.place_light(session, x=x, y=y, light_type=lt)
    except InfrastructureError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not result.ok:
        raise HTTPException(status_code=400, detail=result.reason)
    session.commit()
    return JSONResponse({"ok": True})


@router.delete("/api/infrastructure/light/{x}/{y}")
def api_remove_light(x: int, y: int, session: Session = Depends(get_db)) -> JSONResponse:
    ok = InfrastructureService.remove_light(session, x=x, y=y)
    session.commit()
    return JSONResponse({"ok": ok})


@router.get("/api/infrastructure/coverage.json")
def api_coverage_grid(
    x0: int = 0,
    y0: int = 0,
    x1: int = 20,
    y1: int = 20,
    session: Session = Depends(get_db),
) -> JSONResponse:
    """Copertura luminosa cella per cella in un bbox."""
    cells: list[dict[str, object]] = []
    for xx in range(x0, x1 + 1):
        for yy in range(y0, y1 + 1):
            cov = InfrastructureService.lighting_coverage_at(session, x=xx, y=yy)
            if cov > 0:
                cells.append({"x": xx, "y": yy, "coverage": cov})
    return JSONResponse({"cells": cells})


@router.get("/api/infrastructure/costs.json")
def api_costs() -> JSONResponse:
    return JSONResponse(
        {
            "roads": {k.value: v for k, v in ROAD_COSTS.items()},
            "lights": {k.value: v for k, v in LIGHT_COSTS.items()},
            "light_radii": {k.value: v for k, v in LIGHT_RADII.items()},
        }
    )
