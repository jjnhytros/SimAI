"""Enum del dominio economia (mercato, lavoro)."""

from enum import StrEnum


class JobType(StrEnum):
    """Categoria di lavoro."""

    FARMER = "FARMER"
    CRAFTSMAN = "CRAFTSMAN"
    MERCHANT = "MERCHANT"
    TEACHER = "TEACHER"
    HEALER = "HEALER"
    GUARD = "GUARD"
    SERVANT = "SERVANT"
    ARTIST = "ARTIST"
    SCHOLAR = "SCHOLAR"
    LABORER = "LABORER"


#: Salario giornaliero di default (in Athel) per tipo di lavoro.
DEFAULT_WAGES: dict[JobType, int] = {
    JobType.FARMER: 5,
    JobType.CRAFTSMAN: 8,
    JobType.MERCHANT: 10,
    JobType.TEACHER: 7,
    JobType.HEALER: 12,
    JobType.GUARD: 9,
    JobType.SERVANT: 4,
    JobType.ARTIST: 6,
    JobType.SCHOLAR: 8,
    JobType.LABORER: 4,
}


#: Margine trattenuto dal negozio sulla vendita dell'usato.
SHOP_RESALE_MARGIN: float = 0.20


class MortgageStatus(StrEnum):
    """Stato di un mutuo."""

    ACTIVE = "ACTIVE"
    PAID_OFF = "PAID_OFF"
    DEFAULTED = "DEFAULTED"  # 3+ rate mancate
    FORECLOSED = "FORECLOSED"  # pignorato


__all__ = [
    "DEFAULT_WAGES",
    "SHOP_RESALE_MARGIN",
    "JobType",
    "MortgageStatus",
]
