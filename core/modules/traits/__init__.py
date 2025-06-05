# core/modules/traits/__init__.py
from core.settings import DEBUG_MODE

from .base_trait import BaseTrait # BaseTrait è ora qui
# Import dei tratti esistenti (che avrai spostato nelle loro sottocartelle)
from .physical.active_trait import ActiveTrait
from .lifestyle.bookworm_trait import BookwormTrait
from .lifestyle.glutton_trait import GluttonTrait
from .social.loner_trait import LonerTrait # LonerTrait dalla tua nuova enum

# Import dei nuovi tratti di esempio
from .personality.ambitious_trait import AmbitiousTrait
from .personality.lazy_trait import LazyTrait
from .social.social_trait import SocialTrait # Per TraitType.SOCIAL
from .lifestyle.creative_trait import CreativeTrait # Per TraitType.CREATIVE

# Aggiungi qui gli altri tratti man mano che li crei e categorizzi

__all__ = [
    'BaseTrait',
    # Esistenti (presumendo siano stati smistati)
    'ActiveTrait',
    'BookwormTrait',
    'GluttonTrait',
    'LonerTrait',
    # Nuovi esempi
    'AmbitiousTrait',
    'LazyTrait',
    'SocialTrait',
    'CreativeTrait',
    # ...aggiungere i nomi delle altre classi Tratto
]

if DEBUG_MODE: print("  [Traits Package] Package 'core.modules.traits' caricato.")