# core/modules/traits/__init__.py
"""
Rende la cartella 'traits' un package e riesporta tutte le classi Tratto
per un'importazione centralizzata e più pulita.
"""

# Importa la classe base
from .base_trait import BaseTrait

# Importa i tratti dalle loro sottocartelle di categoria
from .creative.artistic_trait import ArtisticTrait
from .creative.creative_trait import CreativeTrait
from .lifestyle.bookworm_trait import BookwormTrait
from .lifestyle.glutton_trait import GluttonTrait
from .personality.ambitious_trait import AmbitiousTrait
from .personality.childish_trait import ChildishTrait
from .personality.lazy_trait import LazyTrait
from .personality.good_trait import GoodTrait
from .personality.playful_trait import PlayfulTrait
from .personality.uninhibited_trait import UninhibitedTrait
from .physical.active_trait import ActiveTrait
from .social.charmer_trait import CharmerTrait
from .social.loner_trait import LonerTrait
from .social.party_animal_trait import PartyAnimalTrait
from .social.shy_trait import ShyTrait
from .social.social_trait import SocialTrait

# La lista __all__ definisce cosa viene importato con "from core.modules.traits import *"
__all__ = [
    'ActiveTrait',
    'AmbitiousTrait',
    'ArtisticTrait',
    'BaseTrait',
    'BookwormTrait',
    'CharmerTrait',
    'ChildishTrait',
    'CreativeTrait',
    'GluttonTrait',
    'GoodTrait',
    'LazyTrait',
    'LonerTrait',
    'PartyAnimalTrait',
    'PlayfulTrait',
    'ShyTrait',
    'SocialTrait',
    'UninhibitedTrait',
]

    # ...aggiungere i nomi delle altre classi Tratto


from core import settings
if settings.DEBUG_MODE:
    print("  [Traits Package] Package 'core.modules.traits' caricato.")
