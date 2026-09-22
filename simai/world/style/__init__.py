"""Package `simai.world.style` — pavimenti, rivestimenti."""

from simai.world.style.enums import (
    MAX_STYLE_UPDATES_PER_DAY,
    StyleKind,
    WallSide,
)
from simai.world.style.models import FloorTile, StyleCatalog, WallCovering
from simai.world.style.seed import STYLE_ENTRIES, seed_style_catalog
from simai.world.style.service import StyleApplyResult, StyleError, StyleService

__all__ = [
    "MAX_STYLE_UPDATES_PER_DAY",
    "STYLE_ENTRIES",
    "FloorTile",
    "StyleApplyResult",
    "StyleCatalog",
    "StyleError",
    "StyleKind",
    "StyleService",
    "WallCovering",
    "WallSide",
    "seed_style_catalog",
]
