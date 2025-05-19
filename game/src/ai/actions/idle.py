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
    if not hasattr(npc, 'needs') or not npc.needs:
        if DEBUG_AI:
            logger.warning(f"AI Decision ({npc.name}): NeedsComponent non trovato o non inizializzato. Impossibile prendere decisioni basate sui bisogni.")
        return # Non può fare nulla senza bisogni

    if DEBUG_AI:
        logger.debug(f"AI Decision ({npc.name}): In idle. Valutazione bisogni...")
        # Accesso corretto ai bisogni tramite npc.needs.NOME_BISOGNO
        if hasattr(npc.needs, 'energy'):
            logger.debug(f"AI Decision ({npc.name}): Energia: {npc.needs.energy.get_value():.1f}/{npc.needs.energy.max_value:.0f} (Soglia: {config.NPC_ENERGY_THRESHOLD})")
        if hasattr(npc.needs, 'hunger'):
            logger.debug(f"AI Decision ({npc.name}): Fame: {npc.needs.hunger.get_value():.1f}/{npc.needs.hunger.max_value:.0f} (Soglia: {config.NPC_HUNGER_THRESHOLD})")
        if hasattr(npc.needs, 'bladder'):
            logger.debug(f"AI Decision ({npc.name}): Vescica: {npc.needs.bladder.get_value():.1f}/{npc.needs.bladder.max_value:.0f} (Soglia: {config.NPC_BLADDER_THRESHOLD})")
        if hasattr(npc.needs, 'social'):
            logger.debug(f"AI Decision ({npc.name}): Social: {npc.needs.social.get_value():.1f}/{npc.needs.social.max_value:.0f} (Soglia: {config.NPC_SOCIAL_THRESHOLD})")
        if hasattr(npc.needs, 'intimacy'):
            logger.debug(f"AI Decision ({npc.name}): Intimità: {npc.needs.intimacy.get_value():.1f}/{npc.needs.intimacy.max_value:.0f} (Soglia Richiesta: {config.NPC_INTIMACY_THRESHOLD})")
        if hasattr(npc.needs, 'fun'):
            logger.debug(f"AI Decision ({npc.name}): Divertimento: {npc.needs.fun.get_value():.1f}/{npc.needs.fun.max_value:.0f} (Soglia: {config.NPC_FUN_THRESHOLD})")
        if hasattr(npc.needs, 'hygiene'):
            logger.debug(f"AI Decision ({npc.name}): Igiene: {npc.needs.hygiene.get_value():.1f}/{npc.needs.hygiene.max_value:.0f} (Soglia: {config.NPC_HYGIENE_THRESHOLD})")


    # --- Priorità 1: Bisogni Critici ---
    # Energia / Sonno
    if hasattr(npc.needs, 'energy') and npc.needs.energy.get_value() < config.NPC_ENERGY_THRESHOLD:
        if DEBUG_AI: logger.debug(f"AI Decision ({npc.name}): Energia bassa ({npc.needs.energy.get_value():.1f}). Cerco letto.")
        
        bed_interaction_pos = None
        chosen_slot_index = -1

        if game_state.bed_slot_1_interaction_pos_world and not game_state.bed_slot_1_occupied_by:
            bed_interaction_pos = game_state.bed_slot_1_interaction_pos_world
            chosen_slot_index = 0
            if DEBUG_AI: logger.debug(f"AI Decision ({npc.name}): Slot 0 letto disponibile a {bed_interaction_pos}.")
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
                npc.bed_slot_index = chosen_slot_index 
                npc.previous_action_was_movement_to_target = True
                return
            else:
                if DEBUG_AI: logger.warning(f"AI WARN ({npc.name}): No path to bed slot {chosen_slot_index} at {bed_interaction_pos_int}.")
        elif DEBUG_AI:
            logger.info(f"AI INFO ({npc.name}): Energia bassa, ma nessun letto libero o posizioni letto non definite.")
    
    # Bisogno Vescica (Bladder) - Ricorda che per Bladder, alto è buono (sollievo), quindi se scende SOTTO la soglia, agisci.
    # La tua config dice: NPC_BLADDER_THRESHOLD = 25
    # La tua logica in idle.py era: npc.bladder.get_value() > config.NPC_BLADDER_THRESHOLD
    # Questo è INVERSO se alto è buono. Se il valore (sollievo) è ALTO, non deve andare in bagno.
    # Deve andare se il valore di sollievo è BASSO.
    if hasattr(npc.needs, 'bladder') and npc.needs.bladder.get_value() < config.NPC_BLADDER_THRESHOLD: # CORRETTO: se sollievo è BASSO
        if DEBUG_AI: logger.debug(f"AI Decision ({npc.name}): Sollievo vescica basso ({npc.needs.bladder.get_value():.1f}). Cerco bagno.")
        if game_state.toilet_rect_instance:
            interaction_x = game_state.toilet_rect_instance.centerx
            interaction_y = game_state.toilet_rect_instance.bottom + config.TILE_SIZE // 2 
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
            logger.info(f"AI INFO ({npc.name}): Sollievo vescica basso, ma nessun bagno definito in game_state.")

    # Fame (Hunger) - Ricorda che per Hunger, alto è buono (sazio), quindi se scende SOTTO la soglia, agisci.
    if hasattr(npc.needs, 'hunger') and npc.needs.hunger.get_value() < config.NPC_HUNGER_THRESHOLD:
        if DEBUG_AI: logger.debug(f"AI Decision ({npc.name}): Sazietà bassa ({npc.needs.hunger.get_value():.1f}). Cerco cibo.")
        # TODO: Implementare la logica per cercare e mangiare cibo
        # Esempio:
        # food_location = game_utils.find_food_source(game_state, npc)
        # if food_location:
        #     path_to_food = game_utils.find_path_to_target(npc, food_location, pf_grid, game_state.world_objects_list)
        #     if path_to_food:
        #         npc.current_action_before_movement = "seeking_food"
        #         # ... imposta target e path ...
        #         return
        pass # Placeholder per la logica del cibo


    # --- Priorità 2: Bisogni Sociali/Intimità (se non critici) ---
    if npc.pending_intimacy_requester and npc.current_action == "idle": 
        partner_candidate = npc.pending_intimacy_requester
        if DEBUG_AI: logger.debug(f"AI Decision ({npc.name}): Ricevuta richiesta di intimità da {partner_candidate.name}. Accetto e attendo.")
        npc.current_action = "accepting_intimacy_and_waiting"
        npc.target_partner = partner_candidate
        npc.target_destination = None
        npc.current_path = None
        npc.is_interacting = True
        npc.pending_intimacy_requester = None 
        return 

    # Intimità - Ricorda che per Intimacy, alto è buono (soddisfazione), quindi se scende SOTTO la soglia, agisci.
    # La tua config dice: NPC_INTIMACY_THRESHOLD = 35
    # La tua logica in idle.py era: npc.intimacy.get_value() > config.NPC_INTIMACY_THRESHOLD
    # Questo è INVERSO se alto è buono. Se il valore (soddisfazione) è ALTO, non ha bisogno di intimità.
    # Deve agire se la soddisfazione è BASSA.
    if hasattr(npc.needs, 'intimacy') and npc.needs.intimacy.get_value() < config.NPC_INTIMACY_THRESHOLD and \
       len(all_npcs) > 1 and npc.current_action == "idle": 
        if DEBUG_AI: logger.debug(f"AI Decision ({npc.name}): Soddisfazione intimità bassa ({npc.needs.intimacy.get_value():.1f}). Cerco partner idle.")
        
        potential_partners = [p for p in all_npcs if p.uuid != npc.uuid and p.current_action == "idle" and p.pending_intimacy_requester is None]
        if potential_partners:
            chosen_partner = random.choice(potential_partners)
            
            chosen_partner.pending_intimacy_requester = npc
            if DEBUG_AI: logger.debug(f"AI Decision ({npc.name}): Inviata richiesta di intimità a {chosen_partner.name}.")

            interaction_offset_x = random.choice([-config.TILE_SIZE, config.TILE_SIZE]) 
            target_pos_world_for_meeting = (chosen_partner.rect.centerx + interaction_offset_x, chosen_partner.rect.centery)
            
            path_to_meet_partner = game_utils.find_path_to_target(npc, target_pos_world_for_meeting, pf_grid, game_state.world_objects_list)
            if path_to_meet_partner:
                npc.target_partner = chosen_partner 
                npc.current_action_before_movement = "seeking_partner_for_intimacy"
                npc.current_action = "moving_to_target"
                npc.target_destination = target_pos_world_for_meeting
                npc.current_path = path_to_meet_partner
                npc.previous_action_was_movement_to_target = True
                if DEBUG_AI: logger.debug(f"AI Decision ({npc.name}): Path trovato per incontrare {chosen_partner.name} per intimità.")
                return
            else:
                if DEBUG_AI: logger.warning(f"AI WARN ({npc.name}): No path to meet partner {chosen_partner.name}. Annullamento richiesta.")
                chosen_partner.pending_intimacy_requester = None 
        elif DEBUG_AI:
            logger.info(f"AI INFO ({npc.name}): Soddisfazione intimità bassa, ma nessun partner idle/disponibile trovato.")
            
    # Socialità (Telefonare)
    if hasattr(npc.needs, 'social') and npc.needs.social.get_value() < config.NPC_SOCIAL_THRESHOLD and npc.current_action == "idle":
        if DEBUG_AI: logger.debug(f"AI Decision ({npc.name}): Bisogno Social basso ({npc.needs.social.get_value():.1f}). Inizio 'phoning'.")
        npc.current_action = "phoning"
        npc.is_interacting = True 
        npc.time_in_current_action = 0.0 
        return

    # Divertimento (Fun)
    if hasattr(npc.needs, 'fun') and npc.needs.fun.get_value() < config.NPC_FUN_THRESHOLD and npc.current_action == "idle":
        if DEBUG_AI: logger.debug(f"AI Decision ({npc.name}): Divertimento basso ({npc.needs.fun.get_value():.1f}). Cerco attività divertente.")
        # TODO: Implementare la logica per cercare un'attività divertente
        # Esempio:
        # fun_activity_location = game_utils.find_fun_activity(game_state, npc)
        # if fun_activity_location:
        #     # ... vai all'attività ...
        #     return
        pass # Placeholder

    # Igiene (Hygiene)
    if hasattr(npc.needs, 'hygiene') and npc.needs.hygiene.get_value() < config.NPC_HYGIENE_THRESHOLD and npc.current_action == "idle":
        if DEBUG_AI: logger.debug(f"AI Decision ({npc.name}): Igiene bassa ({npc.needs.hygiene.get_value():.1f}). Cerco doccia/lavandino.")
        # TODO: Implementare la logica per cercare doccia/lavandino
        # Esempio:
        # hygiene_station_location = game_utils.find_hygiene_station(game_state, npc)
        # if hygiene_station_location:
        #     # ... vai alla stazione di igiene ...
        #     return
        pass # Placeholder


    # --- Fallback: Wandering ---
    if random.random() < getattr(config, 'NPC_IDLE_WANDER_CHANCE', 0.02) and npc.current_action == "idle":
        target_wander_pos = game_utils.get_random_walkable_tile_in_radius(
            npc.rect.center, pf_grid,
            min_dist_tiles=getattr(config, 'NPC_WANDER_MIN_DIST_TILES', 3),
            max_dist_tiles=getattr(config, 'NPC_WANDER_MAX_DIST_TILES', 8),
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
        return False 
    else:
        if DEBUG_AI: logger.debug(f"AI ({npc.name}): In 'post_intimacy_idle'. Timer: {npc.time_in_current_action:.2f}/{post_interaction_idle_duration:.2f}")
        return True