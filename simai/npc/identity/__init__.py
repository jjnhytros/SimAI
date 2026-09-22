"""Package `simai.npc.identity` — identità sessuale, SEP, cultura."""

from simai.npc.identity.enums import (
    TRADITION_RANGES,
    CulturalTradition,
    TabooReaction,
)
from simai.npc.identity.gender import (
    GenderIdentity,
    is_cisgender,
    is_heterosexual,
    parse_gender,
)
from simai.npc.identity.lgbtq import (
    DEFAULT_DISCLOSURE_LENIENT,
    DEFAULT_DISCLOSURE_MODERATE,
    DEFAULT_DISCLOSURE_SEVERE,
    PUBLIC_DISCLOSURE_THRESHOLD,
    LGBTQService,
)
from simai.npc.identity.models import (
    SEP,
    CulturalProfile,
    IdentityProfile,
    Sexuality,
)
from simai.npc.identity.service import (
    CULTURE_INHERITANCE_WEIGHT,
    FLUIDITY_MAX_AGE_YEARS,
    FLUIDITY_SIGMA,
    IdentityService,
)

__all__ = [
    "CULTURE_INHERITANCE_WEIGHT",
    "DEFAULT_DISCLOSURE_LENIENT",
    "DEFAULT_DISCLOSURE_MODERATE",
    "DEFAULT_DISCLOSURE_SEVERE",
    "FLUIDITY_MAX_AGE_YEARS",
    "FLUIDITY_SIGMA",
    "PUBLIC_DISCLOSURE_THRESHOLD",
    "SEP",
    "TRADITION_RANGES",
    "CulturalProfile",
    "CulturalTradition",
    "GenderIdentity",
    "IdentityProfile",
    "IdentityService",
    "LGBTQService",
    "Sexuality",
    "TabooReaction",
    "is_cisgender",
    "is_heterosexual",
    "parse_gender",
]
