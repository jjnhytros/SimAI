"""Enum del dominio World."""

from enum import StrEnum


class LocationType(StrEnum):
    """Tipo di location."""

    ROOM = "ROOM"
    BUILDING = "BUILDING"
    LOT = "LOT"
    DISTRICT = "DISTRICT"
    OUTDOOR = "OUTDOOR"
    SHOP = "SHOP"


class EdgeKind(StrEnum):
    """Tipo di connessione tra due location."""

    DOOR = "DOOR"
    CORRIDOR = "CORRIDOR"
    OUTDOOR = "OUTDOOR"
    STAIRS = "STAIRS"
    ELEVATOR = "ELEVATOR"


class GameObjectState(StrEnum):
    """Stato fisico di un GameObject."""

    NEW = "NEW"
    CLEAN = "CLEAN"
    USED = "USED"
    DIRTY = "DIRTY"
    BROKEN = "BROKEN"
    IN_USE = "IN_USE"
    DISCARDED = "DISCARDED"


class DistrictType(StrEnum):
    """Tipo di quartiere."""

    RESIDENTIAL = "RESIDENTIAL"
    COMMERCIAL = "COMMERCIAL"
    INDUSTRIAL = "INDUSTRIAL"
    MIXED = "MIXED"
    RURAL = "RURAL"


class LotUsage(StrEnum):
    """Uso del suolo di un lotto."""

    RESIDENTIAL = "RESIDENTIAL"
    COMMERCIAL = "COMMERCIAL"
    INDUSTRIAL = "INDUSTRIAL"
    PUBLIC = "PUBLIC"
    VACANT = "VACANT"
    PARK = "PARK"


__all__ = [
    "DistrictType",
    "EdgeKind",
    "GameObjectState",
    "LocationType",
    "LotUsage",
]
