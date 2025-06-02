# core/modules/traits/active_trait.py
"""
Definizione del tratto di personalità "Attivo" (Active).
Riferimento TODO: IV.3.b
"""
from typing import TYPE_CHECKING

from core.enums.trait_types import TraitType
from core.enums.need_types import NeedType # Per identificare il bisogno di Energia
from core.enums.action_types import ActionType
from .base_trait import BaseTrait
from core.settings import (
    NEED_CRITICAL_THRESHOLD, NEED_LOW_THRESHOLD
)
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

    def get_need_decay_modifier(self, need_type: NeedType, base_decay_rate: float) -> float: # Cambiato NeedTypeHint a NeedType
        if need_type == NeedType.ENERGY:
            return base_decay_rate * 0.8
        return base_decay_rate

    def get_need_urgency_modifier(self, need_type: NeedType, current_urgency_score: float) -> float: # Cambiato NeedTypeHint a NeedType
        if need_type == NeedType.ENERGY:
            energy_value = self._character_owner.get_need_value(NeedType.ENERGY)
            if energy_value is not None and energy_value > NEED_CRITICAL_THRESHOLD:
                return current_urgency_score * 0.8
        return current_urgency_score

    def get_action_preference_modifier(self, action_type: ActionType, character: 'Character') -> float:
        """
        Aumenta la preferenza per azioni FUN attive (se l'azione è HaveFunAction e
        l'activity_type è appropriato) e diminuisce leggermente quella per dormire se non stanco.
        """
        if action_type == ActionType.ACTION_HAVE_FUN:
            # Per fare questo in modo più preciso, avremmo bisogno di accedere all'activity_type
            # dell'azione specifica se `action_type` è solo l'enum generico.
            # Per ora, potremmo dare un piccolo boost generale a HAVE_FUN,
            # o la logica andrà in AIDecisionMaker quando considera specificamente HaveFunAction.
            # Per ora, un piccolo boost generale al divertimento.
            return 1.2 # 20% più propenso a divertirsi
        
        if action_type == ActionType.ACTION_SLEEP:
            energy_value = character.get_need_value(NeedType.ENERGY)
            if energy_value is not None and energy_value > NEED_LOW_THRESHOLD: # Se non è particolarmente stanco
                return 0.7 # Meno propenso a dormire subito
        return 1.0
