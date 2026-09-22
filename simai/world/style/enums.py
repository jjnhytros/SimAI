"""Enum del dominio style mode."""

from __future__ import annotations

from enum import StrEnum
from typing import Final


class StyleKind(StrEnum):
    """Tipo di stile."""

    FLOOR = "FLOOR"
    WALL = "WALL"


class WallSide(StrEnum):
    """Lato del muro (per ora solo INTERIOR; EXTERIOR predisposto)."""

    INTERIOR = "INTERIOR"
    EXTERIOR = "EXTERIOR"


#: Cap di applicazioni di stile per giorno (protezione).
MAX_STYLE_UPDATES_PER_DAY: Final[int] = 500


__all__ = ["MAX_STYLE_UPDATES_PER_DAY", "StyleKind", "WallSide"]
