"""Seed del catalogo oggetti demo."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.world.buy.enums import ObjectCategory
from simai.world.buy.models import ObjectCatalog


@dataclass(frozen=True, slots=True)
class CatalogSeedResult:
    """Esito del seed catalogo."""

    created: int
    total: int


# (type_code, name, category, price, w, h, container_cap, interactions, icon)
CATALOG_ENTRIES: list[
    tuple[str, str, ObjectCategory, int, int, int, int | None, list[str], str]
] = [
    # Furniture
    ("sofa", "Divano", ObjectCategory.FURNITURE, 250, 2, 1, None, ["sit", "sleep"], "bi-house"),
    ("armchair", "Poltrona", ObjectCategory.FURNITURE, 120, 1, 1, None, ["sit"], "bi-house"),
    (
        "dining_table",
        "Tavolo da pranzo",
        ObjectCategory.FURNITURE,
        180,
        2,
        2,
        None,
        ["eat", "put"],
        "bi-border-width",
    ),
    ("chair", "Sedia", ObjectCategory.FURNITURE, 40, 1, 1, None, ["sit"], "bi-person"),
    (
        "coffee_table",
        "Tavolino",
        ObjectCategory.FURNITURE,
        90,
        2,
        1,
        None,
        ["put"],
        "bi-border-width",
    ),
    (
        "bed_single",
        "Letto singolo",
        ObjectCategory.FURNITURE,
        150,
        1,
        2,
        None,
        ["sleep", "lie"],
        "bi-moon",
    ),
    (
        "bed_double",
        "Letto matrimoniale",
        ObjectCategory.FURNITURE,
        350,
        2,
        2,
        None,
        ["sleep", "lie"],
        "bi-moon",
    ),
    (
        "wardrobe",
        "Armadio",
        ObjectCategory.STORAGE,
        200,
        2,
        1,
        30,
        ["open", "put", "take"],
        "bi-archive",
    ),
    (
        "bookshelf",
        "Libreria",
        ObjectCategory.STORAGE,
        130,
        2,
        1,
        40,
        ["open", "put", "take"],
        "bi-book",
    ),
    (
        "desk",
        "Scrivania",
        ObjectCategory.FURNITURE,
        140,
        2,
        1,
        None,
        ["work", "put"],
        "bi-briefcase",
    ),
    # Appliances
    (
        "fridge",
        "Frigorifero",
        ObjectCategory.APPLIANCE,
        400,
        1,
        2,
        20,
        ["open", "put", "take"],
        "bi-snow",
    ),
    ("stove", "Forno", ObjectCategory.APPLIANCE, 350, 1, 1, None, ["cook", "power_on"], "bi-fire"),
    (
        "microwave",
        "Microonde",
        ObjectCategory.APPLIANCE,
        150,
        1,
        1,
        None,
        ["cook", "power_on"],
        "bi-fire",
    ),
    (
        "washing_machine",
        "Lavatrice",
        ObjectCategory.APPLIANCE,
        300,
        1,
        1,
        None,
        ["wash"],
        "bi-droplet",
    ),
    (
        "dishwasher",
        "Lavastoviglie",
        ObjectCategory.APPLIANCE,
        280,
        1,
        1,
        None,
        ["wash"],
        "bi-droplet",
    ),
    # Electronics
    (
        "tv_small",
        "TV piccola",
        ObjectCategory.ELECTRONICS,
        200,
        1,
        1,
        None,
        ["watch", "power_on"],
        "bi-tv",
    ),
    (
        "tv_large",
        "TV grande",
        ObjectCategory.ELECTRONICS,
        500,
        2,
        1,
        None,
        ["watch", "power_on"],
        "bi-tv",
    ),
    (
        "computer",
        "Computer",
        ObjectCategory.ELECTRONICS,
        600,
        1,
        1,
        None,
        ["work", "power_on"],
        "bi-pc-display",
    ),
    (
        "radio",
        "Radio",
        ObjectCategory.ELECTRONICS,
        80,
        1,
        1,
        None,
        ["listen", "power_on"],
        "bi-music-note",
    ),
    (
        "lamp_floor",
        "Lampada da terra",
        ObjectCategory.LIGHTING,
        90,
        1,
        1,
        None,
        ["toggle"],
        "bi-lamp",
    ),
    ("lamp_ceiling", "Lampadario", ObjectCategory.LIGHTING, 120, 1, 1, None, ["toggle"], "bi-lamp"),
    # Decor
    (
        "rug_small",
        "Tappeto piccolo",
        ObjectCategory.DECOR,
        40,
        1,
        1,
        None,
        ["walk_on"],
        "bi-square",
    ),
    (
        "rug_large",
        "Tappeto grande",
        ObjectCategory.DECOR,
        100,
        2,
        2,
        None,
        ["walk_on"],
        "bi-square",
    ),
    ("painting", "Quadro", ObjectCategory.DECOR, 60, 1, 1, None, ["look"], "bi-image"),
    ("mirror", "Specchio", ObjectCategory.DECOR, 70, 1, 1, None, ["look"], "bi-circle"),
    ("clock", "Orologio", ObjectCategory.DECOR, 50, 1, 1, None, ["look"], "bi-clock"),
    # Plants
    (
        "plant_small",
        "Pianta piccola",
        ObjectCategory.PLANT,
        25,
        1,
        1,
        None,
        ["water"],
        "bi-flower1",
    ),
    ("plant_large", "Pianta grande", ObjectCategory.PLANT, 80, 1, 1, None, ["water"], "bi-tree"),
    # Plumbing
    ("toilet", "WC", ObjectCategory.PLUMBING, 200, 1, 1, None, ["use"], "bi-droplet"),
    ("sink", "Lavandino", ObjectCategory.PLUMBING, 150, 1, 1, None, ["wash"], "bi-droplet"),
    (
        "bathtub",
        "Vasca da bagno",
        ObjectCategory.PLUMBING,
        400,
        2,
        1,
        None,
        ["wash", "fill"],
        "bi-water",
    ),
    ("shower", "Doccia", ObjectCategory.PLUMBING, 250, 1, 1, None, ["wash"], "bi-water"),
]


def seed_object_catalog(session: Session) -> CatalogSeedResult:
    """Popola `ObjectCatalog` con le voci demo (idempotente)."""
    existing = session.scalars(select(ObjectCatalog)).first()
    if existing is not None:
        total = len(list(session.scalars(select(ObjectCatalog))))
        return CatalogSeedResult(created=0, total=total)

    created = 0
    for (
        code,
        name,
        cat,
        price,
        w,
        h,
        cap,
        interactions,
        icon,
    ) in CATALOG_ENTRIES:
        session.add(
            ObjectCatalog(
                type_code=code,
                name=name,
                category=cat.value,
                base_price=price,
                footprint_w=w,
                footprint_h=h,
                is_wall_mounted=False,
                is_container=cap is not None,
                container_capacity=cap,
                icon=icon,
                interactions_json=list(interactions),
                metadata_json={},
            )
        )
        created += 1
    session.flush()
    return CatalogSeedResult(created=created, total=created)


__all__ = ["CATALOG_ENTRIES", "CatalogSeedResult", "seed_object_catalog"]
