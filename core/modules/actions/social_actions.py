# core/modules/actions/social_actions.py
from typing import Dict, Optional, TYPE_CHECKING
import random 

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation

from core.enums import NeedType, RelationshipType, SocialInteractionType, ActionType
from .action_base import BaseAction
from core.settings import DEBUG_MODE
class SocializeAction(BaseAction):
    def __init__(self, 
                npc: 'Character', 
                simulation_context: 'Simulation',
                target_npc: 'Character',
                interaction_type: SocialInteractionType,
                # --- Parametri di configurazione ora iniettati ---
                duration_ticks: int,
                initiator_social_gain: float,
                target_social_gain: float,
                relationship_score_change: int,
                # Parametri opzionali
                new_relationship_type_on_success: Optional[RelationshipType] = None,
                effects_on_target: Optional[Dict[NeedType, float]] = None
                ):
        
        self.target_npc: 'Character' = target_npc
        self.interaction_type: SocialInteractionType = interaction_type

        # Salva i parametri specifici dell'interazione
        self.initiator_social_gain: float = initiator_social_gain
        self.target_social_gain: float = target_social_gain
        self.relationship_score_change: int = relationship_score_change
        self.new_rel_type_on_success: Optional[RelationshipType] = new_relationship_type_on_success
        self.effects_on_target: Dict[NeedType, float] = effects_on_target or {}

        action_type_name_str = f"ACTION_SOCIALIZE_{interaction_type.name}"
        # Trova l'enum ActionType corrispondente, se esiste
        corresponding_action_type_enum = getattr(ActionType, action_type_name_str, ActionType.ACTION_SOCIALIZE)

        super().__init__(
            npc=npc,
            action_type_name=action_type_name_str,
            action_type_enum=corresponding_action_type_enum,
            duration_ticks=duration_ticks,
            p_simulation_context=simulation_context, 
            is_interruptible=True
        )
        
        # L'effetto primario sull'iniziatore è sul bisogno SOCIAL
        self.effects_on_needs = {NeedType.SOCIAL: self.initiator_social_gain}

    def is_valid(self) -> bool:
        # La logica di validazione rimane simile, ma può essere semplificata
        if not self.npc or not self.target_npc or self.npc == self.target_npc: return False
        
        # Potremmo aggiungere qui controlli basati su parametri iniettati, es:
        # relationship = self.npc.get_relationship_with(self.target_npc.npc_id)
        # if relationship and self.min_rel_score_req is not None and relationship.score < self.min_rel_score_req:
        #     return False

        # ... (altri controlli esistenti su target occupato, dormendo, attrazione per flirt, ecc.) ...
        return True

    def on_finish(self):
        if not self.npc or not self.target_npc:
            super().on_finish()
            return

        if DEBUG_MODE:
            print(f"    [{self.action_type_name} FINISH - {self.npc.name}] Interazione '{self.interaction_type.name}' terminata. Applico effetti.")
        
        # Applica effetti sui bisogni all'iniziatore
        for need_type, amount in self.effects_on_needs.items():
            self.npc.change_need_value(need_type, amount)

        # Applica effetti sui bisogni al target
        self.target_npc.change_need_value(NeedType.SOCIAL, self.target_social_gain)
        if self.effects_on_target:
            for need_type, amount in self.effects_on_target.items():
                self.target_npc.change_need_value(need_type, amount)

        # Aggiorna la relazione
        # La logica per determinare il nuovo tipo di relazione ora è più semplice
        # o può essere passata direttamente come parametro.
        rel_type_to_set = self.new_rel_type_on_success
        # Se non viene passato un nuovo tipo specifico, manteniamo quello corrente (o ACQUAINTANCE se non c'è)
        if rel_type_to_set is None:
            current_rel = self.npc.get_relationship_with(self.target_npc.npc_id)
            rel_type_to_set = current_rel.type if current_rel else RelationshipType.ACQUAINTANCE
        
        self.npc.update_relationship(
            target_npc_id=self.target_npc.npc_id, 
            new_type=rel_type_to_set, 
            score_change=self.relationship_score_change
        )
        self.target_npc.update_relationship( 
            target_npc_id=self.npc.npc_id, 
            new_type=rel_type_to_set,
            score_change=self.relationship_score_change
        )
        
        super().on_finish()

    # ... (on_start, execute_tick, on_interrupt_effects rimangono simili, ma on_interrupt_effects
    #      dovrebbe usare i parametri d'istanza per calcolare gli effetti parziali) ...