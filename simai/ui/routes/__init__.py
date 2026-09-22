"""Router FastAPI della UI SimAI."""

from simai.ui.routes import (
    aion_routes,
    build_routes,
    city_routes,
    infrastructure_routes,
    transport_routes,
)

__all__ = [
    "aion_routes",
    "build_routes",
    "city_routes",
    "infrastructure_routes",
    "transport_routes",
]
