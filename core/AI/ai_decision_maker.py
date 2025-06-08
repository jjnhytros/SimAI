# core/AI/ai_decision_maker.py
from typing import Optional, TYPE_CHECKING, List, Dict, Tuple, Any
import random

# Import Enum
from core.enums import (
    NeedType, ActionType, TraitType, LifeStage, FunActivityType,
    SocialInteractionType, ObjectType, RelationshipType, ProblemType
)
# Import Classi Azione
from core.modules.actions import (
    BaseAction, EatAction, DrinkAction, SleepAction, HaveFunAction,
    UseBathroomAction, SocializeAction, EngageIntimacyAction, MoveToAction
)
# Import Sistemi IA
from core.AI.needs_processor import NeedsProcessor
from core.AI.problem_definitions import Problem

# Import Configurazioni e Utility
from core.config import npc_config, time_config, actions_config 
from core import settings 
from core.utils import calculate_distance

if TYPE_CHECKING:
    from core.character import Character
    from ..simulation import Simulation 
    from ..modules.time_manager import TimeManager
    from ..world.location import Location

class AIDecisionMaker:
    """
    Determina l'azione successiva che un NPC dovrebbe intraprendere basandosi
    su un ciclo cognitivo di identificazione del problema, scoperta delle soluzioni
    e valutazione delle opzioni.
    """
    BASE_ACTION_CHECK_INTERVAL_TICKS = 10 
    MAX_CONSECUTIVE_SAME_ACTION = 3

    # Il catalogo che lega i bisogni alle possibili azioni risolutive.
    PROBLEM_SOLVERS_BY_NEED: Dict[NeedType, List[type]] = {
        NeedType.HUNGER: [EatAction],
        NeedType.ENERGY: [SleepAction],
        NeedType.THIRST: [DrinkAction],
        NeedType.BLADDER: [UseBathroomAction],
        NeedType.HYGIENE: [UseBathroomAction],
        NeedType.FUN: [HaveFunAction],
        NeedType.SOCIAL: [SocializeAction],
        NeedType.INTIMACY: [EngageIntimacyAction],
    }

    def __init__(self, npc: 'Character'):
        self.npc: 'Character' = npc
        self.ticks_since_last_base_action_check: int = 0
        self.last_selected_action_type: Optional[ActionType] = None
        self.consecutive_action_type_count: int = 0
        self.needs_processor = NeedsProcessor()

    def _calculate_action_score(self, action_effects: Dict[NeedType, float]) -> float:
        """Calcola un punteggio base per un'azione in base a come soddisfa i bisogni."""
        total_score = 0.0
        if not self.npc.needs: return 0.0

        for need_type, effect_value in action_effects.items():
            if effect_value <= 0: continue
            need_obj = self.npc.needs.get(need_type)
            if not need_obj: continue

            current_need_value = need_obj.get_value()
            desirability = 1.0 - (current_need_value / npc_config.NEED_MAX_VALUE)
            base_weight = npc_config.NEED_WEIGHTS.get(need_type, 0.5)
            critical_modifier = self.needs_processor._get_critical_need_modifier(current_need_value)
            
            trait_modifier = 1.0
            for trait_obj in self.npc.traits.values():
                if hasattr(trait_obj, 'get_need_satisfaction_modifier'):
                    trait_modifier *= trait_obj.get_need_satisfaction_modifier(need_type, effect_value)
            
            need_score = effect_value * desirability * base_weight * critical_modifier * trait_modifier
            total_score += need_score
        return total_score

    def _evaluate_action_candidate(self, action: BaseAction, simulation_context: 'Simulation') -> float:
        """Valuta un'azione candidata calcolando un punteggio complessivo basato su più fattori."""
        time_manager = simulation_context.time_manager
        weather_manager = simulation_context.weather_manager
        
        need_score = self._calculate_action_score(getattr(action, 'effects_on_needs', {}))
        if need_score <= 0: need_score = 1.0

        personality_modifier = 1.0
        if action.action_type_enum is not None:
            for trait_obj in self.npc.traits.values():
                modifier = trait_obj.get_action_choice_priority_modifier(action.action_type_enum, simulation_context)
                personality_modifier *= modifier

        memory_modifier = 1.0
        if self.npc.memory_system and action.action_type_enum:
            query: Dict[str, Any] = {"action_type": action.action_type_enum}
            target_npc = getattr(action, 'target_npc', None)
            activity_type = getattr(action, 'activity_type', None)
            if target_npc: query["target_npc_id"] = target_npc.npc_id
            if activity_type:
                if isinstance(action, SocializeAction): query["interaction_type"] = action.interaction_type
                else: query["activity_type"] = activity_type
            relevant_memories = self.npc.memory_system.get_memories_about(query)
            if relevant_memories:
                total_emotional_impact = sum(m.emotional_impact for m in relevant_memories[:3])
                memory_modifier = max(0.1, 1.0 + total_emotional_impact) 
        
        context_modifier = 1.0
        is_night_time = time_manager.is_night() if time_manager else False
        if getattr(action, 'is_outdoors', False) and weather_manager and weather_manager.is_raining():
            context_modifier *= 0.1
        if getattr(action, 'is_noisy', False) and is_night_time:
            context_modifier *= 0.2
        if action.action_type_enum == ActionType.ACTION_SLEEP:
            context_modifier *= 2.0 if is_night_time else 0.3
        
        final_score = need_score * personality_modifier * memory_modifier * context_modifier
        
        if settings.DEBUG_MODE:
            print(f"      -> Scoring {action.action_type_name}: Base(Need)={need_score:.2f}, "
                  f"PersMod={personality_modifier:.2f}, MemMod={memory_modifier:.2f}, CtxMod={context_modifier:.2f} "
                  f"-> FINALE: {final_score:.2f}")

        return final_score

    def _discover_and_instantiate_solutions(self, problem: Problem, simulation_context: 'Simulation') -> List[BaseAction]:
        """Data un problema, trova e crea istanze di tutte le azioni valide che possono risolverlo."""
        valid_actions: List[BaseAction] = []
        if problem.problem_type != ProblemType.LOW_NEED: return valid_actions

        need_to_address = problem.details.get("need")
        if not isinstance(need_to_address, NeedType): return valid_actions

        possible_action_classes = self.PROBLEM_SOLVERS_BY_NEED.get(need_to_address, [])
        
        for action_class in possible_action_classes:
            try:
                # Logica di istanziazione per azioni complesse che generano molte varianti
                if action_class == HaveFunAction:
                    for activity_type in FunActivityType:
                        activity_config = actions_config.HAVEFUN_ACTIVITY_CONFIGS.get(activity_type, {})
                        params = { "npc": self.npc, "simulation_context": simulation_context, "activity_type": activity_type,
                                   "duration_ticks": int(activity_config.get("duration_hours", actions_config.HAVEFUN_DEFAULT_DURATION_HOURS) * time_config.IXH),
                                "fun_gain": activity_config.get("fun_gain", actions_config.HAVEFUN_DEFAULT_FUN_GAIN),
                                "required_object_types": activity_config.get("required_object_types"),
                                "skill_to_practice": activity_config.get("skill_to_practice"), "skill_xp_gain": activity_config.get("skill_xp_gain", 0.0) }
                        action_instance = HaveFunAction(**params)
                        if action_instance.is_valid(): valid_actions.append(action_instance)
                
                elif action_class == SocializeAction:
                    current_loc = simulation_context.get_location_by_id(self.npc.current_location_id)
                    if current_loc:
                        for target_id in current_loc.npcs_present_ids:
                            if target_id == self.npc.npc_id: continue
                            target_char = simulation_context.get_npc_by_id(target_id)
                            if not target_char: continue
                            for interaction_type in SocialInteractionType:
                                i_config = actions_config.SOCIALIZE_INTERACTION_CONFIGS.get(interaction_type, {})
                                min_score = i_config.get("min_rel_score_req")
                                if min_score is not None:
                                    rel = self.npc.get_relationship_with(target_char.npc_id)
                                    if not rel or rel.score < min_score: continue
                                params = {
                                    "npc": self.npc, "simulation_context": simulation_context, "target_npc": target_char, "interaction_type": interaction_type,
                                    "duration_ticks": i_config.get("duration_ticks", actions_config.SOCIALIZE_DEFAULT_DURATION_TICKS),
                                    "initiator_social_gain": i_config.get("initiator_gain", actions_config.SOCIALIZE_DEFAULT_INITIATOR_GAIN),
                                    "target_social_gain": i_config.get("target_gain", actions_config.SOCIALIZE_DEFAULT_TARGET_GAIN),
                                    "relationship_score_change": i_config.get("rel_change", actions_config.SOCIALIZE_DEFAULT_REL_CHANGE) }
                                action_instance = SocializeAction(**params)
                                if action_instance.is_valid(): valid_actions.append(action_instance)
                
                # Logica per azioni più semplici che generano una sola istanza
                else:
                    action_configs = {}
                    if action_class == SleepAction:
                        base_h = getattr(actions_config, 'SLEEP_ACTION_DEFAULT_HOURS', 7.0)
                        adj_h = base_h
                        if self.npc.life_stage and (self.npc.life_stage.is_child or self.npc.life_stage.is_teenager): adj_h = getattr(actions_config, 'SLEEP_HOURS_CHILD_TEEN', 9.0)
                        elif self.npc.life_stage and self.npc.life_stage.is_elder: adj_h = getattr(actions_config, 'SLEEP_HOURS_ELDERLY', 8.0)
                        action_configs = {
                            "duration_hours": adj_h, "energy_gain_per_hour": getattr(actions_config, 'SLEEP_ACTION_ENERGY_GAIN_PER_HOUR', 15.0),
                            "validation_threshold": getattr(npc_config, 'ENERGY_THRESHOLD_TO_CONSIDER_SLEEP', (npc_config.NEED_LOW_THRESHOLD + 10)),
                            "on_finish_energy_target": npc_config.NEED_MAX_VALUE, "on_finish_needs_adjust": {
                                NeedType.HUNGER: getattr(actions_config, 'NEED_VALUE_ON_WAKE_HUNGER', 70.0), NeedType.THIRST: getattr(actions_config, 'NEED_VALUE_ON_WAKE_THIRST', 75.0),
                                NeedType.BLADDER: getattr(actions_config, 'NEED_VALUE_ON_WAKE_BLADDER', 80.0)}}
                    elif action_class == EatAction:
                        action_configs = {"duration_ticks": int(getattr(actions_config, 'EAT_ACTION_DEFAULT_DURATION_HOURS', 0.5) * time_config.IXH), "hunger_gain": getattr(actions_config, 'EAT_ACTION_DEFAULT_HUNGER_GAIN', 70.0)}
                    elif action_class == DrinkAction:
                         action_configs = {"drink_type_name": "WATER", "duration_ticks": int(getattr(actions_config, 'DRINK_WATER_DURATION_HOURS', 0.2) * time_config.IXH), "thirst_gain": getattr(actions_config, 'DRINK_WATER_THIRST_GAIN', 60.0), "effects_on_other_needs": {NeedType.BLADDER: getattr(actions_config, 'DRINK_WATER_BLADDER_EFFECT', -10.0)}}
                    elif action_class == UseBathroomAction:
                        if need_to_address == NeedType.BLADDER:
                            action_configs = {"for_need": need_to_address, "duration_ticks": getattr(actions_config, 'USEBATHROOM_TOILET_DURATION_TICKS', int(0.15 * time_config.IXH)), "bladder_relief": getattr(actions_config, 'USEBATHROOM_TOILET_BLADDER_RELIEF', 100.0), "hygiene_gain": getattr(actions_config, 'USEBATHROOM_TOILET_HYGIENE_GAIN', 15.0)}
                        elif need_to_address == NeedType.HYGIENE:
                            action_configs = {"for_need": need_to_address, "duration_ticks": getattr(actions_config, 'USEBATHROOM_SHOWER_DURATION_TICKS', int(0.4 * time_config.IXH)), "bladder_relief": 0.0, "hygiene_gain": getattr(actions_config, 'USEBATHROOM_SHOWER_HYGIENE_GAIN', 80.0)}
                    elif action_class == EngageIntimacyAction:
                         target_id = getattr(self.npc, 'pending_intimacy_target_accepted', None)
                         if target_id and (target_char := simulation_context.get_npc_by_id(target_id)):
                            action_configs = {"target_npc": target_char, "duration_ticks": getattr(actions_config, 'INTIMACY_ACTION_DEFAULT_DURATION_TICKS', int(time_config.IXH * 1)), "initiator_intimacy_gain": getattr(actions_config, 'INTIMACY_ACTION_DEFAULT_INITIATOR_GAIN', 60.0), "target_intimacy_gain": getattr(actions_config, 'INTIMACY_ACTION_DEFAULT_TARGET_GAIN', 60.0), "relationship_score_gain": getattr(actions_config, 'INTIMACY_ACTION_DEFAULT_REL_GAIN', 15)}
                    
                    if action_configs:
                        constructor_params = {"npc": self.npc, "simulation_context": simulation_context, **action_configs}
                        action_instance = action_class(**constructor_params)
                        if action_instance.is_valid(): valid_actions.append(action_instance)
            except (TypeError, KeyError) as e:
                if settings.DEBUG_MODE: print(f"  [AI Discover] Errore parametri/chiave per {action_class.__name__}: {e}")
                continue
        
        return valid_actions

    def decide_next_action(self, time_manager: 'TimeManager', simulation_context: 'Simulation') -> Optional[BaseAction]:
        self.ticks_since_last_base_action_check += 1
        if self.ticks_since_last_base_action_check < self.BASE_ACTION_CHECK_INTERVAL_TICKS:
            return None
        self.ticks_since_last_base_action_check = 0

        active_problems: List[Problem] = self.needs_processor.identify_need_problems(self.npc, float(time_manager.total_ticks_sim_run))
        if not active_problems:
            if settings.DEBUG_MODE: print(f"  [AI Decide - {self.npc.name}] Nessun problema attivo.")
            return None
        current_problem = active_problems[0]
        
        potential_solutions = self._discover_and_instantiate_solutions(current_problem, simulation_context)
        if not potential_solutions:
            if settings.DEBUG_MODE: print(f"  [AI Decide - {self.npc.name}] Nessuna soluzione valida trovata per il problema: {current_problem.problem_type.name}")
            return None
        
        best_action_candidate: Optional[BaseAction] = None
        highest_action_score: float = -float('inf')

        if settings.DEBUG_MODE: print(f"    [AI Decide - {self.npc.name}] Valutazione di {len(potential_solutions)} potenziali soluzioni...")

        for action_candidate in potential_solutions:
            score = self._evaluate_action_candidate(action_candidate, simulation_context)
            if score > highest_action_score:
                highest_action_score = score
                best_action_candidate = action_candidate

        if best_action_candidate and hasattr(best_action_candidate, 'target_object') and best_action_candidate.target_object:
            target_obj = best_action_candidate.target_object
            if hasattr(target_obj, 'logical_x') and target_obj.logical_x is not None:
                npc_pos = (self.npc.logical_x, self.npc.logical_y)
                obj_pos = (target_obj.logical_x, target_obj.logical_y)
                if calculate_distance(npc_pos, obj_pos) > getattr(settings, 'NPC_INTERACTION_DISTANCE_THRESHOLD', 1.5):
                    best_action_candidate = MoveToAction(npc=self.npc, simulation_context=simulation_context, destination=obj_pos, follow_up_action=best_action_candidate)
        
        if best_action_candidate:
            if self.last_selected_action_type == best_action_candidate.action_type_enum and not isinstance(best_action_candidate, MoveToAction):
                self.consecutive_action_type_count += 1
                if self.consecutive_action_type_count >= self.MAX_CONSECUTIVE_SAME_ACTION:
                    if settings.DEBUG_MODE: print(f"  [AI Decide - {self.npc.name}] Max ripetizioni per {best_action_candidate.action_type_name}. NPC non fa nulla.")
                    return None 
            else: self.consecutive_action_type_count = 0
            self.last_selected_action_type = best_action_candidate.action_type_enum
        else: 
            self.consecutive_action_type_count = 0
            self.last_selected_action_type = None

        if best_action_candidate and settings.DEBUG_MODE:
            problem_desc = current_problem.problem_type.name
            if current_problem.problem_type == ProblemType.LOW_NEED:
                need_detail_val = current_problem.details.get("need")
                if isinstance(need_detail_val, NeedType): problem_desc += f" ({need_detail_val.name})"
            action_name_log = getattr(best_action_candidate, 'action_type_name', "AzioneSenzaNome")
            print(f"  [AI Decide - {self.npc.name}] Azione Scelta Finale: {action_name_log} (Score: {highest_action_score:.2f}) per Problema: {problem_desc}")
            
        return best_action_candidate

    def reset_decision_state(self):
        self.ticks_since_last_base_action_check = self.BASE_ACTION_CHECK_INTERVAL_TICKS 
        self.last_selected_action_type = None
        self.consecutive_action_type_count = 0