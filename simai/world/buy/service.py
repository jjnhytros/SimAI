"""BuyService — piazzamento, spostamento, rimozione oggetti."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.world.buy.enums import (
    ALLOWED_ROTATIONS,
    MAX_OBJECTS_PER_LOT,
    ObjectCategory,
)
from simai.world.buy.models import ObjectCatalog
from simai.world.lot import Lot
from simai.world.models import GameObject, Location

if TYPE_CHECKING:
    from simai.core.anthalys_datetime import AnthalysDateTime
    from simai.npc.models import Character

# ---------------------------------------------------------------------------
# Eccezioni
# ---------------------------------------------------------------------------


class BuyError(Exception):
    """Errore di validazione buy mode."""


# ---------------------------------------------------------------------------
# DTO
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class PlacementResult:
    """Esito di un piazzamento.

    - `cost_paid`: totale pagato (item + tax). Zero in sandbox.
    - `item_price`: prezzo base dell'item (0 in sandbox).
    - `tax_paid`: quota sales tax (0 in sandbox).
    """

    ok: bool
    reason: str
    object_id: int | None = None
    cost_paid: int = 0
    supplier_location_id: int | None = None
    item_price: int = 0
    tax_paid: int = 0


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------


class BuyService:
    """Servizio stateless di buy mode."""

    # ------------------------------------------------------------------
    # Catalog
    # ------------------------------------------------------------------

    @staticmethod
    def list_catalog(
        session: Session, *, category: ObjectCategory | None = None
    ) -> list[ObjectCatalog]:
        stmt = select(ObjectCatalog).order_by(ObjectCatalog.category, ObjectCatalog.name)
        if category is not None:
            stmt = stmt.where(ObjectCatalog.category == category.value)
        return list(session.scalars(stmt))

    @staticmethod
    def catalog_by_code(session: Session, code: str) -> ObjectCatalog | None:
        return session.scalars(select(ObjectCatalog).where(ObjectCatalog.type_code == code)).first()

    @staticmethod
    def catalog_by_id(session: Session, catalog_id: int) -> ObjectCatalog | None:
        return session.get(ObjectCatalog, catalog_id)

    # ------------------------------------------------------------------
    # Query objects
    # ------------------------------------------------------------------

    @staticmethod
    def objects_on_lot(session: Session, lot_id: int) -> list[GameObject]:
        """Oggetti piazzati su un lotto (con posizione)."""
        return list(
            session.scalars(
                select(GameObject)
                .where(
                    GameObject.lot_id == lot_id,
                    GameObject.position_x.is_not(None),
                )
                .order_by(GameObject.id)
            )
        )

    # ------------------------------------------------------------------
    # Overlap / bounds check
    # ------------------------------------------------------------------

    @staticmethod
    def _effective_cells(x: int, y: int, w: int, h: int) -> set[tuple[int, int]]:
        return {(x + dx, y + dy) for dx in range(w) for dy in range(h)}

    @staticmethod
    def _check_bounds(lot: Lot, x: int, y: int, w: int, h: int) -> None:
        if x < 0 or y < 0:
            raise BuyError("Coordinate negative non ammesse")
        if x + w > lot.bounds_w:
            raise BuyError(f"L'oggetto eccede la griglia in x ({x + w} > {lot.bounds_w})")
        if y + h > lot.bounds_h:
            raise BuyError(f"L'oggetto eccede la griglia in y ({y + h} > {lot.bounds_h})")

    @staticmethod
    def _check_object_overlap(
        session: Session,
        lot: Lot,
        cells: set[tuple[int, int]],
        *,
        exclude_object_id: int | None = None,
    ) -> None:
        existing = BuyService.objects_on_lot(session, lot.id)
        for obj in existing:
            if exclude_object_id is not None and obj.id == exclude_object_id:
                continue
            if obj.position_x is None or obj.position_y is None:
                continue
            if obj.catalog_type_id is None:
                continue
            cat = session.get(ObjectCatalog, obj.catalog_type_id)
            if cat is None:
                continue
            w, h = cat.effective_footprint(obj.rotation)
            other_cells = BuyService._effective_cells(obj.position_x, obj.position_y, w, h)
            if cells & other_cells:
                raise BuyError(f"Overlap con oggetto id={obj.id} ({obj.name})")

    # ------------------------------------------------------------------
    # Room detection for location assignment
    # ------------------------------------------------------------------

    @staticmethod
    def _find_room_for_cell(session: Session, lot: Lot, x: int, y: int) -> Location | None:
        """Trova la Location ROOM che contiene la cella (lot-local coords).

        Ritorna il building se non c'è una room specifica.
        """
        if lot.location_id is None:
            return None
        # Coordinate globali della cella (per confronto con i bounds della Location)
        gx = lot.bounds_x + x
        gy = lot.bounds_y + y

        rooms = list(
            session.scalars(
                select(Location).where(
                    Location.parent_id == lot.location_id,
                )
            )
        )
        for r in rooms:
            if (
                r.bounds_x <= gx < r.bounds_x + r.bounds_w
                and r.bounds_y <= gy < r.bounds_y + r.bounds_h
            ):
                return r
        return session.get(Location, lot.location_id)

    # ------------------------------------------------------------------
    # Placement
    # ------------------------------------------------------------------

    @staticmethod
    @staticmethod
    def place_object(
        session: Session,
        *,
        lot: Lot,
        catalog: ObjectCatalog,
        x: int,
        y: int,
        rotation: int = 0,
        buyer: Character | None = None,
        supplier_location_id: int | None = None,
        current_dt: AnthalysDateTime | None = None,
    ) -> PlacementResult:
        """Piazza un oggetto sul lotto.

        Se `buyer` è None: piazzamento gratuito (modalità sandbox/build-dev).
        Se `buyer` è valorizzato: verifica cash, scala soldi e stock.
        """
        try:
            BuyService._validate_placement(
                session,
                lot=lot,
                catalog=catalog,
                x=x,
                y=y,
                rotation=rotation,
            )
        except BuyError as exc:
            return PlacementResult(ok=False, reason=str(exc))

        # --- Pagamento (solo se buyer specificato) ---
        cost_paid = 0
        actual_supplier_id: int | None = None

        if buyer is not None:
            from simai.city.tax import TaxService
            from simai.world.buy.supplier import SupplierService

            if current_dt is None:
                return PlacementResult(False, "current_dt_required_for_purchase")

            # Trova offerta
            if supplier_location_id is not None:
                offer = SupplierService.get_offer(
                    session,
                    location_id=supplier_location_id,
                    type_code=catalog.type_code,
                )
                if offer is None:
                    return PlacementResult(
                        False,
                        f"fornitore {supplier_location_id} non vende {catalog.type_code}",
                    )
            else:
                offer = SupplierService.find_supplier(session, catalog.type_code)
                if offer is None:
                    return PlacementResult(
                        False,
                        f"nessun fornitore disponibile per {catalog.type_code}",
                    )

            if offer.stock == 0:
                return PlacementResult(False, "out_of_stock")

            # Sales tax (Chunk 4.7c)
            tax = TaxService.preview_sales_tax(offer.current_price)
            total_cost = offer.current_price + tax

            if int(buyer.athel_balance) < total_cost:
                return PlacementResult(
                    False,
                    f"fondi insufficienti: {buyer.athel_balance} < {total_cost}",
                )

            # Scala cash (item price)
            from simai.npc.economy.service import WealthService

            WealthService.add(session, buyer, -offer.current_price)

            # Sales tax -> CityBudget
            tax_result = TaxService.collect_sales_tax(
                session,
                buyer=buyer,
                purchase_amount=offer.current_price,
                current_dt=current_dt,
            )
            tax_paid = tax_result.amount if tax_result.ok else 0

            cost_paid = offer.current_price + tax_paid
            item_price = offer.current_price
            actual_supplier_id = offer.location_id

            # Scala stock
            SupplierService.decrement_stock(
                session,
                location_id=offer.location_id,
                type_code=catalog.type_code,
            )
        else:
            cost_paid = 0
            item_price = 0
            tax_paid = 0
            actual_supplier_id = None

        room = BuyService._find_room_for_cell(session, lot, x, y)

        obj = GameObject(
            name=catalog.name,
            type=catalog.type_code,
            location_id=room.id if room is not None else None,
            owner_character_id=buyer.id if buyer is not None else None,
            state="NEW",
            condition=1.0,
            container_capacity=catalog.container_capacity if catalog.is_container else None,
            container_contents_json=[],
            interactions_json=list(catalog.interactions_json),
            metadata_json=dict(catalog.metadata_json or {}),
            catalog_type_id=catalog.id,
            lot_id=lot.id,
            position_x=x,
            position_y=y,
            rotation=rotation,
        )
        session.add(obj)
        session.flush()

        # Transaction record (solo se pagato)
        if buyer is not None and cost_paid > 0:
            session.flush()

        logger.debug(
            "Buy: placed object {} ({}) at ({},{}) rot={} on lot={} cost={} buyer={}",
            obj.id,
            catalog.type_code,
            x,
            y,
            rotation,
            lot.id,
            cost_paid,
            buyer.id if buyer else "none",
        )
        return PlacementResult(
            ok=True,
            reason="ok",
            object_id=obj.id,
            cost_paid=cost_paid,
            supplier_location_id=actual_supplier_id,
            item_price=item_price,
            tax_paid=tax_paid,
        )

    @staticmethod
    def _validate_placement(
        session: Session,
        *,
        lot: Lot,
        catalog: ObjectCatalog,
        x: int,
        y: int,
        rotation: int,
    ) -> None:
        if rotation not in ALLOWED_ROTATIONS:
            raise BuyError(f"Rotazione {rotation} non ammessa (consentite: {ALLOWED_ROTATIONS})")
        count = len(BuyService.objects_on_lot(session, lot.id))
        if count >= MAX_OBJECTS_PER_LOT:
            raise BuyError(f"Limite oggetti per lotto raggiunto ({MAX_OBJECTS_PER_LOT})")
        w, h = catalog.effective_footprint(rotation)
        BuyService._check_bounds(lot, x, y, w, h)
        cells = BuyService._effective_cells(x, y, w, h)
        BuyService._check_object_overlap(session, lot, cells)

    # ------------------------------------------------------------------
    # Move / remove
    # ------------------------------------------------------------------

    @staticmethod
    def move_object(
        session: Session,
        *,
        lot: Lot,
        object_id: int,
        x: int,
        y: int,
        rotation: int | None = None,
    ) -> PlacementResult:
        obj = session.get(GameObject, object_id)
        if obj is None or obj.lot_id != lot.id:
            return PlacementResult(False, "object_not_found")
        if obj.catalog_type_id is None:
            return PlacementResult(False, "not_from_catalog")
        catalog = session.get(ObjectCatalog, obj.catalog_type_id)
        if catalog is None:
            return PlacementResult(False, "catalog_missing")
        new_rot = rotation if rotation is not None else obj.rotation

        try:
            BuyService._validate_placement(
                session,
                lot=lot,
                catalog=catalog,
                x=x,
                y=y,
                rotation=new_rot,
            )
        except BuyError as exc:
            # Ripeti l'overlap check escludendo l'oggetto stesso
            try:
                BuyService._validate_placement_excluding(
                    session,
                    lot=lot,
                    catalog=catalog,
                    x=x,
                    y=y,
                    rotation=new_rot,
                    exclude_object_id=object_id,
                )
            except BuyError as exc2:
                return PlacementResult(False, str(exc2))
            # Se passa escludendo, prosegui
            _ = exc

        obj.position_x = x
        obj.position_y = y
        obj.rotation = new_rot
        room = BuyService._find_room_for_cell(session, lot, x, y)
        obj.location_id = room.id if room is not None else obj.location_id
        session.flush()
        return PlacementResult(True, "ok", object_id)

    @staticmethod
    def _validate_placement_excluding(
        session: Session,
        *,
        lot: Lot,
        catalog: ObjectCatalog,
        x: int,
        y: int,
        rotation: int,
        exclude_object_id: int,
    ) -> None:
        w, h = catalog.effective_footprint(rotation)
        BuyService._check_bounds(lot, x, y, w, h)
        cells = BuyService._effective_cells(x, y, w, h)
        BuyService._check_object_overlap(session, lot, cells, exclude_object_id=exclude_object_id)

    @staticmethod
    def remove_object(session: Session, *, object_id: int) -> bool:
        obj = session.get(GameObject, object_id)
        if obj is None:
            return False
        session.delete(obj)
        session.flush()
        return True


__all__ = [
    "BuyError",
    "BuyService",
    "PlacementResult",
]
