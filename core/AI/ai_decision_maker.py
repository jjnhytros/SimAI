# core/AI/ai_decision_maker.py
from typing import Optional, TYPE_CHECKING, List, Dict, Tuple, Any
import random

# Import Enum
from core.enums import (
    NeedType, ActionType, TraitType, LifeStage, FunActivityType,
    SocialInteractionType, ObjectType, RelationshipType # Aggiunti per completezza
)
# Import Classi Azione
from core.modules.actions.action_base import BaseAction
from core.modules.actions.energy_actions import SleepAction
from core.modules.actions.hunger_actions import EatAction
from core.modules.actions.thirst_actions import DrinkAction
from core.modules.actions.bathroom_actions import UseBathroomAction
from core.modules.actions.fun_actions import HaveFunAction
from core.modules.actions.social_actions import SocializeAction
from core.modules.actions.movement_actions import MoveToAction # Importa la nuova azione di movimento
from core.modules.actions.intimacy_actions import EngageIntimacyAction
# Import Sistemi IA
from core.AI.needs_processor import NeedsProcessor
from core.AI.problem_definitions import Problem, ProblemType

# Import Configurazioni e Utility
from core.config import npc_config, time_config, actions_config # Assumendo esista actions_config
from core.settings import DEBUG_MODE
from core.utils.math_utils import calculate_distance # Importa la funzione per la distanza

if TYPE_CHECKING:
    from core.character import Character
    from ..simulation import Simulation 
    from ..modules.time_manager import TimeManager

class AIDecisionMaker:
    """
    Determina l'azione successiva che un NPC dovrebbe intraprendere basandosi
    sui problemi identificati (es. bisogni bassi).
    """
    BASE_ACTION_CHECK_INTERVAL_TICKS = 10 
    MAX_CONSECUTIVE_SAME_ACTION = 3

    def __init__(self, npc: 'Character'):
        self.npc: 'Character' = npc
        self.ticks_since_last_base_action_check: int = 0
        self.last_selected_action_type: Optional[ActionType] = None
        self.consecutive_action_type_count: int = 0
        self.needs_processor = NeedsProcessor()

    def _calculate_action_score(self, action_effects: Dict[NeedType, float]) -> float:
        """
        Calcola un punteggio per un'azione potenziale basato su come soddisfa i bisogni
        attuali dell'NPC, considerando i pesi dei bisogni e i tratti.
        """
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
            critical_modifier = self.needs_processor._get_critical_need_modifier(current_need_value) # Usa il metodo da NeedsProcessor
            
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

        # --- FASE 1: Identificazione del Problema tramite NeedsProcessor ---
        sim_timestamp_float = float(time_manager.total_ticks) if time_manager else None
        active_problems: List[Problem] = self.needs_processor.identify_need_problems(self.npc, sim_timestamp_float)

        if not active_problems:
            if DEBUG_MODE: print(f"  [AI Decide - {self.npc.name}] Nessun problema attivo identificato.")
            # TODO: Logica per azioni idle, hobby, aspirazioni.
            return None

        current_problem = active_problems[0]
        if DEBUG_MODE:
            details_desc = ""
            if current_problem.problem_type == ProblemType.LOW_NEED:
                need_val = current_problem.details.get('need')
                if isinstance(need_val, NeedType): details_desc = f"Need: {need_val.name}, Val: {current_problem.details.get('current_value', 'N/A'):.1f}"
            print(f"  [AI Decide - {self.npc.name}] Problema: {current_problem.problem_type.name} (Urg: {current_problem.urgency:.2f}), Dettagli: {details_desc}")
        
        best_action_candidate: Optional[BaseAction] = None
        highest_action_score: float = -1.0
        
        action_class_to_try: Optional[type] = None
        action_configs: Dict[str, Any] = {}

        if current_problem.problem_type == ProblemType.LOW_NEED:
            need_to_address = current_problem.details.get("need")
            if not isinstance(need_to_address, NeedType): return None

            potential_actions_map: Dict[NeedType, type] = {
                NeedType.HUNGER: EatAction, NeedType.ENERGY: SleepAction, NeedType.THIRST: DrinkAction,
                NeedType.BLADDER: UseBathroomAction, NeedType.HYGIENE: UseBathroomAction,
                NeedType.FUN: HaveFunAction, NeedType.SOCIAL: SocializeAction,
                NeedType.INTIMACY: EngageIntimacyAction,
            }
            action_class_to_try = potential_actions_map.get(need_to_address)
            
            if action_class_to_try:
                # Recupera le configurazioni specifiche per il tipo di azione
                # Questo blocco ora popola `action_configs`
                if action_class_to_try == SleepAction:
                    # 1. Leggi il valore di default da actions_config
                    base_sleep_hours = getattr(actions_config, 'SLEEP_ACTION_DEFAULT_HOURS', 7.0)
                    adjusted_sleep_hours = base_sleep_hours # Inizia con il default

                    # 2. Applica le eccezioni basate sullo stadio di vita, usando i metodi helper
                    if self.npc.life_stage: # Controlla sempre che life_stage non sia None
                        if self.npc.life_stage.is_child or self.npc.life_stage.is_teenager:
                            # Leggi da actions_config per bambini/adolescenti
                            adjusted_sleep_hours = getattr(actions_config, 'SLEEP_HOURS_CHILD_TEEN', 9.0)
                        
                        elif self.npc.life_stage.is_elder:
                            # Leggi da actions_config per anziani
                            adjusted_sleep_hours = getattr(actions_config, 'SLEEP_HOURS_ELDERLY', 8.0)

                    # 3. Popola il dizionario di configurazione finale per l'azione
                    action_configs = {
                        "duration_hours": adjusted_sleep_hours,
                        "energy_gain_per_hour": getattr(actions_config, 'SLEEP_ACTION_ENERGY_GAIN_PER_HOUR', 15.0),
                        "validation_threshold": getattr(npc_config, 'ENERGY_THRESHOLD_TO_CONSIDER_SLEEP', (npc_config.NEED_LOW_THRESHOLD + 10)),
                        "on_finish_energy_target": npc_config.NEED_MAX_VALUE,
                        "on_finish_needs_adjust": {
                            NeedType.HUNGER: getattr(actions_config, 'NEED_VALUE_ON_WAKE_HUNGER', 70.0),
                            NeedType.THIRST: getattr(actions_config, 'NEED_VALUE_ON_WAKE_THIRST', 75.0),
                            NeedType.BLADDER: getattr(actions_config, 'NEED_VALUE_ON_WAKE_BLADDER', 80.0)
                        }
                    }
                elif action_class_to_try == EatAction:
                    action_configs = {
                        "duration_ticks": int(getattr(action_configs, 'EAT_ACTION_DEFAULT_DURATION_HOURS', 0.5) * time_config.IXH),
                        "hunger_gain": getattr(action_configs, 'EAT_ACTION_DEFAULT_HUNGER_GAIN', 70.0)}
                elif action_class_to_try == DrinkAction:
                    action_configs = { "drink_type": "WATER" } # Mantiene la tua logica attuale
                elif action_class_to_try == UseBathroomAction:
                    action_configs = { "for_need": need_to_address } # Mantiene la tua logica attuale
                elif action_class_to_try == HaveFunAction:
                    available_activities = list(FunActivityType) if FunActivityType else []
                    # TODO: La scelta dovrebbe essere influenzata da tratti e interessi dell'NPC, non puramente casuale.
                    chosen_activity = random.choice(available_activities) if available_activities else None
                    
                    if chosen_activity:
                        # Recupera la configurazione specifica per l'attività scelta, con fallback ai default
                        activity_config = actions_config.HAVEFUN_ACTIVITY_CONFIGS.get(chosen_activity, {})
                        
                        config_duration_hours = activity_config.get("duration_hours", actions_config.HAVEFUN_DEFAULT_DURATION_HOURS)
                        
                        action_configs = {
                            "activity_type": chosen_activity,
                            "duration_ticks": int(config_duration_hours * time_config.IXH),
                            "fun_gain": activity_config.get("fun_gain", actions_config.HAVEFUN_DEFAULT_FUN_GAIN),
                            "required_object_types": activity_config.get("required_object_types"),
                            "skill_to_practice": activity_config.get("skill_to_practice"),
                            "skill_xp_gain": activity_config.get("skill_xp_gain", 0.0)
                        }
                    else:
                        action_class_to_try = None # Nessuna attività trovata, non si può creare l'azione
                        if DEBUG_MODE: print(f"  [AI Decide WARN - {self.npc.name}] Nessuna FunActivityType disponibile.")
                elif action_class_to_try == SocializeAction:
                    target_char: Optional['Character'] = simulation_context.find_available_social_target(self.npc)
                    
                    if target_char:
                        # Logica per scegliere l'interaction_type (es. dal SocialManager)
                        interaction_type_to_use = SocialInteractionType.CHAT_CASUAL # Placeholder
                        if hasattr(simulation_context, 'social_manager'):
                            interaction_type_to_use = simulation_context.social_manager._select_interaction_type(self.npc, target_char)

                        # Recupera la configurazione per l'interazione scelta
                        interaction_config = actions_config.SOCIALIZE_INTERACTION_CONFIGS.get(interaction_type_to_use, {})

                        # Controlla se i prerequisiti (es. punteggio relazione) sono soddisfatti
                        min_score_req = interaction_config.get("min_rel_score_req")
                        if min_score_req is not None:
                            relationship = self.npc.get_relationship_with(target_char.npc_id)
                            if not relationship or relationship.score < min_score_req:
                                if DEBUG_MODE:
                                    print(f"    [AI Decide] {self.npc.name} non può fare '{interaction_type_to_use.name}' con {target_char.name}, relazione non sufficiente.")
                                action_class_to_try = None # Annulla l'azione
                                
                        if action_class_to_try: # Prosegui solo se i prerequisiti sono soddisfatti
                            action_configs = {
                                "target_npc": target_char,
                                "interaction_type": interaction_type_to_use,
                                # Passa tutti i parametri dalla configurazione, con fallback ai default globali
                                "duration_ticks": interaction_config.get("duration_ticks", actions_config.SOCIALIZE_DEFAULT_DURATION_TICKS),
                                "initiator_social_gain": interaction_config.get("initiator_gain", actions_config.SOCIALIZE_DEFAULT_INITIATOR_GAIN),
                                "target_social_gain": interaction_config.get("target_gain", actions_config.SOCIALIZE_DEFAULT_TARGET_GAIN),
                                "relationship_score_change": interaction_config.get("rel_change", actions_config.SOCIALIZE_DEFAULT_REL_CHANGE),
                                "new_relationship_type_on_success": interaction_config.get("new_rel_type_on_success"),
                                "effects_on_target": interaction_config.get("effects_on_target")
                            }
                    else:
                        action_class_to_try = None
                        if DEBUG_MODE: print(f"    [AI Decide WARN - {self.npc.name}] Nessun target per SocializeAction.")

        if action_class_to_try:
            try:
                # Istanziamento unificato (ancora in evoluzione man mano che rifattorizzi gli __init__)
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
            except TypeError as e: # Catch specifico per errori di parametri
                if DEBUG_MODE:
                    print(f"  [AI Decide TypeError - {self.npc.name}] Errore parametri creando {action_class_to_try.__name__}: {e}")
            except Exception as e:
                if DEBUG_MODE:
                    print(f"  [AI Decide ERROR - {self.npc.name}] Eccezione: {e} creando {action_class_to_try.__name__}")

        if best_action_candidate and hasattr(best_action_candidate, 'target_object') and best_action_candidate.target_object:
            target_obj = best_action_candidate.target_object
            if hasattr(target_obj, 'logical_x') and target_obj.logical_x is not None and \
            hasattr(target_obj, 'logical_y') and target_obj.logical_y is not None:
                
                npc_pos = (self.npc.logical_x, self.npc.logical_y)
                obj_pos = (target_obj.logical_x, target_obj.logical_y)
                distance = calculate_distance(npc_pos, obj_pos)
                interaction_distance_threshold = getattr(action_configs, 'NPC_INTERACTION_DISTANCE_THRESHOLD', 1.5)
                
                if distance > interaction_distance_threshold:
                    if DEBUG_MODE:
                        print(f"  [AI Decide - {self.npc.name}] L'oggetto '{target_obj.name}' è troppo lontano ({distance:.1f}u). Accodo MoveToAction.")
                    move_action = MoveToAction(
                        npc=self.npc,
                        simulation_context=simulation_context,
                        destination=obj_pos,
                        follow_up_action=best_action_candidate
                    )
                    best_action_candidate = move_action
                    # Resetta il contatore perché l'azione è cambiata
                    self.consecutive_action_type_count = 0 

        if best_action_candidate:
            if self.last_selected_action_type == best_action_candidate.action_type_enum:
                self.consecutive_action_type_count += 1
                if self.consecutive_action_type_count >= self.MAX_CONSECUTIVE_SAME_ACTION:
                    if DEBUG_MODE: print(f"  [AI Decide - {self.npc.name}] Max ripetizioni per {best_action_candidate.action_type_name}. NPC non fa nulla.")
                    return None 
            else: self.consecutive_action_type_count = 0
            self.last_selected_action_type = best_action_candidate.action_type_enum
        else: 
            self.consecutive_action_type_count = 0
            self.last_selected_action_type = None

        if best_action_candidate and DEBUG_MODE:
            problem_desc = current_problem.problem_type.name
            if current_problem.problem_type == ProblemType.LOW_NEED:
                need_detail_val = current_problem.details.get("need")
                if isinstance(need_detail_val, NeedType): # isinstance gestisce già il caso None
                    problem_desc += f" ({need_detail_val.name})"
            print(f"  [AI Decide - {self.npc.name}] Azione Scelta Finale: {best_action_candidate.action_type_name} (Score: {highest_action_score:.2f}) per Problema: {problem_desc}")
        elif not best_action_candidate and DEBUG_MODE and current_problem:
            problem_desc_else = current_problem.problem_type.name # Rinominato per chiarezza
            if current_problem.problem_type == ProblemType.LOW_NEED:
                need_detail_val_else = current_problem.details.get("need")
                if isinstance(need_detail_val_else, NeedType):
                    problem_desc_else += f" ({need_detail_val_else.name})"
            print(f"  [AI Decide - {self.npc.name}] Nessuna azione valida trovata per il problema {problem_desc_else}.")
            
        return best_action_candidate

    def reset_decision_state(self):
        self.ticks_since_last_base_action_check = self.BASE_ACTION_CHECK_INTERVAL_TICKS 
        self.last_selected_action_type = None
        self.consecutive_action_type_count = 0