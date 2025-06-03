# core/AI/ai_decision_maker.py
from typing import Optional, TYPE_CHECKING, List, Dict, Tuple
import random

from core.enums import (
    NeedType, ActionType, TraitType, LifeStage, FunActivityType
)
# from core.modules.actions import ( # Esempio di import azioni specifiche
#     EatAction, SleepAction, UseBathroomAction, HaveFunAction, 
#     SocializeAction, DrinkAction
# )
# Importa le classi azione specifiche che ti servono
from core.modules.actions.action_base import BaseAction
from core.modules.actions.energy_actions import SleepAction
from core.modules.actions.hunger_actions import EatAction
from core.modules.actions.thirst_actions import DrinkAction
from core.modules.actions.bathroom_actions import UseBathroomAction
from core.modules.actions.fun_actions import HaveFunAction
from core.modules.actions.social_actions import SocializeAction


from core.config import npc_config, time_config # Aggiunto time_config
from core import settings # Per DEBUG_MODE

if TYPE_CHECKING:
    from core.character import Character
    from ..simulation import Simulation # Corretto per importare Simulation dal package genitore
    from ..modules.time_manager import TimeManager # Corretto per importare TimeManager
    from . import AICoordinator # Rimosso AICoordinator da qui se causa ciclo
    # from .ai_coordinator import AICoordinator # Alternativa


class AIDecisionMaker:
    """
    Determina l'azione successiva che un NPC dovrebbe intraprendere.
    """
    BASE_ACTION_CHECK_INTERVAL_TICKS = 10 # Ogni quanti tick l'IA rivaluta le azioni base
    
    # Pesi per i bisogni (più alto = più importante quando si sceglie un'azione)
    NEED_WEIGHTS = {
        NeedType.HUNGER: 1.5,
        NeedType.THIRST: 1.6, # Leggermente più prioritario della fame
        NeedType.ENERGY: 1.4,
        NeedType.BLADDER: 1.3,
        NeedType.HYGIENE: 1.0,
        NeedType.FUN: 0.8,
        NeedType.SOCIAL: 0.7,
        NeedType.INTIMACY: 0.6,
        # Aggiungere pesi per altri bisogni (COMFORT, SAFETY, etc.) quando implementati
    }
    # Soglia sotto la quale un bisogno diventa "critico" e la sua soddisfazione urgente
    CRITICAL_NEED_THRESHOLD_MODIFIER = 1.5 # Moltiplicatore per il peso se il bisogno è critico

    def __init__(self, npc: 'Character'): # Rimosso ai_coordinator
        self.npc: 'Character' = npc
        # Se AIDecisionMaker ha bisogno del contesto della simulazione (es. per TimeManager),
        # può accedere tramite self.npc.simulation_context (se l'NPC ce l'ha)
        # Esempio: self.simulation_context = npc.simulation_context
        self.ticks_since_last_base_action_check: int = 0
        self.last_selected_action_type: Optional[ActionType] = None
        self.consecutive_action_type_count: int = 0
        self.MAX_CONSECUTIVE_SAME_ACTION = 3

    def _get_critical_need_modifier(self, need_value: float) -> float:
        """
        Restituisce un moltiplicatore se il bisogno è sotto la soglia critica.
        """
        critical_threshold = npc_config.NEED_CRITICAL_THRESHOLD \
            if hasattr(npc_config, 'NEED_CRITICAL_THRESHOLD') else 10.0
        if need_value <= critical_threshold:
            return self.CRITICAL_NEED_THRESHOLD_MODIFIER
        return 1.0

    def _calculate_action_score(self, action_effects: Dict[NeedType, float]) -> float:
        """
        Calcola un punteggio per un'azione potenziale basato su come soddisfa i bisogni
        attuali dell'NPC, considerando i pesi dei bisogni e i tratti.
        """
        total_score = 0.0
        if not self.npc.needs:
            return 0.0

        for need_type, effect_value in action_effects.items():
            if effect_value <= 0:  # Consideriamo solo effetti positivi di soddisfacimento
                continue

            need_obj = self.npc.needs.get(need_type)
            if not need_obj:
                continue

            current_need_value = need_obj.get_value()
            
            # Quanto è "desiderabile" soddisfare questo bisogno? (0-1, più basso è più desiderabile)
            # Se il bisogno è pieno (100), il desiderio di soddisfarlo è 0.
            # Se il bisogno è vuoto (0), il desiderio di soddisfarlo è 1.
            max_need = npc_config.NEED_MAX_VALUE if hasattr(npc_config, 'NEED_MAX_VALUE') else 100.0
            desirability = 1.0 - (current_need_value / max_need)
            
            base_weight = self.NEED_WEIGHTS.get(need_type, 0.5) # Peso base per il bisogno
            critical_modifier = self._get_critical_need_modifier(current_need_value)
            
            # Modificatori dai tratti
            trait_modifier = 1.0
            for trait in self.npc.traits.values(): # Itera sui BaseTrait objects
                if hasattr(trait, 'get_need_satisfaction_modifier'):
                    trait_modifier *= trait.get_need_satisfaction_modifier(need_type, effect_value)

            # Punteggio per questo singolo bisogno = effetto_azione * desiderabilità * peso_base * mod_critico * mod_tratto
            need_score = effect_value * desirability * base_weight * critical_modifier * trait_modifier
            total_score += need_score
            
            # if settings.DEBUG_MODE and total_score > 0 :
            #     print(f"    [AI Score - {self.npc.name}] Bisogno: {need_type.name}, Effetto: {effect_value:.1f}, Val Cor: {current_need_value:.1f}, Des: {desirability:.2f}, Peso: {base_weight}, CritMod: {critical_modifier}, TraitMod: {trait_modifier:.2f} -> Score Parz: {need_score:.2f}")

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

        # 1. Identificazione del "Problema" (Bisogno più Urgente)
        for need_type_enum, need_obj in self.npc.needs.items():
            current_value = need_obj.get_value()
            max_val = npc_config.NEED_MAX_VALUE if hasattr(npc_config, 'NEED_MAX_VALUE') else 100.0
            
            # --- Calcolo di 'urgency' all'interno del loop ---
            urgency = (1.0 - (current_value / max_val)) * \
                      self.NEED_WEIGHTS.get(need_type_enum, 0.5) * \
                      self._get_critical_need_modifier(current_value)
            
            if urgency > highest_urgency_score:
                highest_urgency_score = urgency
                most_pressing_need_type = need_type_enum
        # --- Fine calcolo 'urgency' ---

        if settings.DEBUG_MODE and most_pressing_need_type:
            print(f"  [AI Decide - {self.npc.name}] Bisogno più pressante: {most_pressing_need_type.name} (Urgenza: {highest_urgency_score:.2f})")
        elif settings.DEBUG_MODE:
            print(f"  [AI Decide - {self.npc.name}] Nessun bisogno pressante identificato.")
            # Potremmo voler che l'IA faccia qualcos'altro se nessun bisogno è pressante.
            # Per ora, se nessun bisogno è urgente, non sceglie un'azione basata sui bisogni.

        best_action_candidate: Optional[BaseAction] = None
        highest_action_score: float = -1.0 # Inizializza a un valore basso ma non -inf per permettere azioni con score 0

        potential_actions_map: Dict[NeedType, type] = {
            NeedType.HUNGER: EatAction,
            NeedType.ENERGY: SleepAction,
            NeedType.THIRST: DrinkAction,
            NeedType.BLADDER: UseBathroomAction, # Assicurati che il nome classe sia corretto
            NeedType.HYGIENE: UseBathroomAction, # Assicurati che il nome classe sia corretto
            NeedType.FUN: HaveFunAction,
            NeedType.SOCIAL: SocializeAction,
        }

        # Questo blocco viene eseguito SOLO se un most_pressing_need_type è stato identificato 
        # E esiste un'azione mappata per quel bisogno.
        if most_pressing_need_type is not None and most_pressing_need_type in potential_actions_map:
            action_class_to_try = potential_actions_map[most_pressing_need_type]
            action_candidate: Optional[BaseAction] = None

            try:
                if action_class_to_try == SleepAction:
                    sleep_hours = 7.0 
                    # Assicurati che i membri di LifeStage siano corretti (EARLY_CHILDHOOD, etc.)
                    if self.npc.life_stage in [LifeStage.EARLY_CHILDHOOD, LifeStage.MIDDLE_CHILDHOOD, LifeStage.ADOLESCENCE]:
                        sleep_hours = 9.0
                    elif self.npc.life_stage == LifeStage.ELDERLY:
                        sleep_hours = 8.0
                    action_candidate = SleepAction(npc=self.npc, simulation_context=simulation_context, duration_hours=sleep_hours)
                
                elif action_class_to_try == EatAction:
                    action_candidate = EatAction(npc=self.npc, simulation_context=simulation_context)
                
                elif action_class_to_try == DrinkAction:
                    action_candidate = DrinkAction(npc=self.npc, simulation_context=simulation_context, drink_type="WATER")

                elif action_class_to_try == UseBathroomAction: # Usa il nome classe corretto
                    action_candidate = UseBathroomAction(npc=self.npc, simulation_context=simulation_context, for_need=most_pressing_need_type)
                
                elif action_class_to_try == HaveFunAction:
                    # Assicurati che FunActivityType sia importato
                    available_activities = list(FunActivityType) if FunActivityType else []
                    chosen_activity = random.choice(available_activities) if available_activities else (FunActivityType.DAYDREAM if FunActivityType and hasattr(FunActivityType, 'DAYDREAM') else None)
                    if chosen_activity:
                        action_candidate = HaveFunAction(npc=self.npc, simulation_context=simulation_context, activity_type=chosen_activity)
                    else: # Fallback se FunActivityType.DAYDREAM non è accessibile
                        if settings.DEBUG_MODE: print(f"  [AI Decide WARN - {self.npc.name}] FunActivityType non definito o DAYDREAM mancante.")
                
                elif action_class_to_try == SocializeAction:
                    target_npc_id = None
                    if simulation_context and self.npc.current_location_id:
                         current_loc = simulation_context.get_location_by_id(self.npc.current_location_id)
                         if current_loc:
                             potential_targets = [oid for oid in current_loc.npcs_present_ids if oid != self.npc.npc_id]
                             if potential_targets:
                                 target_npc_id = random.choice(potential_targets)
                    if target_npc_id:
                         action_candidate = SocializeAction(npc=self.npc, simulation_context=simulation_context, target_npc_id=target_npc_id)
                
                if action_candidate and action_candidate.is_valid():
                    score = self._calculate_action_score(action_candidate.effects_on_needs)
                    if self.last_selected_action_type == action_candidate.action_type_enum:
                        score *= (1.0 - (self.consecutive_action_type_count * 0.25))
                    for trait in self.npc.traits.values():
                        if hasattr(trait, 'get_action_choice_priority_modifier'):
                            score *= trait.get_action_choice_priority_modifier(action_candidate.action_type_enum, simulation_context)
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
        """Resetta lo stato interno del decision maker, es. per forzare una rivalutazione."""
        self.ticks_since_last_base_action_check = self.BASE_ACTION_CHECK_INTERVAL_TICKS 
        self.last_selected_action_type = None
        self.consecutive_action_type_count = 0