# core/modules/traits/loner_trait.py
"""
Definizione del tratto di personalità "Solitario" (Loner).
Riferimento TODO: IV.3.b (nel TODO_Generale.md)
"""
from typing import TYPE_CHECKING

from core.enums.trait_types import TraitType
from core.enums.need_types import NeedType
from core.enums.action_types import ActionType
from .base_trait import BaseTrait

if TYPE_CHECKING:
    from core.character import Character

class LonerTrait(BaseTrait):
    """
    Tratto per gli NPC che preferiscono la solitudine.
    Effetti:
    - Il bisogno Sociale decade più lentamente.
    - Minore preferenza per azioni sociali dirette.
    - (Futuro) Preferenza per attività FUN solitarie.
    """
    def __init__(self, character_owner: 'Character'):
        super().__init__(
            trait_type=TraitType.LONER,
            character_owner=character_owner
        )

    def get_need_decay_modifier(self, need_type: NeedType, base_decay_rate: float) -> float:
        """
        Rallenta il decadimento del bisogno Sociale.
        """
        if need_type == NeedType.SOCIAL:
            # Se il tasso base è -2.5, * 0.5 lo rende -1.25 (decade il 50% più lentamente)
            return base_decay_rate * 0.5 
        return base_decay_rate

    def get_action_preference_modifier(self, action_type: ActionType, character: 'Character') -> float:
        """
        Diminuisce la preferenza per le azioni di socializzazione.
        """
        # Controlliamo specifici tipi di azione sociale. Potremmo voler essere più granulari.
        social_action_types = [
            ActionType.ACTION_SOCIALIZE_CHAT,
            ActionType.ACTION_SOCIALIZE_COMPLIMENT,
            # ActionType.ACTION_SOCIALIZE_INSULT, # Forse un solitario potrebbe insultare?
            ActionType.ACTION_SOCIALIZE_TELL_JOKE,
            ActionType.ACTION_SOCIALIZE_PROPOSE_INTIMACY # Un solitario potrebbe comunque cercare intimità, ma meno proattivamente
        ]
        if action_type in social_action_types:
            return 0.6 # 40% meno propenso a scegliere queste azioni sociali (valore da bilanciare)
        
        # Potrebbe anche dare un piccolo boost a certe azioni FUN solitarie qui,
        # ma per ora lo lasciamo per un'integrazione più avanzata con FunActivityType.
        # if action_type == ActionType.ACTION_HAVE_FUN:
            # Qui dovremmo controllare l'activity_type dell'azione HaveFun,
            # il che richiederebbe di passare l'istanza dell'azione o più contesto.
            # Per ora, nessun modificatore specifico per HAVE_FUN da questo tratto.

        return 1.0