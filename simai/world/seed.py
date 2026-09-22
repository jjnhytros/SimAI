"""Seed di un mondo demo (usato dalla CLI `simai world seed`)."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from simai.world.enums import (
    DistrictType,
    EdgeKind,
    LocationType,
    LotUsage,
)
from simai.world.game_object_service import create_object
from simai.world.location_service import (
    add_edge,
    create_location,
    list_locations,
)
from simai.world.lot_service import create_district, create_lot


@dataclass(frozen=True, slots=True)
class SeedResult:
    """Risultato del seed: conteggi inseriti."""

    districts_created: int
    lots_created: int
    locations_created: int
    edges_created: int
    objects_created: int


def seed_demo_world(session: Session) -> SeedResult:
    """Popola il DB con un mondo demo (idempotente).

    Struttura:
        Quartiere "Centro" (RESIDENTIAL)
        ├── Lotto Casa (RESIDENTIAL, is_developed)
        │   └── Casa (BUILDING)
        │       ├── Soggiorno
        │       ├── Cucina
        │       ├── Camera
        │       ├── Bagno
        │       └── Giardino (OUTDOOR)
        ├── Lotto Negozio 1 (COMMERCIAL)
        │   └── Bottega del Fornaio (SHOP)
        ├── Lotto Negozio 2 (COMMERCIAL)
        │   └── Fucina del Fabbro (SHOP)
        ├── Lotto Negozio 3 (COMMERCIAL)
        │   └── Emporio Centrale (SHOP)
        ├── Lotto Emporio Arredi (COMMERCIAL)
        │   └── Emporio dell'Arredo (SHOP)
        └── Parco Comunale (PARK, vacant)
    """
    existing = list_locations(session)
    if existing:
        return SeedResult(0, 0, 0, 0, 0)

    # --- Quartiere ---
    center = create_district(
        session,
        name="Centro",
        type_=DistrictType.RESIDENTIAL,
        bounds=(0, 0, 100, 100),
        tax_rate=0.06,
        safety_rating=0.75,
        aesthetic_score=0.65,
    )

    # --- Location (spazi fisici) ---
    house = create_location(
        session,
        name="Casa",
        type_=LocationType.BUILDING,
        bounds=(0, 0, 20, 15),
        capacity=8,
    )
    living = create_location(
        session,
        name="Soggiorno",
        type_=LocationType.ROOM,
        parent_id=house.id,
        bounds=(0, 0, 10, 8),
        capacity=6,
    )
    kitchen = create_location(
        session,
        name="Cucina",
        type_=LocationType.ROOM,
        parent_id=house.id,
        bounds=(10, 0, 10, 8),
        capacity=4,
    )
    bedroom = create_location(
        session,
        name="Camera",
        type_=LocationType.ROOM,
        parent_id=house.id,
        bounds=(0, 8, 10, 7),
        capacity=3,
    )
    bathroom = create_location(
        session,
        name="Bagno",
        type_=LocationType.ROOM,
        parent_id=house.id,
        bounds=(10, 8, 10, 7),
        capacity=2,
    )
    garden = create_location(
        session,
        name="Giardino",
        type_=LocationType.OUTDOOR,
        parent_id=house.id,
        bounds=(20, 0, 15, 15),
        capacity=20,
    )
    shop_bakery = create_location(
        session,
        name="Bottega del Fornaio",
        type_=LocationType.SHOP,
        bounds=(50, 0, 10, 10),
        capacity=8,
    )
    shop_smith = create_location(
        session,
        name="Fucina del Fabbro",
        type_=LocationType.SHOP,
        bounds=(62, 0, 10, 10),
        capacity=6,
    )
    shop_market = create_location(
        session,
        name="Emporio Centrale",
        type_=LocationType.SHOP,
        bounds=(74, 0, 12, 12),
        capacity=15,
    )
    shop_furniture = create_location(
        session,
        name="Emporio dell'Arredo",
        type_=LocationType.SHOP,
        bounds=(90, 0, 14, 14),
        capacity=20,
    )
    shop_supplies = create_location(
        session,
        name="Forniture del Quartiere",
        type_=LocationType.SHOP,
        bounds=(106, 0, 12, 12),
        capacity=15,
    )

    # --- Lot (proprietà) ---
    create_lot(
        session,
        district_id=center.id,
        name="Lotto Casa Centrale",
        usage=LotUsage.RESIDENTIAL,
        bounds=(0, 0, 35, 15),
        base_price=2500,
        location_id=house.id,
        is_developed=True,
    )
    create_lot(
        session,
        district_id=center.id,
        name="Lotto Negozio 1",
        usage=LotUsage.COMMERCIAL,
        bounds=(50, 0, 10, 10),
        base_price=1800,
        location_id=shop_bakery.id,
        is_developed=True,
    )
    create_lot(
        session,
        district_id=center.id,
        name="Lotto Negozio 2",
        usage=LotUsage.COMMERCIAL,
        bounds=(62, 0, 10, 10),
        base_price=1500,
        location_id=shop_smith.id,
        is_developed=True,
    )
    create_lot(
        session,
        district_id=center.id,
        name="Lotto Negozio 3",
        usage=LotUsage.COMMERCIAL,
        bounds=(74, 0, 12, 12),
        base_price=2200,
        location_id=shop_market.id,
        is_developed=True,
    )
    create_lot(
        session,
        district_id=center.id,
        name="Lotto Emporio Arredi",
        usage=LotUsage.COMMERCIAL,
        bounds=(90, 0, 14, 14),
        base_price=3000,
        location_id=shop_furniture.id,
        is_developed=True,
    )
    create_lot(
        session,
        district_id=center.id,
        name="Parco Comunale",
        usage=LotUsage.PARK,
        bounds=(30, 50, 40, 40),
        base_price=0,
        is_developed=False,
    )
    create_lot(
        session,
        district_id=center.id,
        name="Lotto Forniture",
        usage=LotUsage.COMMERCIAL,
        bounds=(106, 0, 12, 12),
        base_price=2000,
        location_id=shop_supplies.id,
        is_developed=True,
    )

    # --- Edges (bidirezionali) ---
    edges = [
        (living.id, kitchen.id, EdgeKind.DOOR, 1.0),
        (living.id, bedroom.id, EdgeKind.DOOR, 1.0),
        (bedroom.id, bathroom.id, EdgeKind.DOOR, 1.0),
        (kitchen.id, bathroom.id, EdgeKind.DOOR, 1.0),
        (living.id, garden.id, EdgeKind.OUTDOOR, 2.0),
        (living.id, shop_bakery.id, EdgeKind.OUTDOOR, 3.0),
        (living.id, shop_smith.id, EdgeKind.OUTDOOR, 4.0),
        (living.id, shop_market.id, EdgeKind.OUTDOOR, 5.0),
        (living.id, shop_furniture.id, EdgeKind.OUTDOOR, 6.0),
        (living.id, shop_supplies.id, EdgeKind.OUTDOOR, 7.0),
    ]
    for fid, tid, kind, dist in edges:
        add_edge(session, from_id=fid, to_id=tid, kind=kind, distance=dist)

    # --- Oggetti di arredo di base (dentro la casa) ---
    objects = [
        ("Divano", "furniture", living.id, None, ["sit", "sleep"]),
        ("Tavolo basso", "furniture", living.id, None, ["put"]),
        ("TV", "electronics", living.id, None, ["watch", "power_on"]),
        ("Forno", "appliance", kitchen.id, None, ["cook", "power_on"]),
        ("Frigorifero", "appliance", kitchen.id, 20, ["open", "put", "take"]),
        ("Tavolo da pranzo", "furniture", kitchen.id, None, ["sit", "eat"]),
        ("Letto", "furniture", bedroom.id, None, ["sleep", "sit"]),
        ("Armadio", "furniture", bedroom.id, 30, ["open", "put", "take"]),
        ("Lavandino", "fixture", bathroom.id, None, ["wash", "fill"]),
        ("Doccia", "fixture", bathroom.id, None, ["wash"]),
        ("Panchina giardino", "furniture", garden.id, None, ["sit"]),
    ]
    for name, type_, loc_id, cap, inter in objects:
        create_object(
            session,
            name=name,
            type_=type_,
            location_id=loc_id,
            container_capacity=cap,
            interactions=inter,
        )

    # --- Cataloghi negozi (ShopItem per cibo/beni di consumo) ---
    from simai.economy.models import ShopItem

    catalogs: list[tuple[int, str, str, int, int]] = [
        (shop_bakery.id, "bread", "Pane", 2, -1),
        (shop_bakery.id, "pastry", "Dolce", 4, 20),
        (shop_bakery.id, "flour", "Farina (sacco)", 8, 10),
        (shop_smith.id, "tool", "Attrezzo", 15, 8),
        (shop_smith.id, "knife", "Coltello", 20, 5),
        (shop_smith.id, "horseshoe", "Ferro di cavallo", 3, -1),
        (shop_market.id, "cloth", "Stoffa (rotolo)", 6, -1),
        (shop_market.id, "candle", "Candela", 1, -1),
        (shop_market.id, "soap", "Sapone", 3, -1),
        (shop_market.id, "rope", "Corda", 5, -1),
    ]
    for shop_id, itype, iname, price, stock in catalogs:
        session.add(
            ShopItem(
                location_id=shop_id,
                item_type=itype,
                item_name=iname,
                base_price=price,
                current_price=price,
                stock=stock,
                metadata_json={},
            )
        )

    # --- Catalogo arredi (collegato a ObjectCatalog.type_code) ---
    from simai.world.buy.seed import CATALOG_ENTRIES

    for entry in CATALOG_ENTRIES:
        code, _name, _cat, price, *_rest = entry
        # 20% markup sul prezzo base, stock iniziale 10
        markup_price = int(price * 1.20)
        session.add(
            ShopItem(
                location_id=shop_furniture.id,
                item_type=code,
                item_name=code,
                base_price=markup_price,
                current_price=markup_price,
                stock=10,
                metadata_json={"category": "furniture"},
            )
        )

    # --- Risorse per crafting ---
    from simai.npc.crafting import RESOURCE_NAMES, RESOURCE_PRICES

    for code, name in RESOURCE_NAMES.items():
        price = RESOURCE_PRICES.get(code, 2)
        session.add(
            ShopItem(
                location_id=shop_supplies.id,
                item_type=code,
                item_name=name,
                base_price=price,
                current_price=price,
                stock=-1,  # risorse illimitate per ora
                metadata_json={"category": "resource"},
            )
        )

    session.flush()

    # --- Catalogo oggetti (Buy mode) ---
    from simai.world.buy.seed import seed_object_catalog

    seed_object_catalog(session)

    # --- Catalogo stili (Style mode) ---
    from simai.world.style.seed import seed_style_catalog

    seed_style_catalog(session)

    # --- Servizi pubblici demo (City) ---
    from simai.city.seed import seed_demo_city

    seed_demo_city(session)

    from simai.city.transport.seed import seed_demo_routes

    seed_demo_routes(session)

    return SeedResult(
        districts_created=1,
        lots_created=7,
        locations_created=11,
        edges_created=len(edges),
        objects_created=len(objects),
    )


__all__ = ["SeedResult", "seed_demo_world"]
