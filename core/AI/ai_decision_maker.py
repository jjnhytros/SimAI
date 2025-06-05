# core/AI/ai_decision_maker.py
from typing import Optional, TYPE_CHECKING, List, Dict, Tuple
import random

from core.enums import (
    NeedType, ActionType, TraitType, LifeStage, FunActivityType,
    SocialInteractionType # Assicurati che SocialInteractionType sia importato
)
from core.modules.actions.action_base import BaseAction
from core.modules.actions.energy_actions import SleepAction
from core.modules.actions.hunger_actions import EatAction
from core.modules.actions.thirst_actions import DrinkAction
from core.modules.actions.bathroom_actions import UseBathroomAction
from core.modules.actions.fun_actions import HaveFunAction
from core.modules.actions.social_actions import SocializeAction # Importa la tua SocializeAction

from core.config import npc_config, time_config 
from core import settings 

if TYPE_CHECKING:
    from core.character import Character
    # Se Simulation è in un package genitore (es. simai.core.simulation)
    # e ai_decision_maker è in simai.core.AI, l'import relativo è corretto.
    from ..simulation import Simulation 
    from ..modules.time_manager import TimeManager 
    # from .ai_coordinator import AICoordinator # Rimosso se non usato direttamente qui

class AIDecisionMaker:
    BASE_ACTION_CHECK_INTERVAL_TICKS = 10 
    
    NEED_WEIGHTS = {
        NeedType.HUNGER: 1.5,
        NeedType.THIRST: 1.6, 
        NeedType.ENERGY: 1.4,
        NeedType.BLADDER: 1.3,
        NeedType.HYGIENE: 1.0,
        NeedType.FUN: 0.8,
        NeedType.SOCIAL: 0.7,
        NeedType.INTIMACY: 0.6,
        # Aggiungere pesi per altri bisogni (COMFORT, SAFETY, etc.) quando implementati
    }
    CRITICAL_NEED_THRESHOLD_MODIFIER = 1.5 

    def __init__(self, npc: 'Character'):
        self.npc: 'Character' = npc
        self.ticks_since_last_base_action_check: int = 0
        self.last_selected_action_type: Optional[ActionType] = None
        self.consecutive_action_type_count: int = 0
        self.MAX_CONSECUTIVE_SAME_ACTION = 3 # Definisci questa costante se non già presente

    def _get_critical_need_modifier(self, need_value: float) -> float:
        critical_threshold = npc_config.NEED_CRITICAL_THRESHOLD \
            if hasattr(npc_config, 'NEED_CRITICAL_THRESHOLD') else 10.0
        if need_value <= critical_threshold:
            return self.CRITICAL_NEED_THRESHOLD_MODIFIER
        return 1.0

    def _calculate_action_score(self, action_effects: Dict[NeedType, float]) -> float:
        total_score = 0.0
        if not self.npc.needs:
            return 0.0

        for need_type, effect_value in action_effects.items():
            if effect_value <= 0: 
                continue

            need_obj = self.npc.needs.get(need_type)
            if not need_obj:
                continue

            current_need_value = need_obj.get_value()
            
            max_need = npc_config.NEED_MAX_VALUE if hasattr(npc_config, 'NEED_MAX_VALUE') else 100.0
            desirability = 1.0 - (current_need_value / max_need)
            
            base_weight = self.NEED_WEIGHTS.get(need_type, 0.5) 
            critical_modifier = self._get_critical_need_modifier(current_need_value)
            
            trait_modifier = 1.0
            for trait in self.npc.traits.values(): 
                if hasattr(trait, 'get_need_satisfaction_modifier'): 
                    trait_modifier *= trait.get_need_satisfaction_modifier(need_type, effect_value)

            need_score = effect_value * desirability * base_weight * critical_modifier * trait_modifier
            total_score += need_score
            
        return total_score

    def decide_next_action(self, time_manager: 'TimeManager', simulation_context: 'Simulation') -> Optional[BaseAction]:
        self.ticks_since_last_base_action_check += 1
        if self.ticks_since_last_base_action_check < self.BASE_ACTION_CHECK_INTERVAL_TICKS:
            return None
        self.ticks_since_last_base_action_check = 0

        most_pressing_need_type: Optional[NeedType] = None
        highest_urgency_score: float = -float('inf')

        if not self.npc.needs:
            if settings.DEBUG_MODE: print(f"  [AI Decide - {self.npc.name}] NPC non ha bisogni definiti.")
            return None

        for need_type_enum, need_obj in self.npc.needs.items():
            current_value = need_obj.get_value()
            max_val = npc_config.NEED_MAX_VALUE if hasattr(npc_config, 'NEED_MAX_VALUE') else 100.0
            
            urgency = (1.0 - (current_value / max_val)) * \
                      self.NEED_WEIGHTS.get(need_type_enum, 0.5) * \
                    self._get_critical_need_modifier(current_value)
            
            if urgency > highest_urgency_score:
                highest_urgency_score = urgency
                most_pressing_need_type = need_type_enum

        if settings.DEBUG_MODE and most_pressing_need_type:
            print(f"  [AI Decide - {self.npc.name}] Bisogno più pressante: {most_pressing_need_type.name} (Urgenza: {highest_urgency_score:.2f})")
        elif settings.DEBUG_MODE:
            print(f"  [AI Decide - {self.npc.name}] Nessun bisogno pressante identificato.")

        best_action_candidate: Optional[BaseAction] = None
        highest_action_score: float = -1.0

        potential_actions_map: Dict[NeedType, type] = {
            NeedType.HUNGER: EatAction,
            NeedType.ENERGY: SleepAction,
            NeedType.THIRST: DrinkAction,
            NeedType.BLADDER: UseBathroomAction,
            NeedType.HYGIENE: UseBathroomAction,
            NeedType.FUN: HaveFunAction,
            NeedType.SOCIAL: SocializeAction,
        }

        if most_pressing_need_type is not None and most_pressing_need_type in potential_actions_map:
            action_class_to_try = potential_actions_map[most_pressing_need_type]
            action_candidate: Optional[BaseAction] = None

            try:
                if action_class_to_try == SleepAction:
                    base_sleep_hours = getattr(settings, 'SLEEP_ACTION_DEFAULT_HOURS', 7.0)
                    adjusted_sleep_hours = base_sleep_hours
                    if self.npc.life_stage in [LifeStage.INFANCY, LifeStage.EARLY_CHILDHOOD, LifeStage.MIDDLE_CHILDHOOD, LifeStage.ADOLESCENCE]:
                        adjusted_sleep_hours = getattr(settings, 'SLEEP_HOURS_CHILD_TEEN', 9.0) 
                    elif self.npc.life_stage == LifeStage.ELDERLY:
                        adjusted_sleep_hours = getattr(settings, 'SLEEP_HOURS_ELDERLY', 8.0)
                    
                    config_energy_gain_per_hour = getattr(settings, 'SLEEP_ACTION_ENERGY_GAIN_PER_HOUR', 15.0)
                    config_validation_threshold = getattr(settings, 'ENERGY_THRESHOLD_TO_CONSIDER_SLEEP', 
                                                        (settings.NEED_LOW_THRESHOLD + 10) if hasattr(settings, 'NEED_LOW_THRESHOLD') else 40.0)
                    config_on_finish_energy_target = getattr(settings, 'NEED_MAX_VALUE', 100.0)
                    config_on_finish_needs_adjust = {
                        NeedType.HUNGER: getattr(settings, 'NEED_VALUE_ON_WAKE_HUNGER', 70.0),
                        NeedType.THIRST: getattr(settings, 'NEED_VALUE_ON_WAKE_THIRST', 75.0),
                        NeedType.BLADDER: getattr(settings, 'NEED_VALUE_ON_WAKE_BLADDER', 80.0)
                    }

                    action_candidate = SleepAction(
                        npc=self.npc, 
                        simulation_context=simulation_context,
                        duration_hours=adjusted_sleep_hours,
                        energy_gain_per_hour=config_energy_gain_per_hour,
                        validation_threshold=config_validation_threshold,
                        on_finish_energy_target=config_on_finish_energy_target,
                        on_finish_needs_adjust=config_on_finish_needs_adjust
                    )
                
                elif action_class_to_try == EatAction:
                    # TODO: Rifattorizzare EatAction e passare le sue configurazioni qui
                    # Esempio:
                    # eat_config_hunger_gain = getattr(settings, 'EAT_ACTION_HUNGER_GAIN', 60.0)
                    # action_candidate = EatAction(npc=self.npc, simulation_context=simulation_context,
                    #                            hunger_gain=eat_config_hunger_gain)
                    action_candidate = EatAction(npc=self.npc, simulation_context=simulation_context)
                
                elif action_class_to_try == DrinkAction:
                    # TODO: Rifattorizzare DrinkAction e passare le sue configurazioni qui
                    # Esempio:
                    # drink_config_thirst_gain = getattr(settings, 'DRINK_ACTION_THIRST_GAIN', 40.0)
                    # drink_config_drink_type = "WATER" # o letto da settings
                    # action_candidate = DrinkAction(npc=self.npc, simulation_context=simulation_context, 
                    #                              drink_type=drink_config_drink_type, 
                    #                              thirst_gain=drink_config_thirst_gain)
                    action_candidate = DrinkAction(npc=self.npc, simulation_context=simulation_context, drink_type="WATER")

                elif action_class_to_try == UseBathroomAction:
                    # TODO: Rifattorizzare UseBathroomAction e passare le sue configurazioni qui
                    # Esempio:
                    # bathroom_config_hygiene_gain = getattr(settings, 'USEBATHROOM_HYGIENE_GAIN', 50.0)
                    # bathroom_config_bladder_relief = getattr(settings, 'USEBATHROOM_BLADDER_RELIEF', 100.0)
                    # action_candidate = UseBathroomAction(npc=self.npc, simulation_context=simulation_context, 
                    #                                    for_need=most_pressing_need_type,
                    #                                    hygiene_gain=bathroom_config_hygiene_gain,
                    #                                    bladder_relief=bathroom_config_bladder_relief)
                    action_candidate = UseBathroomAction(npc=self.npc, simulation_context=simulation_context, for_need=most_pressing_need_type)
                
                elif action_class_to_try == HaveFunAction:
                    # TODO: Rifattorizzare HaveFunAction e passare le sue configurazioni qui
                    available_activities = list(FunActivityType) if FunActivityType else []
                    chosen_activity = random.choice(available_activities) if available_activities else (FunActivityType.DAYDREAM if FunActivityType and hasattr(FunActivityType, 'DAYDREAM') else None)
                    
                    if chosen_activity:
                        # Esempio:
                        # fun_config_fun_gain = getattr(settings, f"FUN_ACTIVITY_{chosen_activity.name}_GAIN", 20.0)
                        # fun_config_duration_hours = getattr(settings, f"FUN_ACTIVITY_{chosen_activity.name}_HOURS", 1.0)
                        # action_candidate = HaveFunAction(npc=self.npc, simulation_context=simulation_context, 
                        #                                activity_type=chosen_activity,
                        #                                fun_gain=fun_config_fun_gain,
                        #                                duration_hours=fun_config_duration_hours)
                        action_candidate = HaveFunAction(npc=self.npc, simulation_context=simulation_context, activity_type=chosen_activity)
                    else: 
                        if settings.DEBUG_MODE: print(f"  [AI Decide WARN - {self.npc.name}] FunActivityType non definito o DAYDREAM mancante.")
                
                elif action_class_to_try == SocializeAction:
                    target_id_str: Optional[str] = None
                    target_character_obj: Optional['Character'] = None 
                    interaction_type_to_use: Optional[SocialInteractionType] = None # Inizializza a None

                    if simulation_context and self.npc.current_location_id:
                        current_loc = simulation_context.get_location_by_id(self.npc.current_location_id)
                        if current_loc:
                            potential_targets_ids = [oid for oid in current_loc.npcs_present_ids if oid != self.npc.npc_id]
                            if potential_targets_ids:
                                target_id_str = random.choice(potential_targets_ids)
                                if target_id_str:
                                    target_character_obj = simulation_context.get_npc_by_id(target_id_str) # Usa get_npc_by_id
                    
                    if target_character_obj:
                        # --- Logica per scegliere SocialInteractionType ---
                        # TODO: Questa logica deve essere più sofisticata.
                        # Per ora, se il target esiste, usiamo CHAT come default.
                        # Assicurati che SocialInteractionType.CHAT esista nel tuo Enum!
                        if SocialInteractionType and hasattr(SocialInteractionType, 'CHAT'):
                            #interaction_type_to_use = SocialInteractionType.CHAT
                            pass
                        else:
                            # Fallback se CHAT non esiste o l'enum non è popolato
                            # Potresti scegliere il primo membro dell'enum o loggare un errore più specifico
                            if settings.DEBUG_MODE: print(f"    [AI Decide WARN - {self.npc.name}] SocialInteractionType.CHAT non definito! Serve una logica di fallback.")
                            # Prova a prendere il primo tipo disponibile come fallback estremo
                            if SocialInteractionType:
                                try:
                                    interaction_type_to_use = list(SocialInteractionType)[0]
                                except IndexError:
                                    pass # Lascia interaction_type_to_use = None

                        if interaction_type_to_use: # Procedi solo se un tipo è stato scelto
                            # TODO: Recuperare da settings le configurazioni specifiche per SocializeAction
                            # e interaction_type_to_use e passarle al costruttore.
                            action_candidate = SocializeAction(
                                npc=self.npc, 
                                simulation_context=simulation_context, 
                                target_npc=target_character_obj,
                                interaction_type=interaction_type_to_use
                            )
                        # else: # Se interaction_type_to_use è ancora None dopo i fallback
                        # if settings.DEBUG_MODE:
                        # print(f"    [AI Decide WARN - {self.npc.name}] Impossibile determinare SocialInteractionType per SocializeAction con {target_character_obj.name}.")

                    elif settings.DEBUG_MODE:
                        print(f"    [AI Decide WARN - {self.npc.name}] Nessun target Character valido trovato per SocializeAction.")
                
                if action_candidate and action_candidate.is_valid():
                    # Assicurati che action_candidate.effects_on_needs sia definito in BaseAction o nelle sottoclassi
                    # Se non tutte le azioni hanno 'effects_on_needs', dovrai gestirlo (es. passare un dizionario vuoto)
                    action_effects = getattr(action_candidate, 'effects_on_needs', {}) 
                    score = self._calculate_action_score(action_effects)
                    
                    if self.last_selected_action_type == action_candidate.action_type_enum:
                        score *= (1.0 - (self.consecutive_action_type_count * 0.25))
                    
                    if action_candidate.action_type_enum is not None: # Controlla se action_type_enum è valido
                        for trait_obj in self.npc.traits.values():
                            score_modifier_from_trait = trait_obj.get_action_choice_priority_modifier(
                                action_candidate.action_type_enum, # Ora è sicuramente un ActionType
                                simulation_context
                            )
                            score *= score_modifier_from_trait
                    elif settings.DEBUG_MODE and action_candidate.action_type_name:
                        print(f"    [AI Score WARN - {self.npc.name}] action_type_enum è None per {action_candidate.action_type_name}. Modificatore tratto non applicato.")
                        
                    if score > highest_action_score:
                        highest_action_score = score
                        best_action_candidate = action_candidate
            
            except Exception as e:
                if settings.DEBUG_MODE:
                    action_class_name = action_class_to_try.__name__ if action_class_to_try else 'Azione Sconosciuta'
                    need_name = most_pressing_need_type.name if most_pressing_need_type else 'Bisogno Sconosciuto'
                    print(f"  [AI Decide ERROR - {self.npc.name}] Eccezione durante creazione/valutazione di {action_class_name} per {need_name}: {e}")

        if best_action_candidate:
            if self.last_selected_action_type == best_action_candidate.action_type_enum:
                self.consecutive_action_type_count += 1
                if self.consecutive_action_type_count >= self.MAX_CONSECUTIVE_SAME_ACTION:
                    if settings.DEBUG_MODE:
                        print(f"  [AI Decide - {self.npc.name}] Raggiunto max ripetizioni per {best_action_candidate.action_type_name}. NPC non fa nulla.")
                    return None 
            else:
                self.consecutive_action_type_count = 0
            self.last_selected_action_type = best_action_candidate.action_type_enum
        else: 
            self.consecutive_action_type_count = 0
            self.last_selected_action_type = None

        if best_action_candidate and settings.DEBUG_MODE:
            print(f"  [AI Decide - {self.npc.name}] Azione Scelta: {best_action_candidate.action_type_name} (Score: {highest_action_score:.2f}) per bisogno {most_pressing_need_type.name if most_pressing_need_type else 'N/D'}")
        elif not best_action_candidate and settings.DEBUG_MODE and most_pressing_need_type:
            print(f"  [AI Decide - {self.npc.name}] Nessuna azione valida trovata per il bisogno {most_pressing_need_type.name}.")

        return best_action_candidate

    def reset_decision_state(self):
        self.ticks_since_last_base_action_check = self.BASE_ACTION_CHECK_INTERVAL_TICKS 
        self.last_selected_action_type = None
        self.consecutive_action_type_count = 0