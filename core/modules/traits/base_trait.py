# core/modules/traits/base_trait.py
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional, Dict, Any, List 

from core.enums import TraitType, NeedType, ActionType 
# Assumiamo che NeedType e altri Enum necessari siano importati se usati nei type hint dei metodi
from core.enums import NeedType

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation # Aggiunto per il type hint
    from core.modules.actions.action_base import BaseAction # Aggiunto per il nuovo metodo
    # from core.enums import ActionType, EventType, RelationshipType 
    # from core.world.moodlet import Moodlet
    # from core.modules.actions import BaseAction

class BaseTrait(ABC):
    # Questi attributi possono essere definiti nelle sottoclassi
    trait_type: TraitType
    display_name: str
    description: str

    def __init__(self, character_owner: 'Character'):
        self.character_owner: 'Character' = character_owner

    @abstractmethod
    def get_on_add_effects(self) -> Optional[Dict[str, Any]]:
        return None

    @abstractmethod
    def get_on_remove_effects(self) -> Optional[Dict[str, Any]]:
        return None

    def get_need_satisfaction_modifier(self, need_type: NeedType, satisfaction_value_from_action: float) -> float:
        """
        Permette al tratto di modificare il valore di soddisfazione di un bisogno
        derivante da un'azione.
        Per impostazione predefinita, non modifica il valore (moltiplicatore 1.0).
        Le sottoclassi possono sovrascrivere questo metodo per implementare logiche specifiche.

        Args:
            need_type (NeedType): Il tipo di bisogno che viene soddisfatto.
            satisfaction_value_from_action (float): Il valore base di soddisfazione fornito dall'azione.

        Returns:
            float: Il modificatore da applicare al valore di soddisfazione (es. 1.0 per nessuna modifica,
                1.2 per un aumento del 20%, 0.8 per una riduzione del 20%).
                Nota: il codice chiamante (AIDecisionMaker) si aspetta un moltiplicatore.
        """
        return 1.0 # Default: nessun modificatore

    def get_behavioral_action_modifier(self, action: 'BaseAction', simulation_context: 'Simulation') -> float:
        """
        Restituisce un modificatore di punteggio basato su regole comportamentali specifiche del tratto.
        Permette a un tratto di "vetare" o penalizzare pesantemente un'azione in base al contesto.
        Restituisce 1.0 per default (nessun impatto).
        """
        return 1.0

    def get_action_choice_priority_modifier(self, 
                                        action_type: ActionType, 
                                        simulation_context: 'Simulation' # Aggiunto per coerenza con la chiamata
                                        ) -> float:
        """
        Permette al tratto di modificare il punteggio/priorità di un'azione potenziale.
        Per impostazione predefinita, non modifica la priorità (moltiplicatore 1.0).
        Le sottoclassi possono sovrascrivere questo metodo.

        Args:
            action_type (ActionType): Il tipo di azione che si sta valutando.
            simulation_context (Simulation): Il contesto della simulazione, utile se il tratto
                                            necessita di informazioni sul mondo per decidere.

        Returns:
            float: Un moltiplicatore da applicare allo score dell'azione (es. 1.0 per nessuna modifica).
        """
        return 1.0 # Default: nessun modificatore di priorità

    # --- Altri metodi esistenti o placeholder ---
    # def get_need_decay_modifier(self, need_type: 'NeedType', base_decay_rate: float) -> float:
    #     return base_decay_rate

    # def get_skill_gain_modifier(self, skill_type: 'SkillType', base_gain_rate: float) -> float:
    #     return base_gain_rate
    
    # def get_action_priority_modifier(self, action_type: 'ActionType', base_priority: float) -> float:
    #     return base_priority

    def __str__(self) -> str:
        return self.display_name

    def __repr__(self) -> str:
        owner_name = self.character_owner.name if self.character_owner else "Nessun Proprietario"
        return f"<{self.__class__.__name__} (Trait: {self.trait_type.name}, NPC: {owner_name})>"