"""App factory FastAPI per la UI di SimAI."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from simai.__version__ import __version__

UI_DIR = Path(__file__).parent
TEMPLATES_DIR = UI_DIR / "templates"
STATIC_DIR = UI_DIR / "static"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Inject globali nei template
templates.env.globals["simai_version"] = __version__


def create_app() -> FastAPI:
    """Costruisce l'app FastAPI."""
    from simai.ui.routes import (
        aion_routes,
        build_routes,
        city_routes,
        infrastructure_routes,
        transport_routes,
    )
    from simai.ui.routes.api import router as api_router
    from simai.ui.routes.dashboard import router as dashboard_router
    from simai.ui.routes.economy_routes import router as economy_router
    from simai.ui.routes.live import router as live_router
    from simai.ui.routes.npcs import router as npcs_router
    from simai.ui.routes.world_routes import router as world_router

    app = FastAPI(
        title="SimAI UI",
        version=__version__,
        docs_url="/api/docs",
        redoc_url=None,
    )

    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    app.include_router(dashboard_router)
    app.include_router(npcs_router)
    app.include_router(world_router)
    app.include_router(economy_router)
    app.include_router(live_router)
    app.include_router(api_router, prefix="/api")
    app.include_router(build_routes.router)
    app.include_router(city_routes.router)
    app.include_router(infrastructure_routes.router)
    app.include_router(transport_routes.router)
    app.include_router(aion_routes.router)

    return app


__all__ = ["STATIC_DIR", "TEMPLATES_DIR", "create_app", "templates"]
