# core/modules/traits/__init__.py
from core.settings import DEBUG_MODE

from .base_trait import BaseTrait
from core.modules.traits.lifestyle import (ArtisticTrait,BookwormTrait,CreativeTrait,GluttonTrait,)
# from core.modules.traits.mental import ()
from core.modules.traits.personality import (AmbitiousTrait,ChildishTrait,LazyTrait,PlayfulTrait,)
from core.modules.traits.physical import (ActiveTrait,)
from core.modules.traits.social import (CharmerTrait,LonerTrait,ShyTrait,SocialTrait)
# from core.modules.traits.work import ()

# Import dei tratti esistenti (che avrai spostato nelle loro sottocartelle)


# Import dei nuovi tratti di esempio


# Aggiungi qui gli altri tratti man mano che li crei e categorizzi

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
    'LazyTrait',
    'LonerTrait',
    'PlayfulTrait',
    'ShyTrait',
    'SocialTrait',

    # ...aggiungere i nomi delle altre classi Tratto
]

if DEBUG_MODE: print("  [Traits Package] Package 'core.modules.traits' caricato.")