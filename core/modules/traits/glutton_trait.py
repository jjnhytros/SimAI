# core/modules/traits/glutton_trait.py
"""
Definizione del tratto di personalità "Goloso" (Glutton).
Riferimento TODO: IV.3.b
"""
from typing import TYPE_CHECKING

from core.enums.trait_types import TraitType
from core.enums.need_types import NeedType # Per identificare il bisogno di Fame
from .base_trait import BaseTrait

if TYPE_CHECKING:
    from core.character import Character

class GluttonTrait(BaseTrait):
    """
    Tratto per gli NPC che sono golosi.
    Effetti:
    - Il bisogno di Fame decade più velocemente.
    - Potrebbe cercare cibo più spesso o mangiare porzioni più grandi (futuro).
    """
    def __init__(self, character_owner: 'Character'):
        super().__init__(
            trait_type=TraitType.GLUTTON, 
            character_owner=character_owner
        )

    def get_need_decay_modifier(self, need_type: 'NeedType', base_decay_rate: float) -> float:
        """
        Modifica il tasso di decadimento del bisogno di Fame.
        Un tasso di decadimento è tipicamente negativo (es. -4.0 all'ora).
        Un modificatore di 1.5 lo renderà -6.0 (decade il 50% più velocemente).
        """
        if need_type == NeedType.HUNGER:
            # Aumenta il tasso di decadimento (rende il valore più negativo se base_decay_rate è negativo)
            # Ad esempio, se base_decay_rate è -4.0, restituisce -4.0 * 1.5 = -6.0
            # Se base_decay_rate fosse positivo (improbabile per il decadimento), lo aumenterebbe.
            # Assumiamo che base_decay_rate sia il valore orario da settings (es. -4.2 per HUNGER)
            return base_decay_rate * 1.5 # Decade il 50% più velocemente
        
        return base_decay_rate # Nessuna modifica per altri bisogni