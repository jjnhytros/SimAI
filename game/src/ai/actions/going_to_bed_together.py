# game/src/ai/actions/going_to_bed_together.py
import logging
from typing import TYPE_CHECKING, Optional

# Importa dal package 'game'
from game import config
from game.src.utils import game as game_utils # Per find_path_to_target, occupy_bed_slot, ecc.

if TYPE_CHECKING:
    from game.src.entities.character import Character
    from game.src.modules.game_state_module import GameState

logger = logging.getLogger(__name__)
DEBUG_AI = getattr(config, 'DEBUG_AI_ACTIVE', False)

# --- Funzione di Avvio Azione ---

def start_going_to_bed_together(npc_leader: 'Character', 
                                npc_follower: 'Character', 
                                game_state: 'GameState', 
                                pf_grid) -> bool:
    """
    Inizia la sequenza per due NPC che vanno a letto insieme.
    Trova due slot letto liberi, calcola i percorsi e imposta lo stato degli NPC.
    Restituisce True se la sequenza può iniziare, False altrimenti.
    Chiamata da romantic_interaction.handle_arrival_at_partner_for_intimacy.
    """
    if DEBUG_AI:
        logger.debug(f"AI ({npc_leader.name} & {npc_follower.name}): Tentativo di iniziare 'going_to_bed_together'.")

    slot0_interaction_pos = game_state.bed_slot_1_interaction_pos_world
    slot1_interaction_pos = game_state.bed_slot_2_interaction_pos_world
    
    chosen_slot_leader = -1
    chosen_slot_follower = -1
    leader_bed_destination = None
    follower_bed_destination = None

    # Logica semplice: leader prende il primo slot disponibile, follower il secondo.
    # Potrebbe essere migliorata per scegliere gli slot più vicini a ciascun NPC.
    if slot0_interaction_pos and not game_state.bed_slot_1_occupied_by:
        chosen_slot_leader = 0
        leader_bed_destination = slot0_interaction_pos
        if slot1_interaction_pos and not game_state.bed_slot_2_occupied_by:
            chosen_slot_follower = 1
            follower_bed_destination = slot1_interaction_pos
        else: # Non c'è un secondo slot libero
            chosen_slot_leader = -1 # Annulla se non ci sono due slot
            leader_bed_destination = None
    elif slot1_interaction_pos and not game_state.bed_slot_2_occupied_by: # Slot 0 occupato, prova slot 1 per leader
        chosen_slot_leader = 1
        leader_bed_destination = slot1_interaction_pos
        if slot0_interaction_pos and not game_state.bed_slot_1_occupied_by: # Controlla se slot 0 è libero per follower
            chosen_slot_follower = 0
            follower_bed_destination = slot0_interaction_pos
        else:
            chosen_slot_leader = -1
            leader_bed_destination = None

    if chosen_slot_leader != -1 and chosen_slot_follower != -1 and leader_bed_destination and follower_bed_destination:
        if DEBUG_AI:
            logger.debug(f"AI ({npc_leader.name} & {npc_follower.name}): Slot letto trovati. Leader->{chosen_slot_leader}, Follower->{chosen_slot_follower}")

        path_leader_to_bed = game_utils.find_path_to_target(npc_leader, leader_bed_destination, pf_grid, game_state.world_objects_list)
        path_follower_to_bed = game_utils.find_path_to_target(npc_follower, follower_bed_destination, pf_grid, game_state.world_objects_list)

        if path_leader_to_bed and path_follower_to_bed:
            npc_leader.current_action_before_movement = "going_to_bed_together_leader"
            npc_leader.current_action = "moving_to_target"
            npc_leader.target_destination = leader_bed_destination
            npc_leader.current_path = path_leader_to_bed
            npc_leader.bed_slot_index = chosen_slot_leader
            npc_leader.target_partner = npc_follower # Leader sa chi è il follower
            npc_leader.previous_action_was_movement_to_target = True
            npc_leader.is_interacting = True # Impegnato nella sequenza

            npc_follower.current_action_before_movement = "going_to_bed_together_follower"
            npc_follower.current_action = "moving_to_target"
            npc_follower.target_destination = follower_bed_destination
            npc_follower.current_path = path_follower_to_bed
            npc_follower.bed_slot_index = chosen_slot_follower
            npc_follower.target_partner = npc_leader # Follower sa chi è il leader
            npc_follower.previous_action_was_movement_to_target = True
            npc_follower.is_interacting = True # Impegnato nella sequenza
            # Il follower era in "accepting_intimacy_and_waiting", ora si muove
            npc_follower.time_in_current_action = 0.0 


            if DEBUG_AI:
                logger.debug(f"AI ({npc_leader.name}): Inizio 'going_to_bed_together_leader' verso slot {chosen_slot_leader}.")
                logger.debug(f"AI ({npc_follower.name}): Inizio 'going_to_bed_together_follower' verso slot {chosen_slot_follower}.")
            return True
        else:
            if DEBUG_AI:
                logger.warning(f"AI WARN ({npc_leader.name} o {npc_follower.name}): Path non trovato per uno o entrambi verso il letto.")
            # Resetta target partner se il path fallisce
            npc_leader.target_partner = None
            npc_follower.target_partner = None
            return False
    else:
        if DEBUG_AI:
            logger.info(f"AI INFO ({npc_leader.name} & {npc_follower.name}): Non ci sono due slot letto liberi o posizioni non definite.")
        return False

# --- Funzioni di Aggiornamento (principalmente per lo stato di movimento) ---
# Queste azioni sono principalmente "moving_to_target". L'update del movimento è in Character.py.
# Queste funzioni potrebbero essere vuote o gestire logiche specifiche se l'azione ha più fasi
# oltre al semplice movimento. Per ora, le azioni "_leader" e "_follower" sono solo stati
# che indicano l'obiettivo del movimento. L'arrivo è più importante.

def update_going_to_bed_leader(npc: 'Character', game_state: 'GameState', hours_passed_this_tick: float) -> bool:
    """
    Logica di aggiornamento per l'NPC leader che va a letto.
    Principalmente uno stato; il movimento è gestito da Character.update().
    Restituisce True (l'azione di movimento è implicitamente in corso finché Character.update non la termina).
    """
    # Se l'NPC non si sta più muovendo ma è ancora in questa azione, qualcosa è andato storto
    # o è arrivato (ma l'arrivo è gestito in handle_arrival_at_bed_leader).
    if not npc.current_path and not npc.target_destination:
        logger.warning(f"AI WARN ({npc.name}): In 'going_to_bed_together_leader' ma senza path/destinazione. Forse arrivato?")
        # L'arrivo verrà gestito dal dispatcher di npc_behavior
        return True # Lascia che l'handler di arrivo faccia il suo lavoro
    return True

def update_going_to_bed_follower(npc: 'Character', game_state: 'GameState', hours_passed_this_tick: float) -> bool:
    """
    Logica di aggiornamento per l'NPC follower che va a letto.
    Principalmente uno stato.
    """
    if not npc.current_path and not npc.target_destination:
        logger.warning(f"AI WARN ({npc.name}): In 'going_to_bed_together_follower' ma senza path/destinazione. Forse arrivato?")
        return True
    return True

# --- Funzioni Handler per Arrivo ---

def _handle_common_arrival_at_bed_for_intimacy(npc: 'Character', game_state: 'GameState', pf_grid, action_name_for_log: str) -> bool:
    """Logica comune per quando un NPC (leader o follower) arriva al letto per intimità."""
    if DEBUG_AI:
        logger.debug(f"AI ({npc.name} - {action_name_for_log}): Arrivato al punto di interazione del letto (slot: {npc.bed_slot_index}).")

    # Occupa lo slot letto (dovrebbe essere già stato "prenotato" logicamente da bed_slot_index)
    slot_occupied = game_utils.occupy_bed_slot_for_character(game_state, npc, npc.bed_slot_index)

    if slot_occupied:
        npc.is_on_bed = True
        # Posiziona l'NPC sulla sleeping_pos
        sleep_pos_world = None
        if npc.bed_slot_index == 0:
            sleep_pos_world = game_state.bed_slot_1_sleep_pos_world
        elif npc.bed_slot_index == 1:
            sleep_pos_world = game_state.bed_slot_2_sleep_pos_world
        
        if sleep_pos_world:
            npc.x, npc.y = sleep_pos_world
            npc.rect.center = (int(npc.x), int(npc.y))
        else:
            logger.warning(f"AI WARN ({npc.name}): Posizione sonno per slot {npc.bed_slot_index} non definita.")
        
        # Controlla se anche il partner è arrivato e a letto
        partner = npc.target_partner
        if partner and partner.is_on_bed and partner.bed_object_id == "main_bed" and \
           partner.bed_slot_index is not None and partner.bed_slot_index != npc.bed_slot_index and \
           partner.target_partner == npc and \
           partner.current_action in ["cuddling_in_bed", "moving_to_target", "going_to_bed_together_leader", "going_to_bed_together_follower", "waiting_in_bed_for_partner"]: # Partner potrebbe essere già in cuddling o ancora in movimento/attesa
            
            logger.info(f"AI ({npc.name}): Entrambi gli NPC sono a letto. Inizio 'cuddling_in_bed'.")
            from .cuddling_in_bed import start_cuddling_in_bed # Importa qui per evitare dipendenze circolari a livello di modulo
            start_cuddling_in_bed(npc, partner, game_state) # Questa funzione imposterà l'azione per entrambi
            return True # Azione di arrivo completata, nuova azione iniziata
        elif partner:
            logger.info(f"AI ({npc.name}): Arrivato a letto e nello slot. In attesa di {partner.name} (Stato partner: {partner.current_action}, is_on_bed: {partner.is_on_bed}).")
            npc.current_action = "waiting_in_bed_for_partner" # Nuovo stato per l'attesa
            npc.time_in_current_action = 0.0
            return True # Transizione a uno stato di attesa
        else: # Partner non valido o non più coinvolto
            logger.warning(f"AI WARN ({npc.name}): Arrivato a letto, ma il partner non è valido/pronto. Torno idle.")
            game_utils.free_bed_slot_for_character(game_state, npc) # Libera lo slot appena occupato
            npc.current_action = "idle"
            npc.target_partner = None
            return False
    else:
        logger.warning(f"AI WARN ({npc.name} - {action_name_for_log}): Fallito l'occupazione dello slot letto {npc.bed_slot_index} all'arrivo. Torno idle.")
        npc.current_action = "idle"
        npc.bed_slot_index = -1 # Resetta
        npc.target_partner = None
        return False


def handle_arrival_at_bed_leader(npc: 'Character', game_state: 'GameState', pf_grid) -> bool:
    return _handle_common_arrival_at_bed_for_intimacy(npc, game_state, pf_grid, "GoingToBedLeader")

def handle_arrival_at_bed_follower(npc: 'Character', game_state: 'GameState', pf_grid) -> bool:
    return _handle_common_arrival_at_bed_for_intimacy(npc, game_state, pf_grid, "GoingToBedFollower")

def update_waiting_in_bed_for_partner(npc: 'Character', game_state: 'GameState', hours_passed_this_tick: float) -> bool:
    """
    Aggiorna lo stato dell'NPC che è a letto e aspetta il partner.
    Restituisce True se l'NPC sta ancora aspettando, False se l'attesa è terminata.
    """
    waiting_timeout_hours = getattr(config, 'INTIMACY_BED_WAITING_TIMEOUT_HOURS', 0.3) # Timeout più breve a letto
    npc.time_in_current_action += hours_passed_this_tick
    partner = npc.target_partner

    # Se il partner arriva e si mette a letto, la transizione a "cuddling" avviene nell'handler di arrivo del partner.
    # Qui controlliamo se il partner è effettivamente in cuddling con questo NPC.
    if partner and partner.current_action == "cuddling_in_bed" and partner.target_partner == npc:
        if DEBUG_AI: logger.debug(f"AI ({npc.name}): Partner {partner.name} ha iniziato cuddling. {npc.name} si unisce.")
        # La funzione start_cuddling_in_bed dovrebbe già aver impostato anche questo NPC a cuddling.
        # Se npc.current_action non è già "cuddling_in_bed", c'è un problema di sincronizzazione.
        if npc.current_action != "cuddling_in_bed":
            from .cuddling_in_bed import start_cuddling_in_bed
            start_cuddling_in_bed(npc, partner, game_state) # Tenta di forzare la sincronizzazione
        return True # L'azione cuddling_in_bed prenderà il sopravvento

    if not partner or partner.target_partner != npc or \
       partner.current_action not in ["moving_to_target", "going_to_bed_together_follower", "going_to_bed_together_leader", "waiting_in_bed_for_partner", "cuddling_in_bed"]:
        if DEBUG_AI: logger.warning(f"AI WARN ({npc.name}): Partner {partner.name if partner else 'None'} non più valido o in stato imprevisto mentre {npc.name} aspettava a letto. {npc.name} esce dal letto.")
        game_utils.free_bed_slot_for_character(game_state, npc)
        npc.current_action = "idle"
        npc.target_partner = None
        return False

    if npc.time_in_current_action >= waiting_timeout_hours:
        if DEBUG_AI: logger.info(f"AI ({npc.name}): Timeout attesa a letto per {partner.name if partner else 'partner'}. Esco dal letto.")
        game_utils.free_bed_slot_for_character(game_state, npc)
        npc.current_action = "idle"
        # Informa il partner che l'attesa è finita, se il partner era ancora in targeting
        if partner and partner.target_partner == npc:
            partner.target_partner = None
            if partner.current_action in ["moving_to_target", "going_to_bed_together_follower", "going_to_bed_together_leader"]:
                 partner.current_action = "idle" # Il partner smette di cercare di raggiungere questo NPC per il letto
                 partner.target_destination = None
                 partner.current_path = None
        npc.target_partner = None
        return False
    
    if DEBUG_AI: logger.debug(f"AI ({npc.name}): Ancora in attesa a letto per {partner.name if partner else 'partner'}. Timer: {npc.time_in_current_action:.2f}")
    return True