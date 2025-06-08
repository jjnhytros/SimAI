# core/AI/social_manager.py
"""
Definisce la classe SocialManager, responsabile di orchestrare
le interazioni sociali complesse tra NPC.
"""
from typing import TYPE_CHECKING, Optional, Dict, Any
import random

# Import necessari
from core.enums import SocialInteractionType, RelationshipType, NeedType, Gender
from core.modules.actions.social_actions import SocializeAction
from core.config import actions_config # Per le configurazioni delle interazioni
from core import settings

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation

class SocialManager:
    def __init__(self, simulation_context: 'Simulation'):
        """
        Inizializza il SocialManager.

        Args:
            simulation_context (Simulation): L'istanza della simulazione principale.
        """
        self.simulation_context: 'Simulation' = simulation_context
        if settings.DEBUG_MODE:
            print("  [SocialManager INIT] SocialManager creato.")

    def _select_interaction_type(self, initiator: 'Character', target: 'Character') -> SocialInteractionType:
        """
        Seleziona un tipo di interazione sociale appropriato tra due NPC.
        Questa è la tua logica, come l'hai fornita.
        """
        # TODO: Implementare una logica più sofisticata basata su relazione, tratti, umore, contesto.
        relationship_info = initiator.get_relationship_with(target.npc_id)
        
        possible_interactions = [
            # SocialInteractionType.CHAT_CASUAL, # Decommenta se vuoi che sia una possibilità base
            SocialInteractionType.TELL_JOKE, 
            SocialInteractionType.COMPLIMENT
        ]
        
        if relationship_info:
            if relationship_info.score > 30 and hasattr(SocialInteractionType, 'DEEP_CONVERSATION'):
                possible_interactions.append(SocialInteractionType.DEEP_CONVERSATION)
            
            initiator_is_attracted = (target.gender in initiator.get_sexual_attraction() or \
                                    target.gender in initiator.get_romantic_attraction())

            if relationship_info.score > 10 and initiator_is_attracted and hasattr(SocialInteractionType, 'FLIRT'):
                possible_interactions.append(SocialInteractionType.FLIRT)
            
            if relationship_info.score < -20 and hasattr(SocialInteractionType, 'ARGUE'):
                possible_interactions.append(SocialInteractionType.ARGUE)

        if hasattr(SocialInteractionType, 'PROPOSE_INTIMACY') and SocialInteractionType.PROPOSE_INTIMACY in possible_interactions:
            possible_interactions.remove(SocialInteractionType.PROPOSE_INTIMACY)
            
        if not possible_interactions: 
            if hasattr(SocialInteractionType, 'CHAT_CASUAL'):
                return SocialInteractionType.CHAT_CASUAL # Fallback più sicuro
            else:
                raise ValueError("Enum SocialInteractionType non ha membri base come CHAT_CASUAL o COMPLIMENT.")

        return random.choice(possible_interactions)

    def _update_relationship_from_interaction(self, initiator: 'Character', target: 'Character', interaction_action: SocializeAction):
        """
        Questo metodo può essere usato per logiche di post-elaborazione dopo un'interazione.
        La modifica effettiva della relazione avviene in SocializeAction.on_finish().
        """
        if not initiator or not target or not interaction_action:
            return

        if settings.DEBUG_MODE:
            print(f"    [SocialManager] Registrazione/Post-elaborazione interazione "
                f"'{interaction_action.interaction_type.name}' tra {initiator.name} e {target.name}.")
        pass

    def attempt_social_interaction(self, initiator: 'Character', target: 'Character'):
        """
        Metodo pubblico per un NPC (iniziatore) che tenta di avviare 
        un'interazione sociale con un altro NPC (target).
        """
        if not initiator or not target or initiator == target:
            if settings.DEBUG_MODE:
                print(f"    [SocialManager attempt_social_interaction WARN] Iniziatore o target non validi o uguali.")
            return

        # 1. Seleziona il tipo di interazione
        interaction_type = self._select_interaction_type(initiator, target)
        
        if interaction_type is None:
            if settings.DEBUG_MODE:
                print(f"    [SocialManager attempt_social_interaction WARN] Nessun tipo di interazione valido selezionato per {initiator.name} con {target.name}.")
            return

        if settings.DEBUG_MODE:
            print(f"  [SocialManager] {initiator.name} tenta interazione '{interaction_type.name}' con {target.name}.")

        # 2. Recupera la configurazione per l'interazione scelta da actions_config.py
        interaction_config = actions_config.SOCIALIZE_INTERACTION_CONFIGS.get(interaction_type, {})

        # 3. Controlla prerequisiti definiti nella configurazione
        min_score_req = interaction_config.get("min_rel_score_req")
        if min_score_req is not None:
            relationship = initiator.get_relationship_with(target.npc_id)
            if not relationship or relationship.score < min_score_req:
                if settings.DEBUG_MODE:
                    print(f"    [SocialManager] Interazione '{interaction_type.name}' non valida, relazione non sufficiente.")
                return

        # 4. Prepara tutti i parametri per il costruttore di SocializeAction
        constructor_params: Dict[str, Any] = {
            "npc": initiator,
            "simulation_context": self.simulation_context,
            "target_npc": target,
            "interaction_type": interaction_type,
            # Passa tutti i parametri dalla configurazione, con fallback ai default globali
            "duration_ticks": interaction_config.get("duration_ticks", actions_config.SOCIALIZE_DEFAULT_DURATION_TICKS),
            "initiator_social_gain": interaction_config.get("initiator_gain", actions_config.SOCIALIZE_DEFAULT_INITIATOR_GAIN),
            "target_social_gain": interaction_config.get("target_gain", actions_config.SOCIALIZE_DEFAULT_TARGET_GAIN),
            "relationship_score_change": interaction_config.get("rel_change", actions_config.SOCIALIZE_DEFAULT_REL_CHANGE),
            "new_relationship_type_on_success": interaction_config.get("new_rel_type_on_success"),
            "effects_on_target": interaction_config.get("effects_on_target")
        }

        # 5. Crea e valida l'istanza dell'azione
        try:
            social_action_instance = SocializeAction(**constructor_params)
        except TypeError as e:
            if settings.DEBUG_MODE:
                print(f"  [SocialManager ERROR] Errore parametri creando SocializeAction: {e}")
            return

        if social_action_instance.is_valid():
            initiator.add_action_to_queue(social_action_instance)
            if settings.DEBUG_MODE:
                print(f"    [SocialManager] Azione '{social_action_instance.action_type_name}' accodata per {initiator.name}.")
        elif settings.DEBUG_MODE:
            action_name_for_log = getattr(social_action_instance, 'action_type_name', f"SOCIALIZE_{interaction_type.name}")
            print(f"    [SocialManager] Azione '{action_name_for_log}' con {target.name} non valida per {initiator.name}.")