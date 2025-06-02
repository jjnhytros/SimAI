# core/modules/traits/bookworm_trait.py
"""
Definizione del tratto di personalità "Topo di Biblioteca" (Bookworm).
Riferimento TODO: IV.3.b (nel TODO_Generale.md)
"""
from typing import TYPE_CHECKING

from core.enums.trait_types import TraitType
from core.enums.need_types import NeedType
from core.enums.action_types import ActionType
from core.enums.fun_activity_types import FunActivityType # Per controllare l'attività specifica
from .base_trait import BaseTrait
# Importa HaveFunAction per controllare il tipo di azione
from ..actions.fun_actions import HaveFunAction


if TYPE_CHECKING:
    from core.character import Character
    from core.modules.actions import BaseAction # Per il type hint di get_action_preference_modifier

class BookwormTrait(BaseTrait):
    """
    Tratto per gli NPC che amano leggere e imparare.
    Effetti:
    - Il bisogno Sociale potrebbe decadere leggermente più velocemente.
    - Forte preferenza per l'attività di leggere libri per divertimento.
    - (Futuro) Bonus all'apprendimento di skill tramite lettura.
    """
    def __init__(self, character_owner: 'Character'):
        super().__init__(
            trait_type=TraitType.BOOKWORM,
            character_owner=character_owner
        )

    def get_need_decay_modifier(self, need_type: NeedType, base_decay_rate: float) -> float:
        """
        Leggere è spesso un'attività solitaria, quindi il bisogno sociale potrebbe
        decadere un po' più velocemente se l'NPC passa molto tempo a leggere.
        """
        if need_type == NeedType.SOCIAL:
            # Aumenta il tasso di decadimento (rende il valore più negativo)
            return base_decay_rate * 1.2 # Decade il 20% più velocemente
        return base_decay_rate

    def get_action_preference_modifier(self, action: 'BaseAction', character: 'Character') -> float:
        """
        Aumenta significativamente la preferenza per l'azione di leggere libri.
        Potrebbe anche diminuire la preferenza per attività FUN molto fisiche o superficiali (non implementato ora).
        """
        if isinstance(action, HaveFunAction):
            # Controlla specificamente se l'attività di HaveFunAction è leggere
            have_fun_action = action # Rinomina per chiarezza
            if have_fun_action.activity_type == FunActivityType.READ_BOOK_FOR_FUN:
                return 2.0 # Molto più propenso a scegliere di leggere (valore da bilanciare)
        
        # Per ora, non modifica la preferenza per altre azioni
        return 1.0