# core/AI/ai_decision_maker.py
from typing import Any, Optional, TYPE_CHECKING, List, Dict, Tuple
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
from core.AI.needs_processor import NeedsProcessor
from core.AI.problem_definitions import Problem, ProblemType

from core.config import npc_config, time_config 
from core.config.actions_config import (
    HAVEFUN_ACTIVITY_CONFIGS, 
    HAVEFUN_DEFAULT_FUN_GAIN,
    HAVEFUN_DEFAULT_DURATION_HOURS
)
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
    NEED_WEIGHTS = npc_config.NEED_WEIGHTS
    CRITICAL_NEED_THRESHOLD_MODIFIER = npc_config.CRITICAL_NEED_THRESHOLD_MODIFIER
    MAX_CONSECUTIVE_SAME_ACTION = 3

    def __init__(self, npc: 'Character'):
        self.npc: 'Character' = npc
        self.ticks_since_last_base_action_check: int = 0
        self.last_selected_action_type: Optional[ActionType] = None
        self.consecutive_action_type_count: int = 0
        self.needs_processor = NeedsProcessor()

    def _get_critical_need_modifier(self, need_value: float) -> float:
        # Questa logica è ora in NeedsProcessor, ma può essere usata qui per lo scoring delle azioni
        # se i pesi/modificatori sono gestiti centralmente in npc_config.
        critical_threshold = npc_config.NEED_CRITICAL_THRESHOLD
        if need_value <= critical_threshold:
            return npc_config.CRITICAL_NEED_THRESHOLD_MODIFIER
        return 1.0

    def _calculate_action_score(self, action_effects: Dict[NeedType, float]) -> float:
        total_score = 0.0
        if not self.npc.needs: return 0.0
        for need_type, effect_value in action_effects.items():
            if effect_value <= 0: continue
            need_obj = self.npc.needs.get(need_type)
            if not need_obj: continue
            current_need_value = need_obj.get_value()
            max_need = npc_config.NEED_MAX_VALUE
            desirability = 1.0 - (current_need_value / max_need)
            base_weight = npc_config.NEED_WEIGHTS.get(need_type, 0.5)
            critical_modifier = self._get_critical_need_modifier(current_need_value)
            trait_modifier = 1.0
            for trait_obj in self.npc.traits.values():
                if hasattr(trait_obj, 'get_need_satisfaction_modifier'):
                    trait_modifier *= trait_obj.get_need_satisfaction_modifier(need_type, effect_value)
            need_score = effect_value * desirability * base_weight * critical_modifier * trait_modifier
            total_score += need_score
        return total_score


    def decide_next_action(self, time_manager: 'TimeManager', simulation_context: 'Simulation') -> Optional[BaseAction]:
        self.ticks_since_last_base_action_check += 1
        if self.ticks_since_last_base_action_check < self.BASE_ACTION_CHECK_INTERVAL_TICKS:
            return None
        self.ticks_since_last_base_action_check = 0

        sim_timestamp_float = float(time_manager.total_ticks) if time_manager else None
        active_problems: List[Problem] = self.needs_processor.identify_need_problems(self.npc, sim_timestamp_float)

        if not active_problems:
            if settings.DEBUG_MODE: print(f"  [AI Decide - {self.npc.name}] Nessun problema attivo.")
            return None

        current_problem = active_problems[0]
        if settings.DEBUG_MODE: # Debug print migliorato
            details_desc = ""
            if current_problem.problem_type == ProblemType.LOW_NEED:
                need_val = current_problem.details.get('need')
                if isinstance(need_val, NeedType):
                    details_desc = f"Need: {need_val.name}, Val: {current_problem.details.get('current_value', 'N/A'):.1f}"
            print(f"  [AI Decide - {self.npc.name}] Problema: {current_problem.problem_type.name} (Urg: {current_problem.urgency:.2f}), Dettagli: {details_desc}")
        
        best_action_candidate: Optional[BaseAction] = None
        highest_action_score: float = -1.0
        
        action_class_to_try: Optional[type] = None
        action_configs: Dict[str, Any] = {}

        if current_problem.problem_type == ProblemType.LOW_NEED:
            need_to_address = current_problem.details.get("need")
            if not isinstance(need_to_address, NeedType):
                if settings.DEBUG_MODE: print(f"  [AI Decide ERROR - {self.npc.name}] Dettaglio 'need' mancante o non valido.")
                return None

            potential_actions_map: Dict[NeedType, type] = {
                NeedType.HUNGER: EatAction, NeedType.ENERGY: SleepAction, NeedType.THIRST: DrinkAction,
                NeedType.BLADDER: UseBathroomAction, NeedType.HYGIENE: UseBathroomAction,
                NeedType.FUN: HaveFunAction, NeedType.SOCIAL: SocializeAction,
            }
            action_class_to_try = potential_actions_map.get(need_to_address)

            if action_class_to_try == SleepAction:
                base_h = getattr(settings, 'SLEEP_ACTION_DEFAULT_HOURS', 7.0)
                adj_h = base_h # ... (logica aggiustamento età) ...
                action_configs = {
                    "duration_hours": adj_h,
                    "energy_gain_per_hour": getattr(settings, 'SLEEP_ACTION_ENERGY_GAIN_PER_HOUR', 15.0),
                    "validation_threshold": getattr(settings, 'ENERGY_THRESHOLD_TO_CONSIDER_SLEEP', (settings.NEED_LOW_THRESHOLD + 10)),
                    "on_finish_energy_target": getattr(settings, 'NEED_MAX_VALUE', 100.0),
                    "on_finish_needs_adjust": {
                        NeedType.HUNGER: getattr(settings, 'NEED_VALUE_ON_WAKE_HUNGER', 70.0),
                        NeedType.THIRST: getattr(settings, 'NEED_VALUE_ON_WAKE_THIRST', 75.0),
                        NeedType.BLADDER: getattr(settings, 'NEED_VALUE_ON_WAKE_BLADDER', 80.0)
                    }
                }
            elif action_class_to_try == EatAction:
                # Recupera le configurazioni per EatAction
                config_duration_ticks = getattr(settings, 'EAT_ACTION_DEFAULT_DURATION_TICKS', 
                                                int(getattr(settings, 'EAT_ACTION_DEFAULT_DURATION_HOURS', 0.5) * time_config.IXH))
                config_hunger_gain = getattr(settings, 'EAT_ACTION_DEFAULT_HUNGER_GAIN', 70.0)
                # Potresti aggiungere altre config specifiche se EatAction ne avesse bisogno
                
                action_specific_configs = {
                    "duration_ticks": config_duration_ticks,
                    "hunger_gain": config_hunger_gain
                }
                # L'istanziamento generale che avevamo discusso funzionerà bene:
                # constructor_params = {"npc": self.npc, "simulation_context": simulation_context, **action_specific_configs}
                # action_candidate = action_class_to_try(**constructor_params)
                # Oppure, per chiarezza esplicita per questa azione:
                action_candidate = EatAction(
                    npc=self.npc,
                    simulation_context=simulation_context,
                    duration_ticks=action_specific_configs["duration_ticks"],
                    hunger_gain=action_specific_configs["hunger_gain"]
                )
            elif action_class_to_try == DrinkAction:
                chosen_drink_type_name = "WATER" # Esempio, da rendere dinamico se necessario
                default_duration_hours = getattr(settings, 'DRINK_DEFAULT_DURATION_HOURS', 0.2)
                default_thirst_gain = getattr(settings, 'DRINK_DEFAULT_THIRST_GAIN', 50.0)
                default_other_effects = {NeedType.BLADDER: getattr(settings, 'DRINK_DEFAULT_BLADDER_EFFECT', -10.0)}
                
                config_duration_hours = getattr(settings, f"DRINK_{chosen_drink_type_name.upper()}_DURATION_HOURS", default_duration_hours)
                config_thirst_gain = getattr(settings, f"DRINK_{chosen_drink_type_name.upper()}_THIRST_GAIN", default_thirst_gain)
                other_effects = default_other_effects.copy()
                if chosen_drink_type_name == "JUICE":
                    other_effects[NeedType.FUN] = getattr(settings, "DRINK_JUICE_FUN_GAIN", 5.0)
                
                action_configs = {
                    "drink_type_name": chosen_drink_type_name,
                     "duration_ticks": int(config_duration_hours * time_config.IXH),
                    "thirst_gain": config_thirst_gain,
                    "effects_on_other_needs": other_effects
                }
            elif action_class_to_try == UseBathroomAction:
                # need_to_address è già BLADDER o HYGIENE
                
                if need_to_address == NeedType.BLADDER:
                    # Config per "andare in bagno" (WC)
                    config_duration_ticks = getattr(settings, 'USEBATHROOM_TOILET_DURATION_TICKS', 
                                                    int(0.15 * time_config.IXH)) # Esempio: default ~9 min
                    config_bladder_relief = getattr(settings, 'USEBATHROOM_TOILET_BLADDER_RELIEF', 100.0)
                    config_hygiene_gain = getattr(settings, 'USEBATHROOM_TOILET_HYGIENE_GAIN', 10.0) # Piccolo boost
                elif need_to_address == NeedType.HYGIENE:
                    # Config per "farsi una doccia/bagno"
                    config_duration_ticks = getattr(settings, 'USEBATHROOM_SHOWER_DURATION_TICKS',
                                                    int(0.4 * time_config.IXH)) # Esempio: doccia più lunga
                    config_bladder_relief = 0.0 # Nessun effetto primario sulla vescica
                    config_hygiene_gain = getattr(settings, 'USEBATHROOM_SHOWER_HYGIENE_GAIN', 75.0)
                else: # Fallback o errore se need_to_address non è né BLADDER né HYGIENE (non dovrebbe succedere)
                    if settings.DEBUG_MODE:
                        print(f"  [AI Decide WARN - {self.npc.name}] UseBathroomAction chiamata per bisogno non supportato: {need_to_address.name}")
                    action_class_to_try = None # Impedisce la creazione dell'azione
                    config_duration_ticks, config_bladder_relief, config_hygiene_gain = 0,0,0 # Valori dummy

                if action_class_to_try: # Prosegui solo se la classe azione è ancora valida
                    action_configs = {
                        "for_need_type": need_to_address,
                        "duration_ticks": config_duration_ticks,
                        "bladder_relief_amount": config_bladder_relief,
                        "hygiene_gain_amount": config_hygiene_gain
                        # target_object è opzionale, UseBathroomAction.is_valid() lo cercherà se non fornito
                    }
            elif action_class_to_try == HaveFunAction:
                available_activities = list(FunActivityType) if FunActivityType else []
                # TODO: La scelta dovrebbe essere influenzata da tratti e interessi dell'NPC, non puramente casuale.
                chosen_activity = random.choice(available_activities) if available_activities else None
                
                if chosen_activity:
                    # Recupera la configurazione specifica per l'attività scelta
                    activity_config = HAVEFUN_ACTIVITY_CONFIGS.get(chosen_activity, {})
                    
                    # Usa i valori specifici, con un fallback a quelli di default
                    config_fun_gain = activity_config.get("fun_gain", HAVEFUN_DEFAULT_FUN_GAIN)
                    config_duration_hours = activity_config.get("duration_hours", HAVEFUN_DEFAULT_DURATION_HOURS)
                    
                    action_configs = {
                        "activity_type": chosen_activity,
                        "duration_ticks": int(config_duration_hours * time_config.IXH),
                        "fun_gain": config_fun_gain,
                        # Passa anche gli altri parametri se presenti nella configurazione
                        "required_object_types": activity_config.get("required_object_types"),
                        "skill_to_practice": activity_config.get("skill_to_practice"),
                        "skill_xp_gain": activity_config.get("skill_xp_gain", 0.0)
                    }
                else:
                    action_class_to_try = None
                    if settings.DEBUG_MODE: print(f"  [AI Decide WARN - {self.npc.name}] Nessuna FunActivityType disponibile.")
            
            elif action_class_to_try == SocializeAction:
                target_char: Optional['Character'] = None
                if simulation_context and self.npc.current_location_id:
                    loc = simulation_context.get_location_by_id(self.npc.current_location_id)
                    if loc:
                        ids = [oid for oid in loc.npcs_present_ids if oid != self.npc.npc_id]
                        if ids: target_char = simulation_context.get_npc_by_id(random.choice(ids))
                
                if target_char:
                    sel_interaction_type = SocialInteractionType.CHAT_CASUAL # Placeholder
                    if hasattr(simulation_context, 'social_manager') and \
                    hasattr(simulation_context.social_manager, '_select_interaction_type'):
                        sel_interaction_type = simulation_context.social_manager._select_interaction_type(self.npc, target_char)
                    
                    action_configs = {
                        "target_npc": target_char,
                        "interaction_type": sel_interaction_type,
                        "duration_ticks_param": getattr(settings, f"SOCIALIZE_{sel_interaction_type.name}_DURATION_TICKS", 30),
                        "initiator_social_gain_param": getattr(settings, f"SOCIALIZE_{sel_interaction_type.name}_INITIATOR_GAIN", 20.0),
                        "target_social_gain_param": getattr(settings, f"SOCIALIZE_{sel_interaction_type.name}_TARGET_GAIN", 15.0),
                        "relationship_score_change_param": getattr(settings, f"SOCIALIZE_{sel_interaction_type.name}_REL_CHANGE", 2)
                        # "new_relationship_type_on_success": getattr(settings, f"SOCIALIZE_{sel_interaction_type.name}_NEW_REL_TYPE", None) 
                    }
                else: action_class_to_try = None
        
        # ... (Blocco elif per altri ProblemType futuri) ...

        if action_class_to_try:
            try:
                constructor_params = {"npc": self.npc, "simulation_context": simulation_context, **action_configs}
                action_candidate = action_class_to_try(**constructor_params)

                if action_candidate and action_candidate.is_valid():
                    action_effects = getattr(action_candidate, 'effects_on_needs', {}) 
                    score = self._calculate_action_score(action_effects)
                    if self.last_selected_action_type == action_candidate.action_type_enum:
                        score *= (1.0 - (self.consecutive_action_type_count * 0.25))
                    if action_candidate.action_type_enum is not None:
                        for trait_obj in self.npc.traits.values():
                            modifier = trait_obj.get_action_choice_priority_modifier(action_candidate.action_type_enum, simulation_context)
                            score *= modifier
                    if score > highest_action_score:
                        highest_action_score = score
                        best_action_candidate = action_candidate
            except Exception as e:
                if settings.DEBUG_MODE:
                    print(f"  [AI Decide ERROR - {self.npc.name}] Eccezione: {e} creando {action_class_to_try.__name__ if action_class_to_try else 'Azione sconosciuta'}")

        if best_action_candidate:
            # ... (logica anti-ripetizione e log finale) ...
            if self.last_selected_action_type == best_action_candidate.action_type_enum:
                self.consecutive_action_type_count += 1
                if self.consecutive_action_type_count >= self.MAX_CONSECUTIVE_SAME_ACTION:
                    if settings.DEBUG_MODE: print(f"  [AI Decide - {self.npc.name}] Max ripetizioni per {best_action_candidate.action_type_name}. Null action.")
                    return None 
            else: self.consecutive_action_type_count = 0
            self.last_selected_action_type = best_action_candidate.action_type_enum
        else: 
            self.consecutive_action_type_count = 0
            self.last_selected_action_type = None

        if best_action_candidate and settings.DEBUG_MODE:
            problem_desc = current_problem.problem_type.name # Inizializza problem_desc
            if current_problem.problem_type == ProblemType.LOW_NEED:
                need_detail_value = current_problem.details.get("need")
                # Controlla prima se è None, poi se è del tipo corretto
                if need_detail_value is not None and isinstance(need_detail_value, NeedType):
                    problem_desc += f" ({need_detail_value.name})"
                elif settings.DEBUG_MODE: # Log opzionale se il dettaglio del bisogno non è come atteso
                    problem_desc += " (Dettaglio bisogno mancante o non valido)"
            
            # Assicurati che best_action_candidate.action_type_name esista o gestisci il caso None
            action_name_log = best_action_candidate.action_type_name if hasattr(best_action_candidate, 'action_type_name') else "AzioneSenzaNome"
            score_log = highest_action_score if highest_action_score is not None else -1.0 # Assicurati che highest_action_score sia inizializzato
            print(f"  [AI Decide - {self.npc.name}] Azione Scelta: {action_name_log} (Score: {score_log:.2f}) per Problema: {problem_desc}")
        
        elif not best_action_candidate and settings.DEBUG_MODE and current_problem:
            problem_desc_else = current_problem.problem_type.name # Inizializza problem_desc_else
            if current_problem.problem_type == ProblemType.LOW_NEED:
                need_detail_value_else = current_problem.details.get("need")
                # Controlla prima se è None, poi se è del tipo corretto
                if need_detail_value_else is not None and isinstance(need_detail_value_else, NeedType):
                    problem_desc_else += f" ({need_detail_value_else.name})"
                elif settings.DEBUG_MODE: # Log opzionale
                    problem_desc_else += " (Dettaglio bisogno mancante o non valido)"
            
            print(f"  [AI Decide - {self.npc.name}] Nessuna azione valida trovata per il problema {problem_desc_else}.")

        return best_action_candidate

    def reset_decision_state(self):
        self.ticks_since_last_base_action_check = self.BASE_ACTION_CHECK_INTERVAL_TICKS 
        self.last_selected_action_type = None
        self.consecutive_action_type_count = 0