# core/modules/actions/social_actions.py
"""
Definizione delle azioni concrete legate alle interazioni sociali tra NPC.
Riferimento TODO: VI.2.d
"""
from typing import Dict, Optional, TYPE_CHECKING
import random 

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation

from core.enums import NeedType, RelationshipType, SocialInteractionType, ActionType
from core import settings
from .action_base import BaseAction

_MODULE_DEFAULT_SOCIALIZE_CHAT_DURATION_TICKS: int = 30
_MODULE_DEFAULT_SOCIALIZE_DEEP_CONV_DURATION_TICKS: int = 60
_MODULE_DEFAULT_SOCIALIZE_TELL_JOKE_DURATION_TICKS: int = 10
_MODULE_DEFAULT_SOCIALIZE_COMPLIMENT_DURATION_TICKS: int = 5
_MODULE_DEFAULT_SOCIALIZE_FLIRT_DURATION_TICKS: int = 20
_MODULE_DEFAULT_SOCIALIZE_ARGUE_DURATION_TICKS: int = 25

_MODULE_DEFAULT_SOCIALIZE_SOCIAL_GAIN: float = 25.0
_MODULE_DEFAULT_RELATIONSHIP_SCORE_CHANGE: int = 2

class SocializeAction(BaseAction):
    def __init__(self, 
                npc: 'Character', 
                target_npc: 'Character',
                interaction_type: SocialInteractionType,
                simulation_context: 'Simulation',
                duration_ticks: Optional[int] = None 
                ):
        
        self.target_npc: 'Character' = target_npc
        self.interaction_type: SocialInteractionType = interaction_type

        # Qui le costanti di modulo vengono usate come fallback
        module_default_specific_duration = _MODULE_DEFAULT_SOCIALIZE_CHAT_DURATION_TICKS # Esempio di utilizzo
        
        if interaction_type == SocialInteractionType.DEEP_CONVERSATION:
            module_default_specific_duration = _MODULE_DEFAULT_SOCIALIZE_DEEP_CONV_DURATION_TICKS
        elif interaction_type == SocialInteractionType.TELL_JOKE:
            module_default_specific_duration = _MODULE_DEFAULT_SOCIALIZE_TELL_JOKE_DURATION_TICKS
        elif interaction_type == SocialInteractionType.COMPLIMENT:
            module_default_specific_duration = _MODULE_DEFAULT_SOCIALIZE_COMPLIMENT_DURATION_TICKS
        elif interaction_type == SocialInteractionType.FLIRT:
            module_default_specific_duration = _MODULE_DEFAULT_SOCIALIZE_FLIRT_DURATION_TICKS
        elif interaction_type == SocialInteractionType.ARGUE:
            module_default_specific_duration = _MODULE_DEFAULT_SOCIALIZE_ARGUE_DURATION_TICKS
        elif interaction_type == SocialInteractionType.PROPOSE_INTIMACY: 
            module_default_specific_duration = getattr(settings, "SOCIAL_PROPOSE_INTIMACY_DURATION_TICKS", 10)

        actual_duration = duration_ticks 
        if actual_duration is None:
            specific_duration_key = f"SOCIAL_ACT_{interaction_type.name}_DURATION_TICKS" # Chiave per settings
            actual_duration = getattr(settings, specific_duration_key, None) 
            if actual_duration is None: 
                actual_duration = module_default_specific_duration # Fallback al default di modulo

        action_type_name_str = f"ACTION_SOCIALIZE_{interaction_type.name}"
        corresponding_action_type_enum = None
        try:
            corresponding_action_type_enum = ActionType[action_type_name_str]
        except KeyError:
            if settings.DEBUG_MODE:
                print(f"    [SocializeAction WARN] Enum ActionType.{action_type_name_str} non trovato.")

        super().__init__(
            npc=npc,
            action_type_name=action_type_name_str,
            action_type_enum=corresponding_action_type_enum,
            duration_ticks=actual_duration,
            p_simulation_context=simulation_context, 
            is_interruptible=True
        )
        
        if settings.DEBUG_MODE:
            target_name_log = target_npc.name if target_npc else "N/A"
            print(f"    [{self.action_type_name} INIT - {self.npc.name}] Creata con target {target_name_log} "
                  f"(Tipo: {interaction_type.name}, Durata Effettiva: {self.duration_ticks}t)")

    # ... resto della classe (is_valid, on_start, execute_tick, on_finish, on_interrupt_effects) ...
    # Assicurati che tutti i metodi che usano simulation_context lo facciano tramite self.sim_context
    # come definito in BaseAction. Ad esempio:
    # In is_valid():
    # if not self.sim_context: # ...
    # current_location = self.sim_context.get_location_by_id(...)

    def is_valid(self) -> bool:
        if not self.npc or not self.target_npc or self.npc == self.target_npc:
            if settings.DEBUG_MODE and self.npc: print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] NPC ({self.npc.name if self.npc else 'None'}) o Target ({self.target_npc.name if self.target_npc else 'None'}) non validi o uguali.")
            return False

        initiator_social_need = self.npc.get_need_value(NeedType.SOCIAL)
        if initiator_social_need is None: 
            if settings.DEBUG_MODE: print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Impossibile leggere bisogno SOCIAL.")
            return False
        if initiator_social_need >= (settings.NEED_MAX_VALUE - 5): 
            if settings.DEBUG_MODE: print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Bisogno Sociale ({initiator_social_need:.1f}) già troppo alto.")
            return False
            
        if self.target_npc.current_action:
            if self.target_npc.current_action.action_type_enum == ActionType.ACTION_SLEEP:
                if settings.DEBUG_MODE: print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Target {self.target_npc.name} sta dormendo.")
                return False
            if self.target_npc.is_busy and not self.target_npc.current_action.is_interruptible:
                if settings.DEBUG_MODE: print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Target {self.target_npc.name} è occupato ({self.target_npc.current_action.action_type_name}) e non interrompibile.")
                return False
        
        if self.interaction_type == SocialInteractionType.FLIRT:
            initiator_attracted_sexually = self.target_npc.gender in self.npc.get_sexual_attraction()
            initiator_attracted_romantically = self.target_npc.gender in self.npc.get_romantic_attraction()
            if not (initiator_attracted_sexually or initiator_attracted_romantically):
                if settings.DEBUG_MODE: print(f"    [{self.action_type_name} VALIDATE FLIRT - {self.npc.name}] Non è attratto/a da {self.target_npc.name} ({self.target_npc.gender.name}).")
                return False

            target_attracted_sexually = self.npc.gender in self.target_npc.get_sexual_attraction()
            target_attracted_romantically = self.npc.gender in self.target_npc.get_romantic_attraction()
            if not (target_attracted_sexually or target_attracted_romantically):
                if settings.DEBUG_MODE: print(f"    [{self.action_type_name} VALIDATE FLIRT - {self.npc.name}] Target {self.target_npc.name} non sembra attratto/a da {self.npc.gender.name}.")
                return False
            
            relationship = self.npc.get_relationship_with(self.target_npc.npc_id)
            min_rel_score_for_flirt = getattr(settings, "MIN_REL_SCORE_FOR_FLIRT", -10) 
            if relationship and relationship.score < min_rel_score_for_flirt:
                if settings.DEBUG_MODE: print(f"    [{self.action_type_name} VALIDATE FLIRT - {self.npc.name}] Relazione con {self.target_npc.name} troppo negativa ({relationship.score}) per flirt.")
                return False

        if settings.DEBUG_MODE:
            print(f"    [SocializeAction VALIDATE - {self.npc.name}] Azione '{self.action_type_name}' con {self.target_npc.name} considerata valida.")
        return True

    def on_start(self):
        super().on_start()
        if settings.DEBUG_MODE:
            print(f"    [SocializeAction START - {self.npc.name}] Inizia '{self.interaction_type.display_name_it()}' con {self.target_npc.name}.")

    def execute_tick(self):
        super().execute_tick()
        if self.is_started and settings.DEBUG_MODE:
            log_interval = max(1, self.duration_ticks // 3) 
            if self.ticks_elapsed > 0 and self.ticks_elapsed % log_interval == 0 and not self.is_finished:
                print(f"    [SocializeAction PROGRESS - {self.npc.name}] Sta interagendo con {self.target_npc.name}... ({self.get_progress_percentage():.0%})")

    def on_finish(self):
        if not self.npc or not self.target_npc:
            super().on_finish() 
            return

        if settings.DEBUG_MODE:
            print(f"    [{self.action_type_name} FINISH - {self.npc.name}] Interazione '{self.interaction_type.display_name_it()}' con {self.target_npc.name} terminata.")
        
        base_social_gain = getattr(settings, "DEFAULT_SOCIALIZE_SOCIAL_GAIN", _MODULE_DEFAULT_SOCIALIZE_SOCIAL_GAIN)
        base_rel_change = getattr(settings, "DEFAULT_RELATIONSHIP_SCORE_CHANGE_CHAT", _MODULE_DEFAULT_RELATIONSHIP_SCORE_CHANGE)

        initiator_social_gain = base_social_gain
        target_social_gain = base_social_gain * 0.75 
        relationship_score_change = base_rel_change
        
        current_rel_initiator_to_target = self.npc.get_relationship_with(self.target_npc.npc_id)
        new_relationship_type = current_rel_initiator_to_target.type if current_rel_initiator_to_target else RelationshipType.ACQUAINTANCE

        if self.interaction_type == SocialInteractionType.DEEP_CONVERSATION:
            initiator_social_gain = getattr(settings, "SOCIAL_ACT_DEEP_CONVERSATION_INITIATOR_GAIN", base_social_gain * 1.5)
            target_social_gain = getattr(settings, "SOCIAL_ACT_DEEP_CONVERSATION_TARGET_GAIN", base_social_gain * 1.5)
            relationship_score_change = getattr(settings, "SOCIAL_ACT_DEEP_CONVERSATION_REL_CHANGE", base_rel_change * 3)
            if not current_rel_initiator_to_target or current_rel_initiator_to_target.type == RelationshipType.ACQUAINTANCE:
                if (current_rel_initiator_to_target.score if current_rel_initiator_to_target else 0) + relationship_score_change > getattr(settings, "SCORE_THRESHOLD_FOR_FRIENDSHIP", 20):
                    new_relationship_type = RelationshipType.FRIEND_REGULAR
        
        elif self.interaction_type == SocialInteractionType.TELL_JOKE:
            initiator_social_gain = getattr(settings, "SOCIAL_ACT_TELL_JOKE_INITIATOR_GAIN", base_social_gain * 0.8)
            target_social_gain = getattr(settings, "SOCIAL_ACT_TELL_JOKE_TARGET_GAIN", base_social_gain * 1.2)
            relationship_score_change = getattr(settings, "SOCIAL_ACT_TELL_JOKE_REL_CHANGE", base_rel_change * 1)
            fun_gain_for_joke = getattr(settings, "SOCIAL_TELL_JOKE_FUN_GAIN", 15.0)
            if fun_gain_for_joke > 0 and self.target_npc.get_need_value(NeedType.FUN) is not None:
                self.target_npc.change_need_value(NeedType.FUN, fun_gain_for_joke)
                if settings.DEBUG_MODE: print(f"        Effetto FUN su {self.target_npc.name} per barzelletta: +{fun_gain_for_joke:.1f}")
        
        elif self.interaction_type == SocialInteractionType.ARGUE:
            initiator_social_gain = getattr(settings, "SOCIAL_ACT_ARGUE_INITIATOR_GAIN", base_social_gain * -1.0)
            target_social_gain = getattr(settings, "SOCIAL_ACT_ARGUE_TARGET_GAIN", base_social_gain * -1.0)
            relationship_score_change = getattr(settings, "SOCIAL_ACT_ARGUE_REL_CHANGE", base_rel_change * -4)
            if current_rel_initiator_to_target and (current_rel_initiator_to_target.type.name.count("FRIEND") > 0 or current_rel_initiator_to_target.type.name.count("ROMANTIC") > 0 or current_rel_initiator_to_target.type == RelationshipType.ACQUAINTANCE): 
                 new_relationship_type = RelationshipType.ENEMY_DISLIKED
            elif not current_rel_initiator_to_target: new_relationship_type = RelationshipType.ENEMY_DISLIKED
        
        elif self.interaction_type == SocialInteractionType.FLIRT:
            initiator_social_gain = getattr(settings, "SOCIAL_ACT_FLIRT_INITIATOR_GAIN", base_social_gain * 1.2)
            target_social_gain = getattr(settings, "SOCIAL_ACT_FLIRT_TARGET_GAIN", base_social_gain * 0.6)
            relationship_score_change = getattr(settings, "SOCIAL_ACT_FLIRT_REL_CHANGE", base_rel_change * 2)
            if relationship_score_change > 0 and \
               (not current_rel_initiator_to_target or \
                current_rel_initiator_to_target.type in {RelationshipType.ACQUAINTANCE, RelationshipType.FRIEND_REGULAR, RelationshipType.FRIEND_CLOSE}):
                new_relationship_type = RelationshipType.CRUSH
        
        elif self.interaction_type == SocialInteractionType.COMPLIMENT:
            target_social_gain = getattr(settings, "SOCIAL_ACT_COMPLIMENT_TARGET_GAIN", base_social_gain * 1.5)
            initiator_social_gain = getattr(settings, "SOCIAL_ACT_COMPLIMENT_INITIATOR_GAIN", base_social_gain * 0.8)
            relationship_score_change = getattr(settings, "SOCIAL_ACT_COMPLIMENT_REL_CHANGE", base_rel_change * 2)
        
        elif self.interaction_type == SocialInteractionType.OFFER_COMFORT:
             target_social_gain = getattr(settings, "SOCIAL_ACT_OFFER_COMFORT_TARGET_GAIN", base_social_gain * 2.0) 
             initiator_social_gain = getattr(settings, "SOCIAL_ACT_OFFER_COMFORT_INITIATOR_GAIN", base_social_gain * 0.7)
             relationship_score_change = getattr(settings, "SOCIAL_ACT_OFFER_COMFORT_REL_CHANGE", base_rel_change * 3)
        
        elif self.interaction_type == SocialInteractionType.PROPOSE_INTIMACY:
            if settings.DEBUG_MODE: print(f"    [{self.action_type_name} - {self.npc.name}] Proposta di intimità fatta a {self.target_npc.name}. In attesa di decisione del target.")
            if hasattr(self.target_npc, 'pending_intimacy_proposal_from'):
                self.target_npc.pending_intimacy_proposal_from = self.npc.npc_id
                if settings.DEBUG_MODE: print(f"        Flag 'pending_intimacy_proposal_from' impostato per {self.target_npc.name} da {self.npc.name}")
            else: 
                if settings.DEBUG_MODE: print(f"        ATTENZIONE: {self.target_npc.name} non ha l'attributo 'pending_intimacy_proposal_from'.")
            initiator_social_gain = base_social_gain * 0.5 
            # target_social_gain = base_social_gain * 0.2 # Il target non riceve gain sociale dalla proposta
            relationship_score_change = base_rel_change * 0.5 

        if self.interaction_type != SocialInteractionType.PROPOSE_INTIMACY:
            self.npc.change_need_value(NeedType.SOCIAL, initiator_social_gain)
            self.target_npc.change_need_value(NeedType.SOCIAL, target_social_gain) # Target riceve social gain
            if settings.DEBUG_MODE:
                print(f"        Guadagno SOCIAL per {self.npc.name}: {initiator_social_gain:.1f}, per {self.target_npc.name}: {target_social_gain:.1f}")
        elif self.interaction_type == SocialInteractionType.PROPOSE_INTIMACY: 
            self.npc.change_need_value(NeedType.SOCIAL, initiator_social_gain)
            if settings.DEBUG_MODE:
                print(f"        Guadagno SOCIAL (proposta) per {self.npc.name}: {initiator_social_gain:.1f}")

        if self.interaction_type not in {SocialInteractionType.ARGUE, SocialInteractionType.PROPOSE_INTIMACY}:
            is_new_or_superficial_relation = False
            if not current_rel_initiator_to_target: is_new_or_superficial_relation = True
            elif current_rel_initiator_to_target.type == RelationshipType.ACQUAINTANCE and \
                 abs(current_rel_initiator_to_target.score) < getattr(settings, "SUPERFICIAL_RELATION_SCORE_THRESHOLD", 10):
                is_new_or_superficial_relation = True
            if is_new_or_superficial_relation:
                first_impression_mod = random.randint(getattr(settings, "FIRST_IMPRESSION_MIN_MOD", -2), getattr(settings, "FIRST_IMPRESSION_MAX_MOD", 2)) 
                relationship_score_change += first_impression_mod
                if settings.DEBUG_MODE: print(f"        [SocializeAction] Modificatore prima impressione: {first_impression_mod} (Nuovo score change: {relationship_score_change})")
        
        self.npc.update_relationship(
            target_npc_id=self.target_npc.npc_id, 
            new_type=new_relationship_type, 
            score_change=int(relationship_score_change)
        )
        self.target_npc.update_relationship( 
            target_npc_id=self.npc.npc_id, 
            new_type=new_relationship_type, 
            score_change=int(relationship_score_change)
        )
            
        if settings.DEBUG_MODE:
            final_rel = self.npc.get_relationship_with(self.target_npc.npc_id)
            if final_rel:
                print(f"        Relazione finale {self.npc.name} -> {self.target_npc.name}: Tipo={final_rel.type.name}, Score={final_rel.score}")
        
        super().on_finish()

    def on_interrupt_effects(self):
        super().on_interrupt_effects()
        if self.npc and self.target_npc and settings.DEBUG_MODE:
            print(f"    [SocializeAction INTERRUPT - {self.npc.name}] Interazione con {self.target_npc.name} interrotta.")
        # Per ora, l'interruzione non applica un malus specifico, ma potrebbe in futuro.
        # Se self.relationship_change_amount fosse definito, potremmo usarlo:
        # if self.npc and self.target_npc:
        #     interrupt_rel_penalty = -1 # Esempio
        #     # ... logica per applicare penalità ...