# core/modules/traits/__init__.py
"""
Rende la cartella 'traits' un package e riesporta tutte le classi Tratto
per un'importazione centralizzata e più pulita.
"""

# Importa la classe base
from .base_trait import BaseTrait

# Importa i tratti dalle loro sottocartelle di categoria
from .personality.ambitious_trait import AmbitiousTrait
from .personality.lazy_trait import LazyTrait
from .personality.childish_trait import ChildishTrait
from .personality.playful_trait import PlayfulTrait

from .social.charmer_trait import CharmerTrait
from .social.loner_trait import LonerTrait
from .social.shy_trait import ShyTrait
from .social.social_trait import SocialTrait

from .creative.artistic_trait import ArtisticTrait
from .creative.creative_trait import CreativeTrait

from .lifestyle.bookworm_trait import BookwormTrait
from .lifestyle.glutton_trait import GluttonTrait

from .physical.active_trait import ActiveTrait


# La lista __all__ definisce cosa viene importato con "from core.modules.traits import *"
__all__ = [
    'BaseTrait',
    'AmbitiousTrait',
    'LazyTrait',
    'ChildishTrait',
    'PlayfulTrait',
    'CharmerTrait',
    'LonerTrait',
    'ShyTrait',
    'SocialTrait',
    'ArtisticTrait',
    'CreativeTrait',
    'BookwormTrait',
    'GluttonTrait',
    'ActiveTrait',
]

    # ...aggiungere i nomi delle altre classi Tratto


from core import settings
if settings.DEBUG_MODE:
    print("  [Traits Package] Package 'core.modules.traits' caricato.")
