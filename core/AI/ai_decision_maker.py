# core/AI/ai_decision_maker.py
"""
Modulo per la logica decisionale dell'Intelligenza Artificiale degli NPC.
Contiene AIDecisionMaker che sceglie le azioni per un NPC.
Riferimento TODO: IV.4
"""
import random
from typing import TYPE_CHECKING, Optional, List, Dict, Tuple

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation
    from core.modules.actions import BaseAction

from core.enums import (
    Interest, NeedType, FunActivityType, SocialInteractionType, 
    RelationshipType,
)
from core.modules.actions import (
    EatAction, SleepAction, UseBathroomAction, HaveFunAction, 
    SocializeAction, EngageIntimacyAction, DrinkWaterAction
)
from core import settings
from core.modules.time_manager import TimeManager

INTEREST_TO_FUN_ACTIVITIES_MAP: Dict[Interest, List[FunActivityType]] = {
    Interest.GAMING: [FunActivityType.PLAY_COMPUTER_GAME, FunActivityType.PLAY_BOARD_GAMES],
    Interest.READING: [FunActivityType.READ_BOOK_FOR_FUN],
    Interest.MUSIC_LISTENING: [FunActivityType.LISTEN_TO_MUSIC, FunActivityType.DANCE],
    Interest.MUSIC_PLAYING: [FunActivityType.PLAY_MUSICAL_INSTRUMENT, FunActivityType.DANCE],
    Interest.VISUAL_ARTS: [FunActivityType.ENGAGE_IN_HOBBY_ARTISTIC],
    Interest.WRITING: [FunActivityType.ENGAGE_IN_HOBBY_ARTISTIC],
    Interest.PHOTOGRAPHY: [FunActivityType.ENGAGE_IN_HOBBY_ARTISTIC],
    Interest.SPORTS_ACTIVE: [FunActivityType.DO_SPORTS_FOR_FUN, FunActivityType.DANCE],
    Interest.CRAFTS_GENERAL: [FunActivityType.ENGAGE_IN_HOBBY_CRAFT],
    Interest.TECHNOLOGY: [FunActivityType.PLAY_COMPUTER_GAME, FunActivityType.SOCIAL_MEDIA_Browse],
    Interest.BOARD_GAMES: [FunActivityType.PLAY_BOARD_GAMES],
    Interest.FILM_TV_SERIES: [FunActivityType.WATCH_TV],
    Interest.FASHION: [FunActivityType.GO_SHOPPING_FOR_FUN],
}

NEED_PRIORITY_WEIGHTS: Dict[NeedType, float] = {
    NeedType.BLADDER: 5.0,
    NeedType.HUNGER: 4.0,
    NeedType.THIRST: 4.2,
    NeedType.ENERGY: 3.8,
    NeedType.HYGIENE: 2.5,
    NeedType.SAFETY: 3.5,
    NeedType.COMFORT: 2.0,
    NeedType.SOCIAL: 2.2,
    NeedType.FUN: 1.5,
    NeedType.INTIMACY: 1.8,
    NeedType.ENVIRONMENT: 1.0,
    NeedType.ACHIEVEMENT: 0.8,
    NeedType.AUTONOMY: 0.7,
    NeedType.CREATIVITY: 0.9,
    NeedType.LEARNING: 0.9,
    NeedType.SPIRITUALITY: 0.6
}

class AIDecisionMaker:
    def __init__(self, npc: 'Character'):
        self.npc: 'Character' = npc
        if settings.DEBUG_MODE:
            print(f"    [AIDecisionMaker INIT] Creato per {self.npc.name}")

    def _calculate_need_urgency(self, need_type: NeedType, current_value: float) -> float:
        weight = NEED_PRIORITY_WEIGHTS.get(need_type, 1.0)
        urgency_score = (settings.NEED_MAX_VALUE - current_value) * weight
        if current_value <= settings.NEED_CRITICAL_THRESHOLD:
            urgency_score *= 2.0
        return urgency_score

    def decide_next_action(self, time_manager: TimeManager, simulation_context: 'Simulation'):
        if hasattr(self.npc, 'pending_intimacy_proposal_from') and self.npc.pending_intimacy_proposal_from:
            initiator_id = self.npc.pending_intimacy_proposal_from
            self.npc.pending_intimacy_proposal_from = None
            initiator_npc = simulation_context.get_npc_by_id(initiator_id)
            if initiator_npc:
                if settings.DEBUG_MODE: print(f"  [AI Decision - {self.npc.name}] Ricevuta proposta di intimità da {initiator_npc.name}. Decido...")
                accepted = self.npc.decide_on_intimacy_proposal(initiator_npc, simulation_context)
                if accepted:
                    if settings.DEBUG_MODE: print(f"    [AI Decision - {self.npc.name}] ACCETTATA proposta di intimità da {initiator_npc.name}.")
                    action_to_consider = EngageIntimacyAction(npc=self.npc, target_npc=initiator_npc, simulation_context=simulation_context)
                    if action_to_consider.is_valid():
                        self.npc.add_action_to_queue(action_to_consider)
                        if hasattr(initiator_npc, 'pending_intimacy_target_accepted'):
                            initiator_npc.pending_intimacy_target_accepted = self.npc.npc_id
                        return
                else:
                    if settings.DEBUG_MODE: print(f"    [AI Decision - {self.npc.name}] RIFIUTATA proposta di intimità da {initiator_npc.name}.")
                return

        if hasattr(self.npc, 'pending_intimacy_target_accepted') and self.npc.pending_intimacy_target_accepted:
            target_id = self.npc.pending_intimacy_target_accepted
            self.npc.pending_intimacy_target_accepted = None
            target_npc = simulation_context.get_npc_by_id(target_id)
            if target_npc:
                if settings.DEBUG_MODE: print(f"  [AI Decision - {self.npc.name}] Proposta di intimità precedente accettata da {target_npc.name}. Considero EngageIntimacyAction.")
                action_to_consider = EngageIntimacyAction(npc=self.npc, target_npc=target_npc, simulation_context=simulation_context)
                if action_to_consider.is_valid():
                    self.npc.add_action_to_queue(action_to_consider)
                    return
                elif settings.DEBUG_MODE: print(f"    [AI Decision - {self.npc.name}] EngageIntimacyAction con {target_npc.name} non più valida.")
            return

        actionable_needs: List[Tuple[float, NeedType]] = []
        for need_type, need_object in self.npc.needs.items():
            current_value = need_object.get_value()
            # --- MODIFICA: Considera THIRST anche se il suo valore iniziale potrebbe essere alto ---
            # Lo includiamo sempre se è definito, l'urgenza poi deciderà.
            # O meglio, lo includiamo se è sotto la soglia LOW, come gli altri.
            if current_value <= settings.NEED_LOW_THRESHOLD or need_type == NeedType.THIRST: # Temporaneamente includiamo sempre THIRST se esiste per vedere l'urgenza
                if need_type == NeedType.THIRST and current_value > settings.NEED_LOW_THRESHOLD: # Ma solo se sopra la soglia, non lo rendiamo super urgente
                    pass # Verrà comunque valutato se è l'unico bisogno o se l'urgenza è alta
                
                # Calcola l'urgenza solo per quelli veramente sotto la soglia o per la sete
                if current_value <= settings.NEED_LOW_THRESHOLD:
                    urgency = self._calculate_need_urgency(need_type, current_value)
                    actionable_needs.append((urgency, need_type))
        
        if not actionable_needs:
            return

        actionable_needs.sort(key=lambda x: x[0], reverse=True)

        action_to_consider: Optional['BaseAction'] = None
        chosen_need_type_for_action: Optional[NeedType] = None

        for urgency_score, need_type in actionable_needs:
            if settings.DEBUG_MODE:
                print(f"  [AI Decision - {self.npc.name}] Considero bisogno: {need_type.display_name_it()} (Val: {self.npc.get_need_value(need_type):.1f}, Urgenza: {urgency_score:.2f}).")

            temp_action: Optional['BaseAction'] = None
            if need_type == NeedType.HUNGER:
                temp_action = EatAction(npc=self.npc, simulation_context=simulation_context)
            elif need_type == NeedType.THIRST:
                temp_action = DrinkWaterAction(npc=self.npc, simulation_context=simulation_context)
            elif need_type == NeedType.ENERGY:
                sleep_hours_for_ai = getattr(settings, 'AI_CHOSEN_SLEEP_DURATION_HOURS', None)
                temp_action = SleepAction(npc=self.npc, duration_hours=sleep_hours_for_ai, simulation_context=simulation_context)
            elif need_type == NeedType.BLADDER:
                temp_action = UseBathroomAction(npc=self.npc, simulation_context=simulation_context)
            elif need_type == NeedType.HYGIENE:
                temp_action = UseBathroomAction(npc=self.npc, simulation_context=simulation_context)
            elif need_type == NeedType.FUN:
                preferred_fun_activities: List[FunActivityType] = [act for i in self.npc.get_interests() if i in INTEREST_TO_FUN_ACTIVITIES_MAP for act in INTEREST_TO_FUN_ACTIVITIES_MAP[i]]
                chosen_activity: Optional[FunActivityType] = None
                if preferred_fun_activities:
                    unique_preferred = list(set(preferred_fun_activities))
                    if unique_preferred:
                        chosen_activity = random.choice(unique_preferred)
                        if settings.DEBUG_MODE: print(f"    [AI Decision - {self.npc.name}] Bisogno FUN: Scelta attività basata su interessi: {chosen_activity.name if chosen_activity else 'Nessuna scelta da interessi'}")
                if chosen_activity is None:
                    all_fun_activities = list(FunActivityType)
                    if all_fun_activities:
                        chosen_activity = random.choice(all_fun_activities)
                        if settings.DEBUG_MODE: print(f"    [AI Decision - {self.npc.name}] Bisogno FUN: Ness. attività da interessi, scelta casuale: {chosen_activity.name if chosen_activity else 'Nessuna attività FUN disponibile'}")
                if chosen_activity:
                    temp_action = HaveFunAction(npc=self.npc, activity_type=chosen_activity, simulation_context=simulation_context)
                elif settings.DEBUG_MODE: print(f"    [AI Decision - {self.npc.name}] Nessuna FunActivityType disponibile per azione FUN.")
            elif need_type == NeedType.SOCIAL:
                target_npc_social = simulation_context.find_available_social_target(requesting_npc=self.npc)
                if target_npc_social:
                    chosen_interaction_type_social = random.choice([SocialInteractionType.CHAT_CASUAL, SocialInteractionType.COMPLIMENT])
                    if settings.DEBUG_MODE: print(f"        [AI Decision - {self.npc.name}] Scelto tipo interazione SOCIAL: {chosen_interaction_type_social.name} con {target_npc_social.name}")
                    temp_action = SocializeAction(npc=self.npc, target_npc=target_npc_social, interaction_type=chosen_interaction_type_social, simulation_context=simulation_context)
                elif settings.DEBUG_MODE: print(f"      [AI Decision - {self.npc.name}] Nessun target per socializzare.")
            elif need_type == NeedType.INTIMACY:
                current_sim_tick = time_manager.total_ticks_sim
                cooldown_key = "INTIMACY_PROPOSAL_COOLDOWN_TICKS"
                cooldown_ticks = getattr(settings, cooldown_key, settings.IXH * 1)
                if not (hasattr(self.npc, 'last_intimacy_proposal_tick') and \
                current_sim_tick < self.npc.last_intimacy_proposal_tick + cooldown_ticks):
                    suitable_partner: Optional['Character'] = None
                    if self.npc.relationships:
                        for rel_id, rel_info in self.npc.relationships.items():
                            if rel_info.type in {RelationshipType.ROMANTIC_PARTNER, RelationshipType.SPOUSE} and \
                            rel_info.score >= getattr(settings, "MIN_REL_SCORE_FOR_INTIMACY_PROPOSAL_ACCEPTANCE", 30):
                                partner = simulation_context.get_npc_by_id(rel_id)
                                if partner and not partner.is_busy: suitable_partner = partner; break
                    if suitable_partner:
                        temp_action = SocializeAction(npc=self.npc, target_npc=suitable_partner, interaction_type=SocialInteractionType.PROPOSE_INTIMACY, simulation_context=simulation_context)
                        if hasattr(self.npc, 'last_intimacy_proposal_tick'): self.npc.last_intimacy_proposal_tick = current_sim_tick
                else:
                    if settings.DEBUG_MODE: print(f"    [AI Decision - {self.npc.name}] INTIMACY basso, ma in cooldown per nuova proposta ({self.npc.last_intimacy_proposal_tick + cooldown_ticks - current_sim_tick}t rim.).")

            if temp_action and temp_action.is_valid():
                action_to_consider = temp_action
                chosen_need_type_for_action = need_type
                if settings.DEBUG_MODE: print(f"    [AI Decision - {self.npc.name}] Azione VALIDA '{action_to_consider.action_type_name}' scelta per bisogno {chosen_need_type_for_action.display_name_it()}.")
                break
            elif temp_action and settings.DEBUG_MODE:
                print(f"    [AI Decision - {self.npc.name}] Azione '{temp_action.action_type_name}' per {need_type.display_name_it()} NON valida.")

        if action_to_consider:
            self.npc.add_action_to_queue(action_to_consider)
        elif settings.DEBUG_MODE and actionable_needs:
            print(f"    [AI Decision - {self.npc.name}] Nessuna azione valida trovata per i bisogni urgenti: {[n.name for u, n in actionable_needs]}.")
