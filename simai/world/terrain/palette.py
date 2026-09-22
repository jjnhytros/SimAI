"""Palette colori per TerrainType (usata da UI)."""

from __future__ import annotations

from typing import Final

from simai.world.terrain.enums import TerrainType

#: Colore base (livello 0) per tipo di terreno.
TERRAIN_COLORS: Final[dict[TerrainType, str]] = {
    TerrainType.GRASS: "#4a7a3a",
    TerrainType.DIRT: "#6b5236",
    TerrainType.SAND: "#d8c98a",
    TerrainType.STONE: "#7a7a7a",
    TerrainType.PAVEMENT: "#a8a8a8",
    TerrainType.FARMLAND: "#5f4a2a",
    TerrainType.WATER: "#1a5fa0",
    TerrainType.ROCK: "#4d4d4d",
}

#: Etichette italiane.
TERRAIN_LABELS: Final[dict[TerrainType, str]] = {
    TerrainType.GRASS: "Erba",
    TerrainType.DIRT: "Terra",
    TerrainType.SAND: "Sabbia",
    TerrainType.STONE: "Pietra",
    TerrainType.PAVEMENT: "Pavimentazione",
    TerrainType.FARMLAND: "Terreno agricolo",
    TerrainType.WATER: "Acqua",
    TerrainType.ROCK: "Roccia",
}


def lighten_hex(hex_color: str, elevation: int, max_elev: int = 3) -> str:
    """Ritorna un colore più chiaro in base all'elevazione (0..max_elev)."""
    if elevation <= 0:
        return hex_color
    factor = min(0.5, 0.15 * elevation)
    h = hex_color.lstrip("#")
    r = int(h[0:2], 16)
    g = int(h[2:4], 16)
    b = int(h[4:6], 16)
    r = int(r + (255 - r) * factor)
    g = int(g + (255 - g) * factor)
    b = int(b + (255 - b) * factor)
    return f"#{r:02x}{g:02x}{b:02x}"


__all__ = ["TERRAIN_COLORS", "TERRAIN_LABELS", "lighten_hex"]
