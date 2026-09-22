"""Enum del dominio città."""

from __future__ import annotations

from enum import StrEnum
from typing import Final


class PublicServiceType(StrEnum):
    """Tipo di servizio pubblico."""

    HOSPITAL = "HOSPITAL"
    SCHOOL = "SCHOOL"
    POLICE = "POLICE"
    FIRE = "FIRE"
    GARBAGE = "GARBAGE"
    PARK = "PARK"


class TaxKind(StrEnum):
    """Tipo di tassa."""

    INCOME = "INCOME"
    PROPERTY = "PROPERTY"
    SALES = "SALES"


#: Aliquote di default.
INCOME_TAX_RATE: Final[float] = 0.10  # 10% sullo stipendio
SALES_TAX_RATE: Final[float] = 0.05  # 5% sugli acquisti
# Property tax: già in District.tax_rate

#: Costo giornaliero di default per tipo di servizio.
DEFAULT_DAILY_COST: Final[dict[PublicServiceType, int]] = {
    PublicServiceType.HOSPITAL: 50,
    PublicServiceType.SCHOOL: 35,
    PublicServiceType.POLICE: 40,
    PublicServiceType.FIRE: 30,
    PublicServiceType.GARBAGE: 20,
    PublicServiceType.PARK: 5,
}

#: Qualità iniziale di default.
DEFAULT_QUALITY: Final[float] = 0.6

#: Raggio di copertura di default (in celle della griglia mondiale).
DEFAULT_COVERAGE_RADIUS: Final[int] = 40

#: Soglia sopra cui il servizio è "eccellente".
QUALITY_GOOD_THRESHOLD: Final[float] = 0.75

#: Soglia sotto cui il servizio è "scarso".
QUALITY_POOR_THRESHOLD: Final[float] = 0.40


__all__ = [
    "DEFAULT_COVERAGE_RADIUS",
    "DEFAULT_DAILY_COST",
    "DEFAULT_QUALITY",
    "INCOME_TAX_RATE",
    "QUALITY_GOOD_THRESHOLD",
    "QUALITY_POOR_THRESHOLD",
    "SALES_TAX_RATE",
    "PublicServiceType",
    "TaxKind",
]
