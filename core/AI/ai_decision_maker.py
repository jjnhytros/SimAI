# core/ai/ai_decision_maker.py
"""
Modulo per la logica decisionale dell'Intelligenza Artificiale degli NPC.
Contiene AIDecisionMaker che sceglie le azioni per un NPC.
Riferimento TODO: IV.4
"""
import random
from typing import TYPE_CHECKING, Optional, List, Dict

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation
    from core.modules.actions import BaseAction # Per il type hint di ritorno

from core.enums import (
    Interest, NeedType, FunActivityType, SocialInteractionType, RelationshipType
)
from core.modules.actions import ( # Importa tutte le azioni che può scegliere
    EatAction, SleepAction, UseBathroomAction, HaveFunAction, SocializeAction, EngageIntimacyAction
)
from core import settings
from core.modules.time_manager import TimeManager # Potrebbe servire per decisioni basate sull'ora

# --- Mappa da Interessi ad Attività Divertenti ---
# (Spostata qui da Character.py)
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
    # ... (completa con altre associazioni) ...
}

class AIDecisionMaker:
    def __init__(self, npc: 'Character'):
        self.npc: 'Character' = npc
        # Potremmo anche passare e memorizzare simulation_context qui se è sempre lo stesso,
        # ma passarlo a decide_next_action è più flessibile se il contesto potesse cambiare.
        if settings.DEBUG_MODE:
            print(f"    [AIDecisionMaker INIT] Creato per {self.npc.name}")

    def decide_next_action(self, time_manager: TimeManager, simulation_context: 'Simulation'):
        """
        Logica decisionale dell'IA per scegliere la prossima azione per self.npc.
        Questa è la versione spostata di Character.choose_action().
        L'azione scelta viene accodata direttamente all'NPC.
        """
        # if settings.DEBUG_MODE:
        #     print(f"    >>> AI DECIDING for '{self.npc.name}' (Occupato: {self.npc.is_busy}, Coda: {len(self.npc.action_queue)})")

        # Gestione Proposte di Intimità Ricevute (se questa logica resta qui o va in una "reazione")
        if hasattr(self.npc, 'pending_intimacy_proposal_from') and self.npc.pending_intimacy_proposal_from:
            initiator_id = self.npc.pending_intimacy_proposal_from
            self.npc.pending_intimacy_proposal_from = None 
            initiator_npc = simulation_context.get_npc_by_id(initiator_id)

            if initiator_npc:
                if settings.DEBUG_MODE: print(f"  [AI Decision - {self.npc.name}] Ricevuta proposta di intimità da {initiator_npc.name}. Decido...")
                accepted = self.npc.decide_on_intimacy_proposal(initiator_npc, simulation_context) # Chiama metodo di Character
                
                if accepted:
                    if settings.DEBUG_MODE: print(f"    [AI Decision - {self.npc.name}] ACCETTATA proposta di intimità da {initiator_npc.name}.")
                    action_to_consider = EngageIntimacyAction(npc=self.npc, target_npc=initiator_npc, simulation_context=simulation_context)
                    if action_to_consider.is_valid():
                        self.npc.add_action_to_queue(action_to_consider)
                        if hasattr(initiator_npc, 'pending_intimacy_target_accepted'): # Notifica l'iniziatore
                             initiator_npc.pending_intimacy_target_accepted = self.npc.npc_id
                        return # Azione scelta, esci
                else:
                    if settings.DEBUG_MODE: print(f"    [AI Decision - {self.npc.name}] RIFIUTATA proposta di intimità da {initiator_npc.name}.")
                return # Ha gestito la proposta, esce per questo tick

        # Gestione Proposte di Intimità Accettate (fatte da questo NPC)
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
            

        lowest_need_info = self.npc.get_lowest_need()
        if lowest_need_info:
            need_type, value = lowest_need_info
            
            if value <= settings.NEED_LOW_THRESHOLD: 
                if settings.DEBUG_MODE:
                    print(f"  [AI Decision - {self.npc.name}] Bisogno prioritario: {need_type.display_name_it()} ({value:.1f}). Valuto azione...")
                
                action_to_consider: Optional['BaseAction'] = None # Type hint corretto
                
                if need_type == NeedType.HUNGER:
                    action_to_consider = EatAction(npc=self.npc, simulation_context=simulation_context)
                elif need_type == NeedType.ENERGY:
                    sleep_hours_for_ai = getattr(settings, 'AI_CHOSEN_SLEEP_DURATION_HOURS', None) 
                    action_to_consider = SleepAction(npc=self.npc, duration_hours=sleep_hours_for_ai, simulation_context=simulation_context)
                elif need_type == NeedType.BLADDER:
                    action_to_consider = UseBathroomAction(npc=self.npc, simulation_context=simulation_context)
                elif need_type == NeedType.HYGIENE:
                    action_to_consider = UseBathroomAction(npc=self.npc, simulation_context=simulation_context)
                
                elif need_type == NeedType.FUN:
                    preferred_fun_activities: List[FunActivityType] = []
                    for interest in self.npc.get_interests():
                        if interest in INTEREST_TO_FUN_ACTIVITIES_MAP:
                            preferred_fun_activities.extend(INTEREST_TO_FUN_ACTIVITIES_MAP[interest])
                    chosen_activity: Optional[FunActivityType] = None
                    if preferred_fun_activities:
                        unique_preferred = list(set(preferred_fun_activities))
                        if unique_preferred: chosen_activity = random.choice(unique_preferred) 
                        if settings.DEBUG_MODE: print(f"    [AI Decision - {self.npc.name}] Bisogno FUN: Scelta attività basata su interessi: {chosen_activity.name if chosen_activity else 'Nessuna'}")
                    if not chosen_activity: 
                        available_fun_activities = list(FunActivityType)
                        if available_fun_activities:
                            chosen_activity = random.choice(available_fun_activities)
                            if settings.DEBUG_MODE: print(f"    [AI Decision - {self.npc.name}] Bisogno FUN: Ness. attività preferita, scelta casuale: {chosen_activity.name}")
                    if chosen_activity:
                        action_to_consider = HaveFunAction(npc=self.npc, activity_type=chosen_activity, simulation_context=simulation_context)
                    elif settings.DEBUG_MODE: print(f"    [AI Decision - {self.npc.name}] Nessuna FunActivityType per azione FUN.")

                elif need_type == NeedType.SOCIAL:
                    # ... (logica per trovare target_npc_social e chosen_interaction_type_social come prima, usando self.npc e simulation_context) ...
                    # Esempio abbreviato:
                    target_npc_social = simulation_context.find_available_social_target(requesting_npc=self.npc)
                    if target_npc_social:
                        chosen_interaction_type_social = random.choice([SocialInteractionType.CHAT_CASUAL, SocialInteractionType.COMPLIMENT]) # Semplificato
                        if settings.DEBUG_MODE: print(f"        [AI Decision - {self.npc.name}] Scelto tipo interazione SOCIAL: {chosen_interaction_type_social.name} con {target_npc_social.name}")
                        action_to_consider = SocializeAction(npc=self.npc, target_npc=target_npc_social, interaction_type=chosen_interaction_type_social, simulation_context=simulation_context)
                    elif settings.DEBUG_MODE: print(f"      [AI Decision - {self.npc.name}] Nessun target per socializzare.")

                elif need_type == NeedType.INTIMACY:
                    current_sim_tick = time_manager.total_ticks_sim # Usa time_manager passato
                    if hasattr(self.npc, 'last_intimacy_proposal_tick') and \
                       current_sim_tick < self.npc.last_intimacy_proposal_tick + getattr(settings, "INTIMACY_PROPOSAL_COOLDOWN_TICKS", 60):
                        if settings.DEBUG_MODE: print(f"    [AI Decision - {self.npc.name}] INTIMACY basso, ma in cooldown per nuova proposta.")
                    else:
                        # ... (logica per trovare suitable_partner_for_proposal come prima, usando self.npc e simulation_context) ...
                        suitable_partner_for_proposal: Optional['Character'] = None
                        # (Logica di ricerca partner da Character.choose_action)
                        if suitable_partner_for_proposal:
                            if settings.DEBUG_MODE: print(f"      [AI Decision - {self.npc.name}] Trovato partner {suitable_partner_for_proposal.name} per PROPORRE intimità.")
                            action_to_consider = SocializeAction(npc=self.npc, target_npc=suitable_partner_for_proposal, 
                                                                 interaction_type=SocialInteractionType.PROPOSE_INTIMACY, 
                                                                 simulation_context=simulation_context)
                            if hasattr(self.npc, 'last_intimacy_proposal_tick'): self.npc.last_intimacy_proposal_tick = current_sim_tick
                        elif settings.DEBUG_MODE: print(f"      [AI Decision - {self.npc.name}] Nessun partner per PROPORRE intimità.")
                
                if action_to_consider:
                    if settings.DEBUG_MODE: print(f"    [AI Decision - {self.npc.name}] Considero azione: {action_to_consider.action_type_name} per {need_type.name if need_type else 'N/D'}")
                    if action_to_consider.is_valid():
                        self.npc.add_action_to_queue(action_to_consider) # Accoda all'NPC
                    elif settings.DEBUG_MODE: print(f"    [AI Decision - {self.npc.name}] Azione '{action_to_consider.action_type_name}' non valida.")
                elif settings.DEBUG_MODE and need_type in {NeedType.HUNGER, NeedType.ENERGY, NeedType.BLADDER, NeedType.HYGIENE, NeedType.FUN, NeedType.SOCIAL, NeedType.INTIMACY}:
                    print(f"    [AI Decision - {self.npc.name}] Nessuna azione istanziata per {need_type.display_name_it() if need_type else 'N/D'} ({value:.1f}).")
            # else: (log bisogni non bassi)
        # else: (log nessun bisogno)