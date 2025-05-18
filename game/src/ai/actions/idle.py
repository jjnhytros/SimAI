# game/src/ai/actions/idle.py
import logging
import random
from typing import TYPE_CHECKING, List, Optional

# Importa dal package 'game'
from game import config
from game.src.utils import game as game_utils # Per find_path_to_target, world_to_grid, ecc.

if TYPE_CHECKING:
    from game.src.entities.character import Character
    from game.src.modules.game_state_module import GameState

logger = logging.getLogger(__name__)
DEBUG_AI = getattr(config, 'DEBUG_AI_ACTIVE', False)

# Importa le funzioni di "start" delle altre azioni se handle_idle_decision le chiama direttamente
# Altrimenti, handle_idle_decision imposterà solo npc.current_action e i target,
# e npc_behavior.py gestirà l'avvio effettivo.
# Per ora, assumiamo che handle_idle_decision imposti solo lo stato per altre azioni.
# from . import seeking_bed, phoning, romantic_interaction, wandering # Esempio

def handle_idle_decision(npc: 'Character', 
                         all_npcs: List['Character'], 
                         pf_grid, # Griglia di pathfinding
                         game_state: 'GameState'):
    """
    Logica decisionale per un NPC in stato "idle".
    Determina la prossima azione in base ai bisogni e al contesto.
    Modifica npc.current_action, npc.target_destination, npc.current_path,
    npc.current_action_before_movement, npc.previous_action_was_movement_to_target.
    """
    if DEBUG_AI:
        logger.debug(f"AI Decision ({npc.name}): In idle. Valutazione bisogni...")
        logger.debug(f"AI Decision ({npc.name}): Energia: {npc.energy.get_value():.1f}/{npc.energy.max_value:.0f} (Soglia: {config.NPC_ENERGY_THRESHOLD})")
        logger.debug(f"AI Decision ({npc.name}): Fame: {npc.hunger.get_value():.1f}/{npc.hunger.max_value:.0f} (Soglia: {config.NPC_HUNGER_THRESHOLD})")
        logger.debug(f"AI Decision ({npc.name}): Vescica: {npc.bladder.get_value():.1f}/{npc.bladder.max_value:.0f} (Soglia: {config.NPC_BLADDER_THRESHOLD})")
        logger.debug(f"AI Decision ({npc.name}): Social: {npc.social.get_value():.1f}/{npc.social.max_value:.0f} (Soglia: {config.NPC_SOCIAL_THRESHOLD})")
        logger.debug(f"AI Decision ({npc.name}): Intimità: {npc.intimacy.get_value():.1f}/{npc.intimacy.max_value:.0f} (Soglia Richiesta: {config.NPC_INTIMACY_THRESHOLD})")
        logger.debug(f"AI Decision ({npc.name}): Divertimento: {npc.fun.get_value():.1f}/{npc.fun.max_value:.0f} (Soglia: {config.NPC_FUN_THRESHOLD})")
        logger.debug(f"AI Decision ({npc.name}): Igiene: {npc.hygiene.get_value():.1f}/{npc.hygiene.max_value:.0f} (Soglia: {config.NPC_HYGIENE_THRESHOLD})")


    # --- Priorità 1: Bisogni Critici ---
    # Energia / Sonno
    if npc.energy.get_value() < config.NPC_ENERGY_THRESHOLD:
        if DEBUG_AI: logger.debug(f"AI Decision ({npc.name}): Energia bassa ({npc.energy.get_value():.1f}). Cerco letto.")
        
        # Logica per trovare e andare a letto (simile a quella che avevi in _make_idle_decision)
        # Questo potrebbe essere estratto in una funzione helper in seeking_bed.py
        # from .seeking_bed import attempt_to_find_and_go_to_bed
        # if attempt_to_find_and_go_to_bed(npc, game_state, pf_grid):
        #     return # Decisione presa

        # Logica semplificata per ora, per mantenere la funzione contenuta:
        bed_interaction_pos = None
        chosen_slot_index = -1

        # Controlla Slot 0 (o "slot 1" come definito nel game_state)
        if game_state.bed_slot_1_interaction_pos_world and not game_state.bed_slot_1_occupied_by:
            bed_interaction_pos = game_state.bed_slot_1_interaction_pos_world
            chosen_slot_index = 0
            if DEBUG_AI: logger.debug(f"AI Decision ({npc.name}): Slot 0 letto disponibile a {bed_interaction_pos}.")
        # Controlla Slot 1 (o "slot 2" come definito nel game_state)
        elif game_state.bed_slot_2_interaction_pos_world and not game_state.bed_slot_2_occupied_by:
            bed_interaction_pos = game_state.bed_slot_2_interaction_pos_world
            chosen_slot_index = 1
            if DEBUG_AI: logger.debug(f"AI Decision ({npc.name}): Slot 1 letto disponibile a {bed_interaction_pos}.")
        
        if bed_interaction_pos:
            bed_interaction_pos_int = (int(bed_interaction_pos[0]), int(bed_interaction_pos[1]))
            path_to_bed = game_utils.find_path_to_target(npc, bed_interaction_pos_int, pf_grid, game_state.world_objects_list)
            if path_to_bed:
                if DEBUG_AI: logger.debug(f"AI Decision ({npc.name}): Path trovato per letto slot {chosen_slot_index} a {bed_interaction_pos_int}.")
                npc.current_action_before_movement = "seeking_bed"
                npc.current_action = "moving_to_target"
                npc.target_destination = bed_interaction_pos_int
                npc.current_path = path_to_bed
                npc.bed_slot_index = chosen_slot_index # Memorizza lo slot target
                npc.previous_action_was_movement_to_target = True
                return
            else:
                if DEBUG_AI: logger.warning(f"AI WARN ({npc.name}): No path to bed slot {chosen_slot_index} at {bed_interaction_pos_int}.")
        elif DEBUG_AI:
            logger.info(f"AI INFO ({npc.name}): Energia bassa, ma nessun letto libero o posizioni letto non definite.")
    
    # Bisogno Vescica (Bladder)
    if npc.bladder.get_value() > config.NPC_BLADDER_THRESHOLD: # Alto è male per la vescica
        if DEBUG_AI: logger.debug(f"AI Decision ({npc.name}): Vescica piena ({npc.bladder.get_value():.1f}). Cerco bagno.")
        if game_state.toilet_rect_instance:
            # Determina un punto di interazione per il bagno
            # Esempio: davanti al bagno. Dovresti definire questo nel blueprint dell'oggetto WC.
            # Per ora, usiamo il centro del lato inferiore come punto di interazione grezzo.
            interaction_x = game_state.toilet_rect_instance.centerx
            interaction_y = game_state.toilet_rect_instance.bottom + config.TILE_SIZE // 2 # Un po' sotto
            toilet_interaction_pos = (interaction_x, interaction_y)

            path_to_toilet = game_utils.find_path_to_target(npc, toilet_interaction_pos, pf_grid, game_state.world_objects_list)
            if path_to_toilet:
                if DEBUG_AI: logger.debug(f"AI Decision ({npc.name}): Path trovato per bagno a {toilet_interaction_pos}.")
                npc.current_action_before_movement = "seeking_toilet"
                npc.current_action = "moving_to_target"
                npc.target_destination = toilet_interaction_pos
                npc.current_path = path_to_toilet
                npc.previous_action_was_movement_to_target = True
                return
            else:
                if DEBUG_AI: logger.warning(f"AI WARN ({npc.name}): No path to toilet at {toilet_interaction_pos}.")
        elif DEBUG_AI:
            logger.info(f"AI INFO ({npc.name}): Vescica piena, ma nessun bagno definito in game_state.")

    # TODO: Aggiungere qui la logica per cercare Cibo se npc.hunger.get_value() < config.NPC_HUNGER_THRESHOLD

    # --- Priorità 2: Bisogni Sociali/Intimità (se non critici) ---
    # Gestione richiesta di intimità ricevuta
    if npc.pending_intimacy_requester and npc.current_action == "idle": # Verifica di essere idle
        partner_candidate = npc.pending_intimacy_requester
        if DEBUG_AI: logger.debug(f"AI Decision ({npc.name}): Ricevuta richiesta di intimità da {partner_candidate.name}. Accetto e attendo.")
        npc.current_action = "accepting_intimacy_and_waiting"
        npc.target_partner = partner_candidate
        npc.target_destination = None
        npc.current_path = None
        npc.is_interacting = True
        npc.pending_intimacy_requester = None # Richiesta gestita
        return # Decisione presa

    # Iniziare intimità
    # Assicurati che NPC_INTIMACY_THRESHOLD sia definito in config (es. 75, dove più alto significa più bisogno)
    # e che intimacy.high_is_good sia False (quindi un valore ALTO significa bisogno NON soddisfatto)
    if npc.intimacy.get_value() > config.NPC_INTIMACY_THRESHOLD and \
       len(all_npcs) > 1 and npc.current_action == "idle": # Assicurati che sia idle per iniziare
        if DEBUG_AI: logger.debug(f"AI Decision ({npc.name}): Bisogno di intimità ({npc.intimacy.get_value():.1f}). Cerco partner idle.")
        
        potential_partners = [p for p in all_npcs if p.uuid != npc.uuid and p.current_action == "idle" and p.pending_intimacy_requester is None]
        if potential_partners:
            chosen_partner = random.choice(potential_partners)
            
            # "Invia" la richiesta al partner
            chosen_partner.pending_intimacy_requester = npc
            if DEBUG_AI: logger.debug(f"AI Decision ({npc.name}): Inviata richiesta di intimità a {chosen_partner.name}.")

            # L'NPC iniziatore si muove vicino al partner
            # Calcola un punto vicino al partner (davanti, di lato, ecc.)
            # Questo dovrebbe essere un punto camminabile
            interaction_offset_x = random.choice([-config.TILE_SIZE, config.TILE_SIZE]) 
            target_pos_world_for_meeting = (chosen_partner.rect.centerx + interaction_offset_x, chosen_partner.rect.centery)
            
            path_to_meet_partner = game_utils.find_path_to_target(npc, target_pos_world_for_meeting, pf_grid, game_state.world_objects_list)
            if path_to_meet_partner:
                npc.target_partner = chosen_partner # Imposta il partner target SOLO se può iniziare ad andare
                npc.current_action_before_movement = "seeking_partner_for_intimacy"
                npc.current_action = "moving_to_target"
                npc.target_destination = target_pos_world_for_meeting
                npc.current_path = path_to_meet_partner
                npc.previous_action_was_movement_to_target = True
                if DEBUG_AI: logger.debug(f"AI Decision ({npc.name}): Path trovato per incontrare {chosen_partner.name} per intimità.")
                return
            else:
                if DEBUG_AI: logger.warning(f"AI WARN ({npc.name}): No path to meet partner {chosen_partner.name}. Annullamento richiesta.")
                chosen_partner.pending_intimacy_requester = None # Annulla la richiesta
        elif DEBUG_AI:
            logger.info(f"AI INFO ({npc.name}): Bisogno di intimità, ma nessun partner idle/disponibile trovato.")
            
    # Socialità (Telefonare)
    if npc.social.get_value() < config.NPC_SOCIAL_THRESHOLD and npc.current_action == "idle":
        if DEBUG_AI: logger.debug(f"AI Decision ({npc.name}): Bisogno Social basso ({npc.social.get_value():.1f}). Inizio 'phoning'.")
        npc.current_action = "phoning"
        npc.is_interacting = True # L'azione "phoning" è un'interazione
        npc.time_in_current_action = 0.0 # Resetta il timer per la nuova azione
        return

    # TODO: Aggiungere decisioni per Divertimento e Igiene qui, se non c'è nulla di più urgente

    # --- Fallback: Wandering ---
    if random.random() < getattr(config, 'NPC_IDLE_WANDER_CHANCE', 0.02) and npc.current_action == "idle":
        # La logica di wandering è già in npc_behavior.py,
        # potremmo chiamare una funzione da wandering.py per ottenere la destinazione
        # o implementarla qui.
        # from .wandering import decide_wander_destination
        # target_wander_pos = decide_wander_destination(npc, pf_grid, game_state)
        target_wander_pos = game_utils.get_random_walkable_tile_in_radius(
            npc.rect.center, pf_grid,
            min_dist_tiles=getattr(config, 'NPC_WANDER_MIN_DIST_TILES', 3),
            max_dist_tiles=getattr(config, 'NPC_WANDER_MAX_DIST_TILES', 8),
            # world_obstacles non è usato da get_random_walkable_tile_in_radius
        )

        if target_wander_pos:
            path_to_wander = game_utils.find_path_to_target(npc, target_wander_pos, pf_grid, game_state.world_objects_list)
            if path_to_wander:
                if DEBUG_AI: logger.debug(f"AI Decision ({npc.name}): Wandering verso {target_wander_pos} (griglia: {game_utils.world_to_grid(target_wander_pos[0], target_wander_pos[1])}).")
                npc.current_action_before_movement = "wandering"
                npc.current_action = "moving_to_target"
                npc.target_destination = target_wander_pos
                npc.current_path = path_to_wander
                npc.previous_action_was_movement_to_target = True
                return
            elif DEBUG_AI:
                logger.debug(f"AI Decision ({npc.name}): Voleva fare wandering verso {target_wander_pos} ma nessun path trovato.")
        elif DEBUG_AI:
            logger.debug(f"AI Decision ({npc.name}): Voleva fare wandering ma nessun target valido trovato.")

    # Se nessuna decisione è stata presa, l'NPC rimane "idle"
    if npc.current_action == "idle" and DEBUG_AI:
        logger.debug(f"AI Decision ({npc.name}): Nessuna azione urgente, rimane idle.")

def update_post_interaction_idle(npc: 'Character', game_state: 'GameState', hours_passed_this_tick: float) -> bool:
    """
    Gestisce la breve pausa "post_intimacy_idle".
    Restituisce True se l'azione è ancora in corso, False se è terminata.
    """
    post_interaction_idle_duration = getattr(config, 'POST_INTIMACY_IDLE_DURATION_HOURS', 0.1)
    npc.time_in_current_action += hours_passed_this_tick
    
    if npc.time_in_current_action >= post_interaction_idle_duration:
        if DEBUG_AI: logger.debug(f"AI ({npc.name}): Terminato 'post_intimacy_idle'. Ritorno a idle.")
        npc.current_action = "idle"
        npc.time_in_current_action = 0.0
        return False # Azione terminata
    else:
        if DEBUG_AI: logger.debug(f"AI ({npc.name}): In 'post_intimacy_idle'. Timer: {npc.time_in_current_action:.2f}/{post_interaction_idle_duration:.2f}")
        return True # Azione ancora in corso