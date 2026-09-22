"""Route: Build mode (canvas 2D per editing di lotti)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.ui.app import templates
from simai.ui.deps import get_db
from simai.world.build import (
    BuildError,
    BuildService,
    OpeningKind,
    WallMaterial,
    WallOrientation,
)
from simai.world.buy import (
    ALLOWED_ROTATIONS,
    BuyService,
    ObjectCategory,
)
from simai.world.buy.models import ObjectCatalog
from simai.world.lot_service import get_lot
from simai.world.style import (
    StyleKind,
    StyleService,
    WallSide,
)
from simai.world.terrain import (
    TERRAIN_COLORS,
    TERRAIN_LABELS,
    TerrainService,
    TerrainType,
    lighten_hex,
)

router = APIRouter()


# ---------------------------------------------------------------------------
# HTML
# ---------------------------------------------------------------------------


@router.get("/world/lots/{lot_id}/build", response_class=HTMLResponse)
def build_page(
    request: Request,
    lot_id: int,
    session: Session = Depends(get_db),
) -> HTMLResponse:
    """Editor build mode per un lotto."""
    lot = get_lot(session, lot_id)
    if lot is None:
        raise HTTPException(status_code=404, detail=f"Lot {lot_id} non trovato")
    return templates.TemplateResponse(
        request,
        "build_editor.html",
        {"lot": lot},
    )


# ---------------------------------------------------------------------------
# JSON API
# ---------------------------------------------------------------------------


@router.get("/api/lots/{lot_id}/layout.json")
def layout_json(
    lot_id: int,
    session: Session = Depends(get_db),
) -> JSONResponse:
    """Ritorna il layout corrente del lotto."""
    lot = get_lot(session, lot_id)
    if lot is None:
        raise HTTPException(status_code=404, detail=f"Lot {lot_id} non trovato")
    layout = BuildService.layout_of(session, lot)
    return JSONResponse(
        {
            "lot_id": layout.lot_id,
            "grid_w": layout.grid_w,
            "grid_h": layout.grid_h,
            "walls": layout.walls,
            "openings": layout.openings,
            "rooms": layout.rooms,
        }
    )


@router.post("/api/lots/{lot_id}/walls")
def api_add_wall(
    lot_id: int,
    payload: dict[str, Any] = Body(...),
    session: Session = Depends(get_db),
) -> JSONResponse:
    """Aggiunge un muro."""
    lot = get_lot(session, lot_id)
    if lot is None:
        raise HTTPException(status_code=404, detail=f"Lot {lot_id} non trovato")
    try:
        x = int(payload["x"])
        y = int(payload["y"])
        orientation = WallOrientation(str(payload.get("orientation", "H")))
        material = WallMaterial(str(payload.get("material", "WOOD")))
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=f"Payload non valido: {exc}") from exc

    try:
        wall = BuildService.add_wall(
            session,
            lot=lot,
            x=x,
            y=y,
            orientation=orientation,
            material=material,
        )
    except BuildError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    session.commit()
    return JSONResponse(
        {
            "id": wall.id,
            "x": wall.x,
            "y": wall.y,
            "orientation": wall.orientation,
            "material": wall.material,
        }
    )


@router.delete("/api/walls/{wall_id}")
def api_remove_wall(
    wall_id: int,
    session: Session = Depends(get_db),
) -> JSONResponse:
    """Rimuove un muro."""
    ok = BuildService.remove_wall(session, wall_id=wall_id)
    session.commit()
    return JSONResponse({"ok": ok})


@router.post("/api/walls/{wall_id}/opening")
def api_set_opening(
    wall_id: int,
    payload: dict[str, Any] = Body(...),
    session: Session = Depends(get_db),
) -> JSONResponse:
    """Imposta apertura su un muro (door/window)."""
    from simai.world.build import Wall

    wall = session.get(Wall, wall_id)
    if wall is None:
        raise HTTPException(status_code=404, detail=f"Wall {wall_id} non trovato")
    lot = get_lot(session, wall.lot_id)
    if lot is None:
        raise HTTPException(status_code=500, detail="Lot associato mancante")
    try:
        kind = OpeningKind(str(payload["kind"]))
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=f"Kind non valido: {exc}") from exc
    try:
        op = BuildService.set_opening(session, lot=lot, wall_id=wall_id, kind=kind)
    except BuildError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    session.commit()
    return JSONResponse({"id": op.id, "wall_id": op.wall_id, "kind": op.kind})


@router.delete("/api/walls/{wall_id}/opening")
def api_remove_opening(
    wall_id: int,
    session: Session = Depends(get_db),
) -> JSONResponse:
    ok = BuildService.remove_opening(session, wall_id=wall_id)
    session.commit()
    return JSONResponse({"ok": ok})


@router.post("/api/lots/{lot_id}/recompute-rooms")
def api_recompute_rooms(
    lot_id: int,
    session: Session = Depends(get_db),
) -> JSONResponse:
    """Ricalcola le Location ROOM in base ai muri."""
    lot = get_lot(session, lot_id)
    if lot is None:
        raise HTTPException(status_code=404, detail=f"Lot {lot_id} non trovato")
    n = BuildService.recompute_rooms(session, lot)
    session.commit()
    return JSONResponse({"rooms_created": n})


@router.post("/api/lots/{lot_id}/clear")
def api_clear(
    lot_id: int,
    session: Session = Depends(get_db),
) -> JSONResponse:
    """Cancella tutti i muri e le aperture."""
    n = BuildService.clear_walls(session, lot_id)
    session.commit()
    return JSONResponse({"walls_removed": n})


# ---------------------------------------------------------------------------
# Buy mode endpoints
# ---------------------------------------------------------------------------


@router.get("/api/catalog.json")
def api_catalog(
    category: str | None = None,
    session: Session = Depends(get_db),
) -> JSONResponse:
    """Ritorna il catalogo oggetti con info di prezzo/stock dai fornitori."""
    from simai.world.buy.supplier import SupplierService

    cat: ObjectCategory | None = None
    if category:
        try:
            cat = ObjectCategory(category.upper())
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"Categoria non valida: {category}"
            ) from None
    items = BuyService.list_catalog(session, category=cat)
    payload = []
    for c in items:
        offer = SupplierService.find_supplier(session, c.type_code)
        payload.append(
            {
                "id": c.id,
                "type_code": c.type_code,
                "name": c.name,
                "category": c.category,
                "base_price": c.base_price,
                "footprint_w": c.footprint_w,
                "footprint_h": c.footprint_h,
                "icon": c.icon,
                "supplier_price": offer.current_price if offer else c.base_price,
                "supplier_stock": offer.stock if offer else 0,
                "supplier_location_id": offer.location_id if offer else None,
                "supplier_name": offer.location_name if offer else None,
            }
        )
    from simai.city.enums import SALES_TAX_RATE

    return JSONResponse(
        {
            "sales_tax_rate": SALES_TAX_RATE,
            "items": payload,
        }
    )


@router.get("/api/lots/{lot_id}/objects.json")
def api_objects_on_lot(
    lot_id: int,
    session: Session = Depends(get_db),
) -> JSONResponse:
    """Ritorna gli oggetti piazzati sul lotto."""
    lot = get_lot(session, lot_id)
    if lot is None:
        raise HTTPException(status_code=404, detail=f"Lot {lot_id} non trovato")
    objects = BuyService.objects_on_lot(session, lot_id)
    items = []
    for obj in objects:
        cat = session.get(ObjectCatalog, obj.catalog_type_id) if obj.catalog_type_id else None
        w, h = cat.effective_footprint(obj.rotation) if cat else (1, 1)
        items.append(
            {
                "id": obj.id,
                "name": obj.name,
                "type_code": obj.type,
                "catalog_type_id": obj.catalog_type_id,
                "position_x": obj.position_x,
                "position_y": obj.position_y,
                "rotation": obj.rotation,
                "footprint_w": w,
                "footprint_h": h,
                "icon": cat.icon if cat else "bi-box",
            }
        )
    return JSONResponse({"lot_id": lot_id, "objects": items})


@router.post("/api/lots/{lot_id}/objects")
def api_place_object(
    lot_id: int,
    payload: dict[str, Any] = Body(...),
    session: Session = Depends(get_db),
) -> JSONResponse:
    """Piazza un oggetto dal catalogo.

    Se `buyer_id` è specificato, i soldi vengono scalati e lo stock
    del fornitore decrementato.
    """
    from simai.npc.models import Character as _Char

    lot = get_lot(session, lot_id)
    if lot is None:
        raise HTTPException(status_code=404, detail=f"Lot {lot_id} non trovato")
    try:
        catalog_id = int(payload["catalog_id"])
        x = int(payload["x"])
        y = int(payload["y"])
        rotation = int(payload.get("rotation", 0))
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=f"Payload non valido: {exc}") from exc

    if rotation not in ALLOWED_ROTATIONS:
        raise HTTPException(status_code=400, detail=f"Rotation {rotation} non ammessa")

    catalog = BuyService.catalog_by_id(session, catalog_id)
    if catalog is None:
        raise HTTPException(status_code=404, detail=f"Catalog id={catalog_id} non trovato")

    buyer_id_raw = payload.get("buyer_id")
    buyer = None
    if buyer_id_raw is not None:
        buyer = session.get(_Char, int(buyer_id_raw))
        if buyer is None:
            raise HTTPException(
                status_code=404,
                detail=f"Buyer id={buyer_id_raw} non trovato",
            )

    supplier_raw = payload.get("supplier_location_id")
    supplier_id: int | None = int(supplier_raw) if supplier_raw is not None else None

    result = BuyService.place_object(
        session,
        lot=lot,
        catalog=catalog,
        x=x,
        y=y,
        rotation=rotation,
        buyer=buyer,
        supplier_location_id=supplier_id,
    )
    if not result.ok:
        raise HTTPException(status_code=400, detail=result.reason)
    session.commit()
    return JSONResponse(
        {
            "id": result.object_id,
            "ok": True,
            "cost_paid": result.cost_paid,
            "item_price": result.item_price,
            "tax_paid": result.tax_paid,
            "supplier_location_id": result.supplier_location_id,
        }
    )


@router.put("/api/objects/{object_id}")
def api_move_object(
    object_id: int,
    payload: dict[str, Any] = Body(...),
    session: Session = Depends(get_db),
) -> JSONResponse:
    """Sposta (o ruota) un oggetto."""
    from simai.world.models import GameObject

    obj = session.get(GameObject, object_id)
    if obj is None or obj.lot_id is None:
        raise HTTPException(status_code=404, detail=f"Oggetto {object_id} non trovato")
    lot = get_lot(session, obj.lot_id)
    if lot is None:
        raise HTTPException(status_code=500, detail="Lot associato mancante")
    try:
        x = int(payload["x"])
        y = int(payload["y"])
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=f"Payload non valido: {exc}") from exc
    rotation = payload.get("rotation")
    if rotation is not None:
        rotation = int(rotation)

    result = BuyService.move_object(
        session, lot=lot, object_id=object_id, x=x, y=y, rotation=rotation
    )
    if not result.ok:
        raise HTTPException(status_code=400, detail=result.reason)
    session.commit()
    return JSONResponse({"ok": True})


@router.delete("/api/objects/{object_id}")
def api_remove_object(
    object_id: int,
    session: Session = Depends(get_db),
) -> JSONResponse:
    ok = BuyService.remove_object(session, object_id=object_id)
    session.commit()
    return JSONResponse({"ok": ok})


# ---------------------------------------------------------------------------
# Buyers (character acquirenti)
# ---------------------------------------------------------------------------


@router.get("/api/lots/{lot_id}/buyers.json")
def api_lot_buyers(
    lot_id: int,
    session: Session = Depends(get_db),
) -> JSONResponse:
    """Ritorna gli NPC vivi candidati come acquirenti per questo lotto.

    Il proprietario del lotto (se esiste) è evidenziato e messo per primo.
    """
    from simai.economy.property import LotOwnershipService
    from simai.npc.models import Character as _Char

    lot = get_lot(session, lot_id)
    if lot is None:
        raise HTTPException(status_code=404, detail=f"Lot {lot_id} non trovato")

    owner = LotOwnershipService.owner_character(session, lot_id)
    owner_id = owner.id if owner else None

    chars = list(session.scalars(select(_Char).where(_Char.is_alive.is_(True)).order_by(_Char.id)))

    from dataclasses import dataclass

    @dataclass(frozen=True, slots=True)
    class _BuyerRow:
        id: int
        name: str
        balance: int
        is_owner: bool

    rows = [
        _BuyerRow(
            id=c.id,
            name=c.full_name,
            balance=int(c.athel_balance),
            is_owner=c.id == owner_id,
        )
        for c in chars
    ]
    rows.sort(key=lambda r: (not r.is_owner, -r.balance))
    items: list[dict[str, object]] = [
        {
            "id": r.id,
            "name": r.name,
            "balance": r.balance,
            "is_owner": r.is_owner,
        }
        for r in rows
    ]
    return JSONResponse({"lot_id": lot_id, "buyers": items})


# ---------------------------------------------------------------------------
# Style endpoints
# ---------------------------------------------------------------------------


@router.get("/api/styles.json")
def api_styles(
    kind: str | None = None,
    session: Session = Depends(get_db),
) -> JSONResponse:
    """Ritorna il catalogo stili, opzionalmente filtrato per kind."""
    k: StyleKind | None = None
    if kind:
        try:
            k = StyleKind(kind.upper())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Kind non valido: {kind}") from None
    items = StyleService.list_catalog(session, kind=k)
    return JSONResponse(
        {
            "items": [
                {
                    "id": c.id,
                    "type_code": c.type_code,
                    "name": c.name,
                    "kind": c.kind,
                    "color_hex": c.color_hex,
                    "base_price": c.base_price,
                    "pattern": c.pattern,
                    "icon": c.icon,
                }
                for c in items
            ]
        }
    )


@router.get("/api/lots/{lot_id}/style_layout.json")
def api_style_layout(
    lot_id: int,
    session: Session = Depends(get_db),
) -> JSONResponse:
    """Ritorna floor tiles + wall coverings del lotto."""
    lot = get_lot(session, lot_id)
    if lot is None:
        raise HTTPException(status_code=404, detail=f"Lot {lot_id} non trovato")
    floors = StyleService.floors_of(session, lot_id)
    coverings = StyleService.wall_coverings_of(session, lot_id)
    return JSONResponse(
        {
            "floors": [{"x": f.x, "y": f.y, "style_id": f.style_id} for f in floors],
            "wall_coverings": [
                {"wall_id": c.wall_id, "side": c.side, "style_id": c.style_id} for c in coverings
            ],
        }
    )


@router.post("/api/lots/{lot_id}/floor")
def api_set_floor(
    lot_id: int,
    payload: dict[str, Any] = Body(...),
    session: Session = Depends(get_db),
) -> JSONResponse:
    from simai.npc.models import Character as _Char

    lot = get_lot(session, lot_id)
    if lot is None:
        raise HTTPException(status_code=404, detail=f"Lot {lot_id} non trovato")
    try:
        x = int(payload["x"])
        y = int(payload["y"])
        style_id = int(payload["style_id"])
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=f"Payload non valido: {exc}") from exc
    style = StyleService.by_id(session, style_id)
    if style is None:
        raise HTTPException(status_code=404, detail=f"Style id={style_id} non trovato")
    buyer = None
    if "buyer_id" in payload and payload["buyer_id"] is not None:
        buyer = session.get(_Char, int(payload["buyer_id"]))
        if buyer is None:
            raise HTTPException(status_code=404, detail="Buyer non trovato")
    result = StyleService.set_floor(session, lot=lot, x=x, y=y, style=style, buyer=buyer)
    if not result.ok:
        raise HTTPException(status_code=400, detail=result.reason)
    session.commit()
    return JSONResponse({"ok": True, "cost_paid": result.cost_paid})


@router.delete("/api/lots/{lot_id}/floor/{x}/{y}")
def api_clear_floor(
    lot_id: int,
    x: int,
    y: int,
    session: Session = Depends(get_db),
) -> JSONResponse:
    ok = StyleService.clear_floor(session, lot_id=lot_id, x=x, y=y)
    session.commit()
    return JSONResponse({"ok": ok})


@router.post("/api/walls/{wall_id}/covering")
def api_set_wall_covering(
    wall_id: int,
    payload: dict[str, Any] = Body(...),
    session: Session = Depends(get_db),
) -> JSONResponse:
    from simai.npc.models import Character as _Char
    from simai.world.build.models import Wall

    wall = session.get(Wall, wall_id)
    if wall is None:
        raise HTTPException(status_code=404, detail=f"Wall {wall_id} non trovato")
    try:
        style_id = int(payload["style_id"])
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=f"Payload non valido: {exc}") from exc
    side_raw = str(payload.get("side", "INTERIOR"))
    try:
        side = WallSide(side_raw.upper())
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Side non valido: {side_raw}") from None
    style = StyleService.by_id(session, style_id)
    if style is None:
        raise HTTPException(status_code=404, detail=f"Style id={style_id} non trovato")
    buyer = None
    if "buyer_id" in payload and payload["buyer_id"] is not None:
        buyer = session.get(_Char, int(payload["buyer_id"]))
    result = StyleService.set_wall_style(session, wall=wall, style=style, side=side, buyer=buyer)
    if not result.ok:
        raise HTTPException(status_code=400, detail=result.reason)
    session.commit()
    return JSONResponse({"ok": True, "cost_paid": result.cost_paid})


@router.delete("/api/walls/{wall_id}/covering")
def api_clear_wall_covering(
    wall_id: int,
    side: str = "INTERIOR",
    session: Session = Depends(get_db),
) -> JSONResponse:
    try:
        s = WallSide(side.upper())
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Side non valido: {side}") from None
    ok = StyleService.clear_wall_style(session, wall_id=wall_id, side=s)
    session.commit()
    return JSONResponse({"ok": ok})


# ---------------------------------------------------------------------------
# Terrain endpoints
# ---------------------------------------------------------------------------


@router.get("/api/terrains.json")
def api_terrains() -> JSONResponse:
    """Ritorna il catalogo tipi di terreno con colori (statico, no DB)."""
    items = []
    for t in TerrainType:
        items.append(
            {
                "type": t.value,
                "label": TERRAIN_LABELS.get(t, t.value),
                "color_hex": TERRAIN_COLORS.get(t, "#888888"),
            }
        )
    return JSONResponse({"items": items})


@router.get("/api/lots/{lot_id}/terrain_layout.json")
def api_terrain_layout(
    lot_id: int,
    session: Session = Depends(get_db),
) -> JSONResponse:
    """Ritorna i terrain tiles del lotto."""
    lot = get_lot(session, lot_id)
    if lot is None:
        raise HTTPException(status_code=404, detail=f"Lot {lot_id} non trovato")
    tiles = TerrainService.tiles_of(session, lot_id)
    return JSONResponse(
        {
            "tiles": [
                {
                    "x": t.x,
                    "y": t.y,
                    "terrain_type": t.terrain_type,
                    "elevation": t.elevation,
                    "color": lighten_hex(
                        TERRAIN_COLORS.get(TerrainType(t.terrain_type), "#888888"),
                        t.elevation,
                    ),
                }
                for t in tiles
            ]
        }
    )


@router.post("/api/lots/{lot_id}/terrain")
def api_set_terrain(
    lot_id: int,
    payload: dict[str, Any] = Body(...),
    session: Session = Depends(get_db),
) -> JSONResponse:
    from simai.npc.models import Character as _Char

    lot = get_lot(session, lot_id)
    if lot is None:
        raise HTTPException(status_code=404, detail=f"Lot {lot_id} non trovato")
    try:
        x = int(payload["x"])
        y = int(payload["y"])
        terrain_type = TerrainType(str(payload["terrain_type"]))
        elevation = int(payload.get("elevation", 0))
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=f"Payload non valido: {exc}") from exc

    buyer = None
    if "buyer_id" in payload and payload["buyer_id"] is not None:
        buyer = session.get(_Char, int(payload["buyer_id"]))

    result = TerrainService.set_terrain(
        session,
        lot=lot,
        x=x,
        y=y,
        terrain_type=terrain_type,
        elevation=elevation,
        buyer=buyer,
    )
    if not result.ok:
        raise HTTPException(status_code=400, detail=result.reason)
    session.commit()
    return JSONResponse({"ok": True, "cost_paid": result.cost_paid})


@router.delete("/api/lots/{lot_id}/terrain/{x}/{y}")
def api_clear_terrain(
    lot_id: int,
    x: int,
    y: int,
    session: Session = Depends(get_db),
) -> JSONResponse:
    ok = TerrainService.clear_tile(session, lot_id=lot_id, x=x, y=y)
    session.commit()
    return JSONResponse({"ok": ok})
