# core/modules/traits/active_trait.py
"""
Definizione del tratto di personalità "Attivo" (Active).
Riferimento TODO: IV.3.b
"""
from typing import TYPE_CHECKING

from core.enums.trait_types import TraitType
from core.enums.need_types import NeedType # Per identificare il bisogno di Energia
from .base_trait import BaseTrait

if TYPE_CHECKING:
    from core.character import Character

class ActiveTrait(BaseTrait):
    """
    Tratto per gli NPC che sono energici e amano muoversi.
    Effetti:
    - Il bisogno di Energia decade più lentamente.
    - (Futuro) Il bisogno di Divertimento potrebbe decadere più velocemente se sedentari.
    - (Futuro) Preferenza per azioni attive/sportive.
    """
    def __init__(self, character_owner: 'Character'):
        super().__init__(
            trait_type=TraitType.ACTIVE,
            character_owner=character_owner
        )

    def get_need_decay_modifier(self, need_type: 'NeedType', base_decay_rate: float) -> float:
        """
        Modifica il tasso di decadimento del bisogno di Energia.
        Un tasso di decadimento è tipicamente negativo (es. -5.0 all'ora per ENERGY).
        Un modificatore di 0.8 lo renderà -4.0 (decade il 20% più lentamente).
        """
        if need_type == NeedType.ENERGY:
            # Rallenta il decadimento dell'energia (moltiplica per un valore < 1)
            # Se base_decay_rate è -5.0, restituisce -5.0 * 0.8 = -4.0
            return base_decay_rate * 0.8
        
        return base_decay_rate # Nessuna modifica per altri bisogni

    # Esempio per futuro effetto sul guadagno di energia (non implementato attivamente ora)
    # def get_need_satisfaction_modifier(self, need_type: 'NeedType', base_satisfaction_gain: float) -> float:
    #     """
    #     Potrebbe leggermente aumentare l'efficacia del sonno o del riposo.
    #     """
    #     if need_type == NeedType.ENERGY and base_satisfaction_gain > 0: # Se è un guadagno di energia
    #         return base_satisfaction_gain * 1.05 # 5% più efficace
    #     return base_satisfaction_gain