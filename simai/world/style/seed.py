"""Seed del catalogo stili."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.world.style.enums import StyleKind
from simai.world.style.models import StyleCatalog


@dataclass(frozen=True, slots=True)
class StyleSeedResult:
    created: int
    total: int


# (type_code, name, kind, color_hex, price, pattern, icon)
STYLE_ENTRIES: list[tuple[str, str, StyleKind, str, int, str, str]] = [
    # ---- FLOOR: legno ----
    ("floor_wood_oak", "Parquet rovere", StyleKind.FLOOR, "#8B5A2B", 8, "wood", "bi-grid"),
    ("floor_wood_dark", "Parquet scuro", StyleKind.FLOOR, "#3B2417", 10, "wood", "bi-grid"),
    ("floor_wood_light", "Parquet chiaro", StyleKind.FLOOR, "#D2A86A", 8, "wood", "bi-grid"),
    # ---- FLOOR: piastrelle ----
    (
        "floor_tile_white",
        "Piastrelle bianche",
        StyleKind.FLOOR,
        "#F5F5F5",
        6,
        "tile",
        "bi-grid-3x3",
    ),
    ("floor_tile_black", "Piastrelle nere", StyleKind.FLOOR, "#1A1A1A", 6, "tile", "bi-grid-3x3"),
    ("floor_tile_terracotta", "Cotto", StyleKind.FLOOR, "#B25B3D", 7, "tile", "bi-grid-3x3"),
    # ---- FLOOR: moquette ----
    (
        "floor_carpet_red",
        "Moquette rossa",
        StyleKind.FLOOR,
        "#8B1A1A",
        12,
        "solid",
        "bi-square-fill",
    ),
    (
        "floor_carpet_blue",
        "Moquette blu",
        StyleKind.FLOOR,
        "#1A3A8B",
        12,
        "solid",
        "bi-square-fill",
    ),
    (
        "floor_carpet_green",
        "Moquette verde",
        StyleKind.FLOOR,
        "#1A6B3A",
        12,
        "solid",
        "bi-square-fill",
    ),
    # ---- FLOOR: pietra ----
    ("floor_stone_gray", "Pietra grigia", StyleKind.FLOOR, "#6B6B6B", 9, "stone", "bi-square"),
    ("floor_marble_white", "Marmo bianco", StyleKind.FLOOR, "#EAEAEA", 18, "marble", "bi-diamond"),
    # ---- WALL: vernice ----
    ("wall_paint_white", "Vernice bianca", StyleKind.WALL, "#F0F0F0", 5, "solid", "bi-brush"),
    ("wall_paint_cream", "Vernice crema", StyleKind.WALL, "#F5E6C8", 5, "solid", "bi-brush"),
    ("wall_paint_blue", "Vernice azzurra", StyleKind.WALL, "#A8C8E8", 5, "solid", "bi-brush"),
    ("wall_paint_green", "Vernice verde", StyleKind.WALL, "#A8D5A8", 5, "solid", "bi-brush"),
    # ---- WALL: carta da parati ----
    ("wall_wp_stripes", "Carta righe", StyleKind.WALL, "#D4A574", 12, "stripes", "bi-list"),
    ("wall_wp_floral", "Carta floreale", StyleKind.WALL, "#C8A8D4", 15, "floral", "bi-flower1"),
    ("wall_wp_dots", "Carta a pois", StyleKind.WALL, "#D4C8A8", 10, "dots", "bi-circle"),
    # ---- WALL: mattoni/legno ----
    ("wall_brick_red", "Mattoni rossi", StyleKind.WALL, "#9B3D26", 14, "brick", "bi-bricks"),
    ("wall_brick_white", "Mattoni bianchi", StyleKind.WALL, "#E8E0D0", 16, "brick", "bi-bricks"),
    ("wall_wood_panel", "Pannelli legno", StyleKind.WALL, "#6B4A2B", 18, "wood", "bi-border-style"),
]


def seed_style_catalog(session: Session) -> StyleSeedResult:
    """Popola `StyleCatalog` (idempotente)."""
    existing = session.scalars(select(StyleCatalog)).first()
    if existing is not None:
        total = len(list(session.scalars(select(StyleCatalog))))
        return StyleSeedResult(created=0, total=total)

    created = 0
    for (
        code,
        name,
        kind,
        color,
        price,
        pattern,
        icon,
    ) in STYLE_ENTRIES:
        session.add(
            StyleCatalog(
                type_code=code,
                name=name,
                kind=kind.value,
                color_hex=color,
                base_price=price,
                pattern=pattern,
                icon=icon,
                metadata_json={},
            )
        )
        created += 1
    session.flush()
    return StyleSeedResult(created=created, total=created)


__all__ = ["STYLE_ENTRIES", "StyleSeedResult", "seed_style_catalog"]
