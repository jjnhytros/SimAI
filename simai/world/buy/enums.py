"""Enum del dominio buy mode."""

from __future__ import annotations

from enum import StrEnum
from typing import Final


class ObjectCategory(StrEnum):
    """Categoria di oggetto nel catalogo."""

    FURNITURE = "FURNITURE"
    APPLIANCE = "APPLIANCE"
    DECOR = "DECOR"
    PLANT = "PLANT"
    PLUMBING = "PLUMBING"
    ELECTRONICS = "ELECTRONICS"
    LIGHTING = "LIGHTING"
    STORAGE = "STORAGE"


#: Rotazioni ammesse (gradi).
ALLOWED_ROTATIONS: Final[tuple[int, ...]] = (0, 90, 180, 270)

#: Limite massimo di oggetti piazzabili per lotto (per performance UI).
MAX_OBJECTS_PER_LOT: Final[int] = 200


__all__ = [
    "ALLOWED_ROTATIONS",
    "MAX_OBJECTS_PER_LOT",
    "ObjectCategory",
]
