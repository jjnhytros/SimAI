"""AionService — API unificata per la piattaforma AION.

Copre in 5.4a:
  - Bootstrap singleton `AionPlatform` + `AionWarehouse` globale.
  - CRUD listing (create/cancel).
  - Ordini con escrow (place_order / confirm_delivery / cancel_order).
  - Conti ledger `aion:revenue` (REVENUE) e `aion:escrow` (LIABILITY).

Le spedizioni fisiche (5.4b) e i prodotti polimorfici (5.4d) sono fuori scope.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.city.transport.models import Vehicle
from simai.core.anthalys_datetime import AnthalysDateTime
from simai.economy.aion.enums import (
    AION_ESCROW_CODE,
    AION_PLATFORM_CODE,
    AION_PLATFORM_NAME,
    AION_REVENUE_CODE,
    CARGO_SPEED_CELLS_PER_TICK,
    DEFAULT_COMMISSION_RATE,
    DEFAULT_COMMISSION_RATES,
    GLOBAL_WAREHOUSE_CAPACITY,
    GLOBAL_WAREHOUSE_CODE,
    GLOBAL_WAREHOUSE_DEPTH_METERS,
    SHIPPING_BASE_COST,
    SHIPPING_COST_PER_CELL,
    SHIPPING_DELIVERY_RADIUS_CELLS,
    AionBuyerType,
    AionFulfillmentMode,
    AionInventoryItemStatus,
    AionListingStatus,
    AionOrderStatus,
    AionProductType,
    AionSellerType,
    AionShipmentStatus,
)
from simai.economy.aion.models import (
    AionInventoryItem,
    AionListing,
    AionOrder,
    AionPlatform,
    AionShipment,
    AionWarehouse,
)
from simai.economy.companies.enums import company_athel_code
from simai.economy.companies.models import Company
from simai.economy.ledger import (
    Account,
    AccountKind,
    AccountOwnerType,
    JournalEntryKind,
    LedgerService,
    PostingDirection,
    PostingSpec,
)
from simai.economy.property import LotOwnershipService
from simai.npc.models import Character
from simai.world.lot import Lot
from simai.world.models import GameObject, Location


class AionError(Exception):
    """Errore di validazione o invariante sul dominio AION."""


# ---------------------------------------------------------------------------
# Dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class OrderResult:
    """Esito di `place_order`."""

    ok: bool
    reason: str
    order_id: int | None
    escrow_entry_id: int | None
    escrowed: int


@dataclass(frozen=True, slots=True)
class SettlementResult:
    """Esito di `confirm_delivery` / `cancel_order`."""

    ok: bool
    reason: str
    settled_amount: int
    commission: int
    settlement_entry_id: int | None


@dataclass(frozen=True, slots=True)
class ShipmentResult:
    """Esito di `ship_order`."""

    ok: bool
    reason: str
    shipment_id: int | None
    mode: str
    duration_ticks: int
    distance_cells: float
    immediate: bool


@dataclass(slots=True)
class ShipmentTickReport:
    """Esito di `tick_shipments`."""

    deliveries_completed: int = 0
    shipments_failed: int = 0
    order_ids: list[int] = field(default_factory=list)


# ---------------------------------------------------------------------------
# AionService
# ---------------------------------------------------------------------------


class AionService:
    """Servizio stateless della piattaforma AION."""

    # ------------------------------------------------------------------
    # Conti ledger
    # ------------------------------------------------------------------

    @staticmethod
    def _revenue_account(session: Session) -> Account:
        return LedgerService.get_or_create_account(
            session,
            code=AION_REVENUE_CODE,
            kind=AccountKind.REVENUE,
            owner_type=AccountOwnerType.SYSTEM,
            name="AION — Ricavi da commissioni",
        )

    @staticmethod
    def _escrow_account(session: Session) -> Account:
        return LedgerService.get_or_create_account(
            session,
            code=AION_ESCROW_CODE,
            kind=AccountKind.LIABILITY,
            owner_type=AccountOwnerType.SYSTEM,
            name="AION — Fondi in escrow",
        )

    @staticmethod
    def _character_athel(session: Session, character: Character) -> Account:
        return LedgerService.character_athel_account(
            session, character.id, character_name=character.full_name
        )

    @staticmethod
    def _actor_athel_account(
        session: Session,
        actor: Character | Company,
    ) -> Account:
        """Ritorna il conto ASSET `athel` dell'attore (Character o Company)."""
        if isinstance(actor, Character):
            return LedgerService.character_athel_account(
                session, actor.id, character_name=actor.full_name
            )
        return LedgerService.get_or_create_account(
            session,
            code=company_athel_code(actor.id),
            kind=AccountKind.ASSET,
            owner_type=AccountOwnerType.COMPANY,
            owner_id=actor.id,
            name=f"Cassa di {actor.name}",
        )

    @staticmethod
    def _actor_display_name(actor: Character | Company) -> str:
        if isinstance(actor, Character):
            return actor.full_name
        return actor.name

    @staticmethod
    def _classify_buyer(
        actor: Character | Company,
    ) -> tuple[AionBuyerType, int | None, int | None]:
        if isinstance(actor, Character):
            return (AionBuyerType.CHARACTER, actor.id, None)
        return (AionBuyerType.COMPANY, None, actor.id)

    @staticmethod
    def _classify_seller(
        actor: Character | Company,
    ) -> tuple[AionSellerType, int | None, int | None]:
        if isinstance(actor, Character):
            return (AionSellerType.CHARACTER, actor.id, None)
        return (AionSellerType.COMPANY, None, actor.id)

    # ------------------------------------------------------------------
    # Bootstrap piattaforma
    # ------------------------------------------------------------------

    @staticmethod
    def get_platform(session: Session) -> AionPlatform | None:
        return session.scalars(
            select(AionPlatform).where(AionPlatform.code == AION_PLATFORM_CODE)
        ).first()

    @staticmethod
    def get_global_warehouse(session: Session) -> AionWarehouse | None:
        return session.scalars(
            select(AionWarehouse).where(AionWarehouse.code == GLOBAL_WAREHOUSE_CODE)
        ).first()

    @staticmethod
    def ensure_platform(session: Session) -> AionPlatform:
        """Crea (idempotente) piattaforma AION + magazzino globale + conti ledger."""
        platform = AionService.get_platform(session)
        if platform is None:
            platform = AionPlatform(
                code=AION_PLATFORM_CODE,
                name=AION_PLATFORM_NAME,
                is_active=True,
                default_commission_rate=DEFAULT_COMMISSION_RATE,
                default_fulfillment_mode=AionFulfillmentMode.SELLER_DIRECT.value,
                metadata_json={
                    "commission_rates": DEFAULT_COMMISSION_RATES,
                    "owner": "GOVERNMENT_OF_ANTHALYS",
                    "managed_by": "AI",
                },
            )
            session.add(platform)
            session.flush()
            logger.info("AION platform creata: code={}", platform.code)

        # Magazzino globale (sotterraneo)
        warehouse = AionService.get_global_warehouse(session)
        if warehouse is None:
            warehouse = AionWarehouse(
                code=GLOBAL_WAREHOUSE_CODE,
                name="Magazzino AION Globale",
                warehouse_kind="GLOBAL",
                depth_meters=GLOBAL_WAREHOUSE_DEPTH_METERS,
                underground_x=0,
                underground_y=0,
                access_location_id=None,
                capacity=GLOBAL_WAREHOUSE_CAPACITY,
                used_capacity=0,
                is_active=True,
                metadata_json={"subterranean": True},
            )
            session.add(warehouse)
            session.flush()
            logger.info(
                "AION global warehouse creato: code={} depth={}m",
                warehouse.code,
                warehouse.depth_meters,
            )

        # Conti ledger (idempotenti)
        AionService._revenue_account(session)
        AionService._escrow_account(session)

        return platform

    # ------------------------------------------------------------------
    # Commissioni
    # ------------------------------------------------------------------

    @staticmethod
    def commission_rate(
        session: Session,
        *,
        seller_type: AionSellerType,
        product_type: AionProductType,
    ) -> float:
        """Ritorna la commissione per (seller_type, product_type).

        Legge da `AionPlatform.metadata_json["commission_rates"]` con
        fallback a `default_commission_rate`.
        """
        platform = AionService.get_platform(session)
        if platform is None:
            return DEFAULT_COMMISSION_RATE
        raw = (platform.metadata_json or {}).get("commission_rates")
        if not isinstance(raw, dict):
            return platform.default_commission_rate
        seller_map = raw.get(seller_type.value)
        if not isinstance(seller_map, dict):
            return platform.default_commission_rate
        try:
            return float(seller_map.get(product_type.value, platform.default_commission_rate))
        except (TypeError, ValueError):
            return platform.default_commission_rate

    @staticmethod
    def preview_commission(
        session: Session,
        *,
        seller_type: AionSellerType,
        product_type: AionProductType,
        total_price: int,
    ) -> int:
        """Commissione che verrebbe applicata su `total_price`."""
        rate = AionService.commission_rate(
            session, seller_type=seller_type, product_type=product_type
        )
        return int(total_price * rate)

    # ------------------------------------------------------------------
    # Listing
    # ------------------------------------------------------------------

    @staticmethod
    def create_listing(
        session: Session,
        *,
        seller: Character | Company,
        item_type: str,
        item_name: str,
        unit_price: int,
        quantity: int = 1,
        product_type: AionProductType = AionProductType.GOODS,
        fulfillment_mode: AionFulfillmentMode = AionFulfillmentMode.SELLER_DIRECT,
        condition: float = 1.0,
        quality_label: str | None = None,
        description: str = "",
        current_dt: AnthalysDateTime,
        source_object_id: int | None = None,
        lot_id: int | None = None,
        vehicle_id: int | None = None,
        warehouse_id: int | None = None,
        metadata: dict[str, object] | None = None,
    ) -> AionListing:
        """Crea un listing. `seller` può essere `Character` o `Company`.

        Il `product_type` determina quali riferimenti sono ammessi:
          - GOODS: `source_object_id` opzionale (singolo GameObject)
          - SERVICE: nessun riferimento
          - LOT: `lot_id` obbligatorio, `quantity` deve essere 1
          - VEHICLE: `vehicle_id` obbligatorio, `quantity` deve essere 1
          - STOCK: non supportato in 5.4d (vedi FASE 5.5)
        """
        if not item_type:
            raise AionError("item_type non può essere vuoto")
        if not item_name:
            raise AionError("item_name non può essere vuoto")
        if unit_price <= 0:
            raise AionError(f"unit_price deve essere > 0, ricevuto {unit_price}")
        if quantity < 1:
            raise AionError(f"quantity deve essere >= 1, ricevuto {quantity}")
        if not (0.0 <= condition <= 1.0):
            raise AionError(f"condition deve essere in [0, 1], ricevuto {condition}")

        AionService._validate_listing_refs(
            product_type=product_type,
            quantity=quantity,
            lot_id=lot_id,
            vehicle_id=vehicle_id,
        )

        seller_type, seller_char_id, seller_comp_id = AionService._classify_seller(seller)

        listing = AionListing(
            seller_type=seller_type.value,
            seller_id=int(seller.id),
            product_type=product_type.value,
            item_type=item_type,
            item_name=item_name,
            description=description,
            quantity=quantity,
            quantity_sold=0,
            unit_price=unit_price,
            condition=condition,
            quality_label=quality_label,
            fulfillment_mode=fulfillment_mode.value,
            status=AionListingStatus.ACTIVE.value,
            created_at_total_seconds=current_dt.to_total_seconds(),
            seller_character_id=seller_char_id,
            seller_company_id=seller_comp_id,
            source_object_id=source_object_id,
            lot_id=lot_id,
            vehicle_id=vehicle_id,
            warehouse_id=warehouse_id,
            metadata_json=dict(metadata or {}),
        )
        session.add(listing)
        session.flush()
        logger.debug(
            "AION listing creato: id={} seller={}:{} product={} item={!r} price={} qty={}",
            listing.id,
            seller_type.value,
            seller.id,
            product_type.value,
            item_type,
            unit_price,
            quantity,
        )
        return listing

    @staticmethod
    def cancel_listing(
        session: Session,
        *,
        listing: AionListing,
        current_dt: AnthalysDateTime,
    ) -> None:
        """Cancella un listing (solo se non ha ordini attivi pendenti)."""
        if listing.status == AionListingStatus.CANCELLED.value:
            return
        # Verifica: nessun ordine in PENDING/ESCROWED
        active_orders = list(
            session.scalars(
                select(AionOrder).where(
                    AionOrder.listing_id == listing.id,
                    AionOrder.status.in_(
                        [
                            AionOrderStatus.PENDING.value,
                            AionOrderStatus.ESCROWED.value,
                            AionOrderStatus.SHIPPED.value,
                        ]
                    ),
                )
            )
        )
        if active_orders:
            raise AionError(f"Listing {listing.id} ha {len(active_orders)} ordini attivi")
        listing.status = AionListingStatus.CANCELLED.value
        session.flush()
        logger.debug("AION listing cancellato: id={}", listing.id)

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    @staticmethod
    def get_listing(session: Session, listing_id: int) -> AionListing | None:
        return session.get(AionListing, listing_id)

    @staticmethod
    def get_order(session: Session, order_id: int) -> AionOrder | None:
        return session.get(AionOrder, order_id)

    @staticmethod
    def active_listings(
        session: Session,
        *,
        seller_type: AionSellerType | None = None,
        seller_id: int | None = None,
        item_type: str | None = None,
    ) -> list[AionListing]:
        stmt = select(AionListing).where(AionListing.status == AionListingStatus.ACTIVE.value)
        if seller_type is not None:
            stmt = stmt.where(AionListing.seller_type == seller_type.value)
        if seller_id is not None:
            stmt = stmt.where(AionListing.seller_id == seller_id)
        if item_type is not None:
            stmt = stmt.where(AionListing.item_type == item_type)
        return list(session.scalars(stmt.order_by(AionListing.id)))

    @staticmethod
    def orders_of_buyer(
        session: Session,
        *,
        buyer_type: AionBuyerType,
        buyer_id: int,
    ) -> list[AionOrder]:
        return list(
            session.scalars(
                select(AionOrder)
                .where(
                    AionOrder.buyer_type == buyer_type.value,
                    AionOrder.buyer_id == buyer_id,
                )
                .order_by(AionOrder.id.desc())
            )
        )

    @staticmethod
    def orders_of_listing(session: Session, listing_id: int) -> list[AionOrder]:
        return list(
            session.scalars(
                select(AionOrder)
                .where(AionOrder.listing_id == listing_id)
                .order_by(AionOrder.id.desc())
            )
        )

    # ------------------------------------------------------------------
    # Ordini con escrow
    # ------------------------------------------------------------------

    @staticmethod
    def place_order(
        session: Session,
        *,
        buyer: Character | Company,
        listing: AionListing,
        quantity: int,
        current_dt: AnthalysDateTime,
        auto_ship: bool = True,
    ) -> OrderResult:
        """Crea un ordine, blocca i fondi in escrow, decrementa lo stock del listing.

        Posta una `JournalEntry`:

            DEBIT  aion:escrow            (+)
            CREDIT <buyer>:athel          (−)

        dove `<buyer>` è `char:<id>` o `company:<id>`.
        """
        if quantity < 1:
            return OrderResult(
                False, f"quantity deve essere >= 1, ricevuto {quantity}", None, None, 0
            )
        if isinstance(buyer, Character) and not buyer.is_alive:
            return OrderResult(False, "buyer_not_alive", None, None, 0)
        if listing.status != AionListingStatus.ACTIVE.value:
            return OrderResult(False, f"listing_status={listing.status}", None, None, 0)
        if listing.remaining_quantity < quantity:
            return OrderResult(
                False,
                f"insufficient_stock ({listing.remaining_quantity} < {quantity})",
                None,
                None,
                0,
            )

        unit_price = int(listing.unit_price)
        total = unit_price * quantity
        commission = AionService.preview_commission(
            session,
            seller_type=AionSellerType(listing.seller_type),
            product_type=AionProductType(listing.product_type),
            total_price=total,
        )
        net_to_seller = total - commission

        if int(buyer.athel_balance) < total:
            return OrderResult(
                False,
                f"insufficient_funds ({buyer.athel_balance} < {total})",
                None,
                None,
                0,
            )

        buyer_type, buyer_char_id, buyer_comp_id = AionService._classify_buyer(buyer)

        escrow_acc = AionService._escrow_account(session)
        buyer_acc = AionService._actor_athel_account(session, buyer)
        escrow_entry = LedgerService.post(
            session,
            kind=JournalEntryKind.TRANSFER,
            description=(f"AION escrow: ordine {listing.item_name!r} x{quantity} ({total} Athel)"),
            postings=[
                PostingSpec(
                    account=escrow_acc,
                    direction=PostingDirection.DEBIT,
                    amount=total,
                ),
                PostingSpec(
                    account=buyer_acc,
                    direction=PostingDirection.CREDIT,
                    amount=total,
                ),
            ],
            current_dt=current_dt,
            reference_type="aion_listing",
            reference_id=listing.id,
            metadata={
                "quantity": quantity,
                "unit_price": unit_price,
                "buyer_type": buyer_type.value,
            },
        )

        buyer.athel_balance = int(buyer.athel_balance) - total

        listing.quantity_sold = int(listing.quantity_sold) + quantity
        if listing.remaining_quantity <= 0:
            listing.status = AionListingStatus.SOLD_OUT.value

        order = AionOrder(
            listing_id=listing.id,
            buyer_type=buyer_type.value,
            buyer_id=int(buyer.id),
            buyer_character_id=buyer_char_id,
            buyer_company_id=buyer_comp_id,
            quantity=quantity,
            unit_price=unit_price,
            total_price=total,
            commission=commission,
            net_to_seller=net_to_seller,
            escrowed_amount=total,
            escrow_entry_id=escrow_entry.id,
            settlement_entry_id=None,
            status=AionOrderStatus.ESCROWED.value,
            created_at_total_seconds=current_dt.to_total_seconds(),
            delivered_at_total_seconds=None,
            metadata_json={
                "item_type": listing.item_type,
                "item_name": listing.item_name,
                "fulfillment_mode": listing.fulfillment_mode,
            },
        )
        session.add(order)
        session.flush()
        logger.info(
            "AION order creata: id={} buyer={}:{} listing={} total={} commission={}",
            order.id,
            buyer_type.value,
            buyer.id,
            listing.id,
            total,
            commission,
        )

        if auto_ship:
            ship_result = AionService.ship_order(session, order=order, current_dt=current_dt)
            if not ship_result.ok:
                logger.warning(
                    "AION ship_order fallito per order={}: {}",
                    order.id,
                    ship_result.reason,
                )

        return OrderResult(
            ok=True,
            reason="ok",
            order_id=order.id,
            escrow_entry_id=escrow_entry.id,
            escrowed=total,
        )

    @staticmethod
    def ship_order(
        session: Session,
        *,
        order: AionOrder,
        current_dt: AnthalysDateTime,
    ) -> ShipmentResult:
        """Crea una `AionShipment` per l'ordine.

        Modalità:
          - `DROP_SHIP`: spedizione astratta, durata basata sulla distanza.
          - `SELLER_DIRECT`: se seller e buyer sono nella stessa location
            (o entro `SHIPPING_DELIVERY_RADIUS_CELLS`) → consegna immediata;
            altrimenti spedizione fisica.
          - `AION_WAREHOUSE`: come `SELLER_DIRECT` ma l'origine è il
            magazzino AION (access location).
        """
        if order.status not in (AionOrderStatus.ESCROWED.value,):
            return ShipmentResult(
                ok=False,
                reason=f"order_status={order.status}",
                shipment_id=None,
                mode="",
                duration_ticks=0,
                distance_cells=0.0,
                immediate=False,
            )

        listing = session.get(AionListing, order.listing_id)
        if listing is None:
            return ShipmentResult(False, "listing_missing", None, "", 0, 0.0, False)

        # Origine
        origin_loc: Location | None = None
        origin_char_id: int | None = listing.seller_character_id
        origin_wh_id: int | None = listing.warehouse_id

        if listing.fulfillment_mode == AionFulfillmentMode.AION_WAREHOUSE.value:
            wh = (
                session.get(AionWarehouse, listing.warehouse_id)
                if listing.warehouse_id
                else AionService.get_global_warehouse(session)
            )
            if wh is not None and wh.access_location_id is not None:
                origin_loc = session.get(Location, wh.access_location_id)
                origin_wh_id = wh.id
        else:
            # SELLER_DIRECT: origine = location del seller (Character o Company)
            origin_loc = AionService._seller_origin_location(session, listing)

        # Destinazione
        buyer = (
            session.get(Character, order.buyer_character_id) if order.buyer_character_id else None
        )
        dest_loc: Location | None = None
        if buyer is not None and buyer.location_id is not None:
            dest_loc = session.get(Location, buyer.location_id)

        # Distanza
        distance = AionService._distance_between(origin_loc, dest_loc)
        immediate = listing.fulfillment_mode != AionFulfillmentMode.DROP_SHIP.value and (
            origin_loc is None
            or dest_loc is None
            or origin_loc.id == dest_loc.id
            or distance <= SHIPPING_DELIVERY_RADIUS_CELLS
        )

        duration_ticks = 0 if immediate else max(1, int(distance / CARGO_SPEED_CELLS_PER_TICK) + 1)

        shipping_cost = 0
        if SHIPPING_BASE_COST > 0 or SHIPPING_COST_PER_CELL > 0:
            shipping_cost = int(SHIPPING_BASE_COST + SHIPPING_COST_PER_CELL * distance)

        now_secs = current_dt.to_total_seconds()
        arrives_secs = now_secs + duration_ticks * 5 * 60  # tick_minutes = 5

        shipment = AionShipment(
            order_id=order.id,
            mode=listing.fulfillment_mode,
            status=AionShipmentStatus.IN_TRANSIT.value,
            origin_character_id=origin_char_id,
            origin_location_id=origin_loc.id if origin_loc else None,
            origin_warehouse_id=origin_wh_id,
            destination_character_id=buyer.id if buyer else None,
            destination_location_id=dest_loc.id if dest_loc else None,
            distance_cells=distance,
            duration_ticks=duration_ticks,
            shipping_cost=shipping_cost,
            started_at_total_seconds=now_secs,
            arrives_at_total_seconds=arrives_secs,
            delivered_at_total_seconds=None,
            metadata_json={
                "immediate": immediate,
                "item_type": listing.item_type,
                "quantity": order.quantity,
            },
        )
        session.add(shipment)
        session.flush()

        # Se immediato, consegna subito
        if immediate:
            settle = AionService.confirm_delivery(session, order=order, current_dt=current_dt)
            if not settle.ok:
                return ShipmentResult(
                    False,
                    f"settlement_failed: {settle.reason}",
                    shipment.id,
                    listing.fulfillment_mode,
                    0,
                    distance,
                    True,
                )
            shipment.status = AionShipmentStatus.DELIVERED.value
            shipment.delivered_at_total_seconds = now_secs
            session.flush()
        else:
            order.status = AionOrderStatus.SHIPPED.value
            session.flush()

        logger.info(
            "AION shipment creata: id={} order={} mode={} immediate={} dist={:.1f} duration={}t",
            shipment.id,
            order.id,
            listing.fulfillment_mode,
            immediate,
            distance,
            duration_ticks,
        )
        return ShipmentResult(
            ok=True,
            reason="ok",
            shipment_id=shipment.id,
            mode=listing.fulfillment_mode,
            duration_ticks=duration_ticks,
            distance_cells=distance,
            immediate=immediate,
        )

    @staticmethod
    def tick_shipments(
        session: Session,
        *,
        current_dt: AnthalysDateTime,
    ) -> ShipmentTickReport:
        """Verifica le spedizioni arrivate e completa gli ordini.

        Per ogni `AionShipment` in `IN_TRANSIT` con `arrives_at <= now`:
          1. chiama `confirm_delivery` sull'ordine
          2. marca la shipment `DELIVERED`
        """
        report = ShipmentTickReport()
        now_secs = current_dt.to_total_seconds()
        arrivals = list(
            session.scalars(
                select(AionShipment).where(
                    AionShipment.status == AionShipmentStatus.IN_TRANSIT.value,
                    AionShipment.arrives_at_total_seconds <= now_secs,
                )
            )
        )
        for shipment in arrivals:
            order = session.get(AionOrder, shipment.order_id)
            if order is None:
                shipment.status = AionShipmentStatus.FAILED.value
                report.shipments_failed += 1
                continue
            settle = AionService.confirm_delivery(session, order=order, current_dt=current_dt)
            if settle.ok:
                shipment.status = AionShipmentStatus.DELIVERED.value
                shipment.delivered_at_total_seconds = now_secs
                report.deliveries_completed += 1
                report.order_ids.append(order.id)
            else:
                shipment.status = AionShipmentStatus.FAILED.value
                report.shipments_failed += 1
                logger.warning(
                    "AION shipment {} failed: {}",
                    shipment.id,
                    settle.reason,
                )
        session.flush()
        if report.deliveries_completed > 0:
            logger.info(
                "AION shipments: {} consegnate, {} fallite",
                report.deliveries_completed,
                report.shipments_failed,
            )
        return report

    @staticmethod
    def store_in_warehouse(
        session: Session,
        *,
        warehouse: AionWarehouse,
        item_type: str,
        item_name: str,
        quantity: int,
        current_dt: AnthalysDateTime,
        listing_id: int | None = None,
        object_id: int | None = None,
        condition: float = 1.0,
        quality_label: str | None = None,
    ) -> AionInventoryItem:
        """Stocca un item in un magazzino AION. Aggiorna `used_capacity`."""
        if quantity < 1:
            raise AionError(f"quantity deve essere >= 1, ricevuto {quantity}")
        if warehouse.used_capacity + quantity > warehouse.capacity:
            raise AionError(
                f"Magazzino {warehouse.code} pieno: "
                f"{warehouse.used_capacity + quantity} > {warehouse.capacity}"
            )
        item = AionInventoryItem(
            warehouse_id=warehouse.id,
            listing_id=listing_id,
            object_id=object_id,
            item_type=item_type,
            item_name=item_name,
            quantity=quantity,
            condition=condition,
            quality_label=quality_label,
            status=AionInventoryItemStatus.STORED.value,
            reserved_for_order_id=None,
            stored_at_total_seconds=current_dt.to_total_seconds(),
            metadata_json={},
        )
        session.add(item)
        warehouse.used_capacity = int(warehouse.used_capacity) + quantity
        session.flush()
        return item

    @staticmethod
    def reserve_from_warehouse(
        session: Session,
        *,
        item: AionInventoryItem,
        order: AionOrder,
        quantity: int,
    ) -> None:
        """Riserva `quantity` unità dall'item per l'ordine."""
        if item.status != AionInventoryItemStatus.STORED.value:
            raise AionError(f"Item {item.id} non disponibile (status={item.status})")
        if item.quantity < quantity:
            raise AionError(f"Item {item.id}: {item.quantity} < {quantity}")
        if item.quantity == quantity:
            item.status = AionInventoryItemStatus.RESERVED.value
            item.reserved_for_order_id = order.id
        else:
            # Split: crea un nuovo item riservato e riduce l'originale
            reserved = AionInventoryItem(
                warehouse_id=item.warehouse_id,
                listing_id=item.listing_id,
                object_id=None,
                item_type=item.item_type,
                item_name=item.item_name,
                quantity=quantity,
                condition=item.condition,
                quality_label=item.quality_label,
                status=AionInventoryItemStatus.RESERVED.value,
                reserved_for_order_id=order.id,
                stored_at_total_seconds=item.stored_at_total_seconds,
                metadata_json=dict(item.metadata_json or {}),
            )
            session.add(reserved)
            item.quantity = int(item.quantity) - quantity
        session.flush()

    @staticmethod
    def ship_warehouse_item(
        session: Session,
        *,
        item: AionInventoryItem,
    ) -> None:
        """Marca un item riservato come spedito."""
        if item.status != AionInventoryItemStatus.RESERVED.value:
            raise AionError(f"Item {item.id} non riservato (status={item.status})")
        item.status = AionInventoryItemStatus.SHIPPED.value
        wh = session.get(AionWarehouse, item.warehouse_id)
        if wh is not None:
            wh.used_capacity = max(0, int(wh.used_capacity) - int(item.quantity))
        session.flush()

    @staticmethod
    def confirm_delivery(
        session: Session,
        *,
        order: AionOrder,
        current_dt: AnthalysDateTime,
    ) -> SettlementResult:
        """Rilascia l'escrow: paga il netto al venditore, trattiene la commissione.

        Posta una `JournalEntry`:

            DEBIT  <seller>:athel          (+ net)
            DEBIT  aion:revenue            (+ commission)
            CREDIT aion:escrow             (− total)
        """
        if order.status not in (
            AionOrderStatus.ESCROWED.value,
            AionOrderStatus.SHIPPED.value,
        ):
            return SettlementResult(False, f"status={order.status}", 0, 0, None)

        listing = session.get(AionListing, order.listing_id)
        if listing is None:
            return SettlementResult(False, "listing_missing", 0, 0, None)

        # 1. Trasferimento fisico/legale del bene (prima del settlement finanziario)
        try:
            AionService._transfer_product(
                session, order=order, listing=listing, current_dt=current_dt
            )
        except AionError as exc:
            logger.warning(
                "AION _transfer_product fallito per order={}: {}",
                order.id,
                exc,
            )
            return SettlementResult(False, f"product_transfer_failed: {exc}", 0, 0, None)

        total = int(order.total_price)
        commission = int(order.commission)
        net = int(order.net_to_seller)

        escrow_acc = AionService._escrow_account(session)
        revenue_acc = AionService._revenue_account(session)

        # Risolvi il seller (Character o Company)
        seller: Character | Company | None = None
        if listing.seller_type == AionSellerType.CHARACTER.value:
            if listing.seller_character_id is not None:
                seller = session.get(Character, listing.seller_character_id)
        elif listing.seller_type == AionSellerType.COMPANY.value:
            if listing.seller_company_id is not None:
                seller = session.get(Company, listing.seller_company_id)
        else:
            return SettlementResult(
                False, f"seller_type_unsupported={listing.seller_type}", 0, 0, None
            )
        if seller is None:
            return SettlementResult(False, "seller_missing", 0, 0, None)

        seller_acc = AionService._actor_athel_account(session, seller)

        postings: list[PostingSpec] = [
            PostingSpec(
                account=escrow_acc,
                direction=PostingDirection.CREDIT,
                amount=total,
            ),
            PostingSpec(
                account=seller_acc,
                direction=PostingDirection.DEBIT,
                amount=net,
            ),
        ]
        if commission > 0:
            postings.append(
                PostingSpec(
                    account=revenue_acc,
                    direction=PostingDirection.DEBIT,
                    amount=commission,
                )
            )

        # Verifica quadratura
        debit_sum = sum(p.amount for p in postings if p.direction is PostingDirection.DEBIT)
        credit_sum = sum(p.amount for p in postings if p.direction is PostingDirection.CREDIT)
        if debit_sum != credit_sum:
            raise AionError(
                f"Entry non bilanciata (settlement order={order.id}): "
                f"DEBIT={debit_sum} ≠ CREDIT={credit_sum}"
            )

        settlement_entry = LedgerService.post(
            session,
            kind=JournalEntryKind.SALE,
            description=(
                f"AION settlement: ordine {order.id} (netto={net}, commissione={commission})"
            ),
            postings=postings,
            current_dt=current_dt,
            reference_type="aion_order",
            reference_id=order.id,
            metadata={"listing_id": listing.id, "commission": commission},
        )

        seller.athel_balance = int(seller.athel_balance) + net
        order.settlement_entry_id = settlement_entry.id
        order.status = AionOrderStatus.DELIVERED.value
        order.delivered_at_total_seconds = current_dt.to_total_seconds()
        session.flush()
        logger.info(
            "AION order consegnata: id={} seller={} net={} commission={}",
            order.id,
            AionService._actor_display_name(seller),
            net,
            commission,
        )
        return SettlementResult(
            ok=True,
            reason="ok",
            settled_amount=net,
            commission=commission,
            settlement_entry_id=settlement_entry.id,
        )

    @staticmethod
    def cancel_order(
        session: Session,
        *,
        order: AionOrder,
        current_dt: AnthalysDateTime,
    ) -> SettlementResult:
        """Rimborsa l'escrow al compratore (Character o Company)."""
        if order.status not in (
            AionOrderStatus.ESCROWED.value,
            AionOrderStatus.PENDING.value,
        ):
            return SettlementResult(False, f"status={order.status}", 0, 0, None)

        total = int(order.escrowed_amount)
        if total <= 0:
            return SettlementResult(False, "nothing_to_refund", 0, 0, None)

        buyer: Character | Company | None = None
        if order.buyer_type == AionBuyerType.CHARACTER.value:
            if order.buyer_character_id is not None:
                buyer = session.get(Character, order.buyer_character_id)
        elif order.buyer_type == AionBuyerType.COMPANY.value:
            if order.buyer_company_id is not None:
                buyer = session.get(Company, order.buyer_company_id)
        else:
            return SettlementResult(False, f"buyer_type_unsupported={order.buyer_type}", 0, 0, None)
        if buyer is None:
            return SettlementResult(False, "buyer_missing", 0, 0, None)

        escrow_acc = AionService._escrow_account(session)
        buyer_acc = AionService._actor_athel_account(session, buyer)

        settlement_entry = LedgerService.post(
            session,
            kind=JournalEntryKind.TRANSFER,
            description=f"AION refund: ordine {order.id}",
            postings=[
                PostingSpec(
                    account=buyer_acc,
                    direction=PostingDirection.DEBIT,
                    amount=total,
                ),
                PostingSpec(
                    account=escrow_acc,
                    direction=PostingDirection.CREDIT,
                    amount=total,
                ),
            ],
            current_dt=current_dt,
            reference_type="aion_order",
            reference_id=order.id,
            metadata={"reason": "cancel"},
        )

        buyer.athel_balance = int(buyer.athel_balance) + total
        order.settlement_entry_id = settlement_entry.id
        order.status = AionOrderStatus.REFUNDED.value
        order.escrowed_amount = 0
        session.flush()
        logger.info(
            "AION order rimborsata: id={} buyer={} amount={}",
            order.id,
            AionService._actor_display_name(buyer),
            total,
        )
        return SettlementResult(
            ok=True,
            reason="ok",
            settled_amount=total,
            commission=0,
            settlement_entry_id=settlement_entry.id,
        )

    @staticmethod
    def _seller_origin_location(
        session: Session,
        listing: AionListing,
    ) -> Location | None:
        """Ritorna la location di origine della merce, in base al seller."""
        if listing.seller_type == AionSellerType.CHARACTER.value and listing.seller_character_id:
            seller = session.get(Character, listing.seller_character_id)
            if seller is not None and seller.location_id is not None:
                return session.get(Location, seller.location_id)
            return None
        if listing.seller_type == AionSellerType.COMPANY.value and listing.seller_company_id:
            company = session.get(Company, listing.seller_company_id)
            if company is not None and company.location_id is not None:
                return session.get(Location, company.location_id)
            return None
        return None

    @staticmethod
    def _transfer_product(
        session: Session,
        *,
        order: AionOrder,
        listing: AionListing,
        current_dt: AnthalysDateTime,
    ) -> None:
        """Trasferisce il bene dal seller al buyer in base al `product_type`.

        Solleva `AionError` se il trasferimento non è possibile.
        """
        try:
            ptype = AionProductType(listing.product_type)
        except ValueError as exc:
            raise AionError(f"product_type sconosciuto: {listing.product_type!r}") from exc

        if ptype is AionProductType.SERVICE:
            return  # nessun bene fisico da trasferire
        if ptype is AionProductType.GOODS:
            AionService._transfer_goods(session, order=order, listing=listing)
            return
        if ptype is AionProductType.LOT:
            AionService._transfer_lot(session, order=order, listing=listing, current_dt=current_dt)
            return
        if ptype is AionProductType.VEHICLE:
            AionService._transfer_vehicle(session, order=order, listing=listing)
            return
        # STOCK è bloccato a monte da _validate_listing_refs
        raise AionError(f"product_type non gestito: {ptype.value}")

    @staticmethod
    def _transfer_goods(
        session: Session,
        *,
        order: AionOrder,
        listing: AionListing,
    ) -> None:
        """Assegna il `GameObject` al buyer (solo se `source_object_id` valorizzato).

        Se il buyer è Company, non esiste un campo `owner_company_id` in
        `GameObject`; in quel caso il GameObject resta senza owner e viene
        tracciato in `metadata_json["delivered_to_company"]`.
        """
        if listing.source_object_id is None:
            return  # listing legacy, nessun GameObject collegato
        obj = session.get(GameObject, listing.source_object_id)
        if obj is None:
            logger.debug(
                "AION _transfer_goods: GameObject {} non trovato (order={})",
                listing.source_object_id,
                order.id,
            )
            return
        if order.buyer_type == AionBuyerType.CHARACTER.value and order.buyer_character_id:
            obj.owner_character_id = order.buyer_character_id
        else:
            obj.owner_character_id = None
            md = dict(obj.metadata_json or {})
            md["delivered_to_company"] = order.buyer_company_id
            obj.metadata_json = md

    @staticmethod
    def _transfer_lot(
        session: Session,
        *,
        order: AionOrder,
        listing: AionListing,
        current_dt: AnthalysDateTime,
    ) -> None:
        """Trasferisce la proprietà del lotto dal seller al buyer (Character)."""
        if listing.lot_id is None:
            raise AionError("LOT: lot_id mancante nel listing")
        if order.buyer_type != AionBuyerType.CHARACTER.value:
            raise AionError("LOT: solo Character può acquistare lotti su AION")
        buyer_id = order.buyer_character_id
        if buyer_id is None:
            raise AionError("LOT: buyer_character_id mancante")
        buyer = session.get(Character, buyer_id)
        if buyer is None:
            raise AionError(f"LOT: buyer id={buyer_id} non trovato")
        lot = session.get(Lot, listing.lot_id)
        if lot is None:
            raise AionError(f"LOT: lot id={listing.lot_id} non trovato")

        # Verifica che il seller sia effettivamente l'owner
        current_owner = LotOwnershipService.owner_character(session, lot.id)
        if current_owner is None:
            raise AionError(f"LOT {lot.id} non ha proprietario")
        if (
            listing.seller_type == AionSellerType.CHARACTER.value
            and current_owner.id != listing.seller_id
        ):
            raise AionError(
                f"LOT {lot.id}: seller non è l'owner attuale "
                f"(owner={current_owner.id}, seller={listing.seller_id})"
            )

        # Rilascia e riassegna
        LotOwnershipService.release_all(session, lot.id)
        LotOwnershipService.assign(
            session,
            character=buyer,
            lot=lot,
            share=1.0,
            purchase_price=int(order.total_price),
            current_dt=current_dt,
        )
        logger.info(
            "AION lot trasferito: lot={} da seller={}:{} a char={}",
            lot.id,
            listing.seller_type,
            listing.seller_id,
            buyer.id,
        )

    @staticmethod
    def _transfer_vehicle(
        session: Session,
        *,
        order: AionOrder,
        listing: AionListing,
    ) -> None:
        """Trasferisce la proprietà del veicolo al buyer (Character)."""
        if listing.vehicle_id is None:
            raise AionError("VEHICLE: vehicle_id mancante nel listing")
        if order.buyer_type != AionBuyerType.CHARACTER.value:
            raise AionError("VEHICLE: solo Character può acquistare veicoli su AION")
        buyer_id = order.buyer_character_id
        if buyer_id is None:
            raise AionError("VEHICLE: buyer_character_id mancante")
        buyer = session.get(Character, buyer_id)
        if buyer is None:
            raise AionError(f"VEHICLE: buyer id={buyer_id} non trovato")
        vehicle = session.get(Vehicle, listing.vehicle_id)
        if vehicle is None:
            raise AionError(f"VEHICLE id={listing.vehicle_id} non trovato")

        if (
            listing.seller_type == AionSellerType.CHARACTER.value
            and vehicle.owner_id != listing.seller_id
        ):
            raise AionError(
                f"VEHICLE {vehicle.id}: seller non è l'owner attuale "
                f"(owner={vehicle.owner_id}, seller={listing.seller_id})"
            )

        vehicle.owner_id = buyer.id
        vehicle.location_id = buyer.location_id
        logger.info(
            "AION vehicle trasferito: id={} da seller={}:{} a char={}",
            vehicle.id,
            listing.seller_type,
            listing.seller_id,
            buyer.id,
        )

    @staticmethod
    def _validate_listing_refs(
        *,
        product_type: AionProductType,
        quantity: int,
        lot_id: int | None,
        vehicle_id: int | None,
    ) -> None:
        """Valida coerenza tra `product_type` e riferimenti passati."""
        if product_type is AionProductType.STOCK:
            raise AionError("product_type=STOCK non supportato in 5.4d (arriverà in FASE 5.5)")
        if product_type is AionProductType.LOT:
            if lot_id is None:
                raise AionError("product_type=LOT richiede lot_id")
            if vehicle_id is not None:
                raise AionError("product_type=LOT non ammette vehicle_id")
            if quantity != 1:
                raise AionError(f"LOT: quantity deve essere 1, ricevuto {quantity}")
        elif product_type is AionProductType.VEHICLE:
            if vehicle_id is None:
                raise AionError("product_type=VEHICLE richiede vehicle_id")
            if lot_id is not None:
                raise AionError("product_type=VEHICLE non ammette lot_id")
            if quantity != 1:
                raise AionError(f"VEHICLE: quantity deve essere 1, ricevuto {quantity}")
        elif product_type is AionProductType.SERVICE:
            if lot_id is not None or vehicle_id is not None:
                raise AionError("product_type=SERVICE non ammette lot_id/vehicle_id")
        else:  # GOODS
            if lot_id is not None:
                raise AionError("product_type=GOODS non ammette lot_id")
            if vehicle_id is not None:
                raise AionError("product_type=GOODS non ammette vehicle_id")

    @staticmethod
    def _distance_between(a: Location | None, b: Location | None) -> float:
        """Distanza geometrica (in celle) tra due Location.

        Ritorna `0.0` se una delle due è `None` o coincidono.
        """
        if a is None or b is None or a.id == b.id:
            return 0.0
        ax, ay = a.center()
        bx, by = b.center()
        dx = ax - bx
        dy = ay - by
        return float((dx * dx + dy * dy) ** 0.5)


__all__ = [
    "AionError",
    "AionService",
    "OrderResult",
    "SettlementResult",
    "ShipmentResult",
    "ShipmentTickReport",
]
