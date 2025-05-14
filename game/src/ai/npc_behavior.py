# simai/game/src/ai/npc_behavior.py
# MODIFIED: NPC now moves to interaction point of their bed slot upon waking up.
# MODIFIED: Implemented bed slot logic for seeking_bed and arrival.
# MODIFIED: Temporarily disable 'seeking_toilet', 'seeking_food', 'phoning' decisions.
# MODIFIED: Made AI debug prints conditional on config.DEBUG_AI_ACTIVE
# MODIFIED: Removed Fallback logic, critical imports will sys.exit().
# MODIFIED: Used config alias for config module.

import math
import random 
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from pathfinding.core.diagonal_movement import DiagonalMovement
import pygame
import sys # Aggiunto per sys.exit()

try:
    from game import config 
    from game import game_utils
    from game.main import GameState
except ImportError as e:
    print(f"CRITICAL ERROR (npc_behavior.py): Could not import 'game.config' or 'game.game_utils': {e}")
    print("Ensure 'game.config' and 'game.game_utils' are accessible in your PYTHONPATH.")
    sys.exit()

def _find_walkable_adjacent_target_grid_coords(obj_rect: pygame.Rect, npc_x: float, npc_y: float, grid_matrix_ref: list) -> tuple | None:
    if not obj_rect:
        return None

    obj_gx_min, obj_gy_min = game_utils.world_to_grid(obj_rect.left, obj_rect.top)
    obj_gx_max, obj_gy_max = game_utils.world_to_grid(obj_rect.right - 1, obj_rect.bottom - 1)
    
    potential_targets_grid = []
    if obj_gy_min > 0:
        for gx_candidate in range(obj_gx_min, obj_gx_max + 1):
            potential_targets_grid.append((gx_candidate, obj_gy_min - 1))
    if obj_gy_max < config.GRID_HEIGHT - 1:
        for gx_candidate in range(obj_gx_min, obj_gx_max + 1):
            potential_targets_grid.append((gx_candidate, obj_gy_max + 1))
    if obj_gx_min > 0:
        for gy_candidate in range(obj_gy_min, obj_gy_max + 1):
            potential_targets_grid.append((obj_gx_min - 1, gy_candidate))
    if obj_gx_max < config.GRID_WIDTH - 1:
        for gy_candidate in range(obj_gy_min, obj_gy_max + 1):
            potential_targets_grid.append((obj_gx_max + 1, gy_candidate))
    
    valid_targets_grid_coords = []
    for pt_gx, pt_gy in potential_targets_grid:
        if (0 <= pt_gy < config.GRID_HEIGHT and
            0 <= pt_gx < config.GRID_WIDTH and
            grid_matrix_ref[pt_gy][pt_gx] == 1): 
            valid_targets_grid_coords.append((pt_gx, pt_gy))
    
    if not valid_targets_grid_coords:
        return None

    npc_gx, npc_gy = game_utils.world_to_grid(npc_x, npc_y)
    valid_targets_grid_coords.sort(key=lambda pos: math.sqrt((pos[0]-npc_gx)**2 + (pos[1]-npc_gy)**2))
    
    return valid_targets_grid_coords[0]


def run_npc_ai_logic(npc, all_characters_list: list, game_hours_advanced: float, 
                     grid_matrix_ref: list, current_food_visible: bool,
                     food_pos_tuple: tuple, 
                     game_state_ref: GameState, # Corretto come tipo
                     toilet_rect_obj: pygame.Rect = None, # Questo è l'ottavo parametro
                     fun_object_rect_obj: pygame.Rect = None, 
                     shower_rect_obj: pygame.Rect = None 
                     ):
    food_eaten_by_this_npc = False
    bed_rect_obj = game_state_ref.bed_rect # Questa riga causava l'errore se game_state_ref era già un Rect
    
    DEBUG_AI = getattr(config, 'DEBUG_AI_ACTIVE', False) # Leggi il flag di debug

    # Section 0: Handle Blocking/Continuous Actions
    if npc.current_action == "resting_on_bed":
        if npc.energy.get_value() >= npc.energy.max_value:
            # NPC si sveglia, libera lo slot e si sposta al punto di interazione
            woke_up_from_slot = None
            if game_state_ref.bed_slot_1_occupied_by == npc.uuid:
                game_state_ref.bed_slot_1_occupied_by = None
                woke_up_from_slot = 1
                if game_state_ref.bed_slot_1_interaction_pos_world:
                    npc.x, npc.y = game_state_ref.bed_slot_1_interaction_pos_world
                    npc.rect.center = (int(npc.x), int(npc.y)) # Aggiorna il rect
                if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Left bed slot 1. Moved to interaction point.")
            elif game_state_ref.bed_slot_2_occupied_by == npc.uuid:
                game_state_ref.bed_slot_2_occupied_by = None
                woke_up_from_slot = 2
                if game_state_ref.bed_slot_2_interaction_pos_world:
                    npc.x, npc.y = game_state_ref.bed_slot_2_interaction_pos_world
                    npc.rect.center = (int(npc.x), int(npc.y)) # Aggiorna il rect
                if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Left bed slot 2. Moved to interaction point.")
            
            npc.current_action = "idle"
            npc.target_destination = None # Cancella ogni destinazione precedente
            npc.current_path = None
            npc.current_path_index = 0
            # Non è necessario fare pathfinding qui, l'NPC è già stato spostato.
            # L'animazione tornerà a idle in Character.update()
            if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Woke up, energy full. Action -> idle. Position: ({npc.x:.0f}, {npc.y:.0f})")
        return food_eaten_by_this_npc 
    elif npc.current_action == "phoning":
        if npc.social.get_value() >= npc.social.max_value: 
            npc.current_action = "idle"
            if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Finished phoning, social full. Action -> idle")
        return food_eaten_by_this_npc
    elif npc.current_action in ["romantic_interaction_action", "affectionate_interaction_action"]:
        if npc.time_in_current_action >= getattr(config, 'INTIMACY_INTERACTION_DURATION_HOURS', 1.0):
            npc.current_action = "idle"; npc.time_in_current_action = 0.0
            if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Finished intimacy interaction. Action -> idle")
        return food_eaten_by_this_npc
    elif npc.current_action == "using_toilet":
        if npc.time_in_current_action >= getattr(config, 'TOILET_USE_DURATION_HOURS', 0.25):
            npc.use_toilet(getattr(config, 'BLADDER_RELIEF_AMOUNT', 80)) 
            npc.current_action = "idle"
            npc.time_in_current_action = 0.0
            if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Finished using toilet. Bladder: {npc.bladder.get_value():.0f}. Action -> idle")
        return food_eaten_by_this_npc 
    
    # Section 1: Handle "Seeking Partner" logic
    if npc.current_action == "seeking_partner":
        if npc.target_partner:
            dist_to_partner = math.sqrt((npc.x - npc.target_partner.x)**2 + (npc.y - npc.target_partner.y)**2)
            if dist_to_partner < config.NPC_PARTNER_INTERACTION_DISTANCE:
                interaction_outcome_action = ""
                if random.random() < getattr(config, 'ROMANTIC_INTERACTION_CHANCE', 0.5): 
                    npc.satisfy_intimacy_drive(config.INTIMACY_SATISFACTION_ROMANTIC) 
                    npc.target_partner.satisfy_intimacy_drive(config.INTIMACY_SATISFACTION_ROMANTIC) 
                    interaction_outcome_action = "romantic_interaction_action" 
                    female_npc = npc if npc.gender=="female" else (npc.target_partner if npc.target_partner.gender=="female" else None)
                    if female_npc and not female_npc.is_pregnant:
                         if random.random() < getattr(config, 'PREGNANCY_CHANCE_FEMALE', 0.25):
                             if hasattr(female_npc, 'become_pregnant'): female_npc.become_pregnant()
                else:
                    npc.satisfy_intimacy_drive(config.INTIMACY_SATISFACTION_AFFECTIONATE) 
                    npc.social.satisfy(config.SOCIAL_SATISFACTION_AFFECTIONATE)         
                    npc.target_partner.satisfy_intimacy_drive(config.INTIMACY_SATISFACTION_AFFECTIONATE) 
                    npc.target_partner.social.satisfy(config.SOCIAL_SATISFACTION_AFFECTIONATE)       
                    interaction_outcome_action = "affectionate_interaction_action" 
                
                if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Interacted with {npc.target_partner.name}, outcome: {interaction_outcome_action}")
                npc.current_action = interaction_outcome_action; npc.time_in_current_action = 0.0
                npc.target_partner.current_action = interaction_outcome_action; npc.target_partner.time_in_current_action = 0.0
                if hasattr(npc.target_partner, 'target_partner'): npc.target_partner.target_partner = None 
                if hasattr(npc.target_partner, 'target_destination'): npc.target_partner.target_destination = None
                if hasattr(npc.target_partner, 'current_path'): npc.target_partner.current_path = None; npc.target_partner.current_path_index = 0
                npc.target_partner = None
        else: 
            npc.current_action = "idle"; npc.target_partner = None
            if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Was seeking partner, but target_partner is None. Action -> idle")
        npc.target_destination = None; npc.current_path = None; npc.current_path_index = 0
        return food_eaten_by_this_npc

    # Section 2: Interrupt A*-based Seeking Actions
    should_interrupt_astar_seek = False; action_being_checked = npc.current_action
    if action_being_checked == "seeking_food" and (not current_food_visible or npc.hunger.get_value() <= config.NPC_HUNGER_THRESHOLD * 0.5):
        should_interrupt_astar_seek = True
    elif action_being_checked == "seeking_bed" and npc.energy.get_value() >= config.NPC_ENERGY_THRESHOLD * 1.5:
        should_interrupt_astar_seek = True
    elif action_being_checked == "seeking_toilet" and npc.bladder.get_value() <= config.NPC_BLADDER_THRESHOLD * 0.5:
        should_interrupt_astar_seek = True
    # Aggiungi interruzioni per seeking_shower, seeking_fun_activity se necessario

    if should_interrupt_astar_seek:
        if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Interrupting '{action_being_checked}' due to changed conditions. Action -> idle")
        npc.current_action = "idle"; npc.target_destination = None; npc.current_path = None; npc.current_path_index = 0

    # Section 3: Handle Arrival at Destination for A* paths
    elif npc.current_path is None and npc.target_destination is None and \
        npc.current_action.startswith("seeking_bed_slot_"): # Modificato per slot specifici
        
        slot_id_being_sought = int(npc.current_action.split("_")[-1]) # Estrae 1 o 2
        
        target_sleep_pos = None
        if slot_id_being_sought == 1 and game_state_ref.bed_slot_1_interaction_pos_world:
            target_sleep_pos = game_state_ref.bed_slot_1_sleep_pos_world
        elif slot_id_being_sought == 2 and game_state_ref.bed_slot_2_interaction_pos_world:
            target_sleep_pos = game_state_ref.bed_slot_2_sleep_pos_world

        # Verifica se l'NPC è arrivato al punto di INTERAZIONE dello slot
        # Non usiamo più bed_rect_obj.center, ma la posizione target dello slot.
        # npc.target_object_interaction_pos dovrebbe essere stato impostato quando ha deciso lo slot
        # Se la logica di pathfinding porta alla cella ESATTA, non c'è bisogno di un check di distanza qui,
        # l'arrivo è implicito quando il path finisce.
        
        if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Arrived at interaction point for bed slot {slot_id_being_sought}.")
        
        can_use_slot = False
        if slot_id_being_sought == 1 and (game_state_ref.bed_slot_1_occupied_by is None or game_state_ref.bed_slot_1_occupied_by == npc.uuid):
            game_state_ref.bed_slot_1_occupied_by = npc.uuid
            can_use_slot = True
            if target_sleep_pos: npc.x, npc.y = target_sleep_pos # "Entra" nel letto
        elif slot_id_being_sought == 2 and (game_state_ref.bed_slot_2_occupied_by is None or game_state_ref.bed_slot_2_occupied_by == npc.uuid):
            game_state_ref.bed_slot_2_occupied_by = npc.uuid
            can_use_slot = True
            if target_sleep_pos: npc.x, npc.y = target_sleep_pos # "Entra" nel letto
        
        if can_use_slot:
            npc.current_action = "resting_on_bed"
            npc.target_destination = None # L'NPC è ora nel letto, non si muove
            npc.current_path = None
            npc.current_path_index = 0
            if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Action -> resting_on_bed in slot {slot_id_being_sought}. Positioned at {npc.x}, {npc.y}")
        else:
            if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Arrived at bed slot {slot_id_being_sought}, but it became occupied. Action -> idle")
            npc.current_action = "idle"
            # Resetta l'obiettivo dello slot se l'avevamo impostato sull'NPC
            if hasattr(npc, 'target_bed_slot_id'): npc.target_bed_slot_id = None
            
        npc.target_destination = None; npc.current_path = None; npc.current_path_index = 0 

    elif npc.current_path is None and npc.target_destination is None and \
         npc.current_action not in ["idle", "resting_on_bed", "phoning", 
                                   "romantic_interaction_action", "affectionate_interaction_action", 
                                   "seeking_partner", "using_toilet", 
                                   "using_shower", "using_fun_object"]: 
        action_at_arrival = npc.current_action
        npc.current_action = "idle" 
    elif npc.current_path is None and npc.target_destination is None and \
         not npc.current_action.startswith("seeking_bed_slot_") and \
         npc.current_action not in ["idle", "resting_on_bed", "phoning", 
                                   "romantic_interaction_action", "affectionate_interaction_action", 
                                   "seeking_partner", "using_toilet", 
                                   "using_shower", "using_fun_object"]:
        action_at_arrival = npc.current_action
        if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Path A* ended for generic action '{action_at_arrival}'. Setting action to idle.")
        npc.current_action = "idle"
        npc.target_destination = None; npc.current_path = None; npc.current_path_index = 0
        
        if action_at_arrival == "seeking_food":
            dist_to_food = math.sqrt((npc.x - food_pos_tuple[0])**2 + (npc.y - food_pos_tuple[1])**2)
            if current_food_visible and dist_to_food < config.NPC_EAT_REACH_DISTANCE:
                npc.eat(config.FOOD_VALUE)
                food_eaten_by_this_npc = True
                if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Ate food. Hunger: {npc.hunger.get_value():.0f}. Action -> idle")
        elif action_at_arrival == "seeking_bed": 
            dist_to_bed_center = math.sqrt((npc.x - bed_rect_obj.centerx)**2 + (npc.y - bed_rect_obj.centery)**2)
            if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Arrived at bed's area. Dist to bed center: {dist_to_bed_center:.1f}, Reach: {config.NPC_BED_REACH_DISTANCE}")
            if dist_to_bed_center < config.NPC_BED_REACH_DISTANCE: 
                npc.current_action = "resting_on_bed" 
                if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Action -> resting_on_bed")
        elif action_at_arrival == "seeking_toilet" and toilet_rect_obj: 
            target_center_wc = toilet_rect_obj.center 
            dist_to_wc_center = math.sqrt((npc.x - target_center_wc[0])**2 + (npc.y - target_center_wc[1])**2)
            if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Arrived near Toilet. Dist: {dist_to_wc_center:.1f}, Reach: {config.NPC_TOILET_REACH_DISTANCE}")
            if dist_to_wc_center < config.NPC_TOILET_REACH_DISTANCE: 
                npc.current_action = "using_toilet"; npc.time_in_current_action = 0.0 
                if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Action -> using_toilet")
            else:
                if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Reached toilet vicinity, but NOT close enough. Action -> idle")
                npc.current_action = "idle"
        # Aggiungi logica di arrivo per fun_object e shower qui...

        if npc.current_action not in ["resting_on_bed", "using_toilet"]: 
            npc.current_action = "idle" 
        npc.target_destination = None; npc.current_path = None; npc.current_path_index = 0 
        

    # Section 4: Decision Making (if NPC is "idle")
    if npc.current_action == "idle":
        if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Is idle. Evaluating needs...")
        target_grid_for_astar = None; action_after_astar = "idle"; chosen_partner_for_intimacy = None
        
        # Priority of needs
        # if npc.bladder.get_value() > config.NPC_BLADDER_THRESHOLD and toilet_rect_obj: # <--- COMMENTA QUESTA SEZIONE
        #     target_grid_for_astar = _find_walkable_adjacent_target_grid_coords(toilet_rect_obj, npc.x, npc.y, grid_matrix_ref)
        #     if target_grid_for_astar: 
        #         action_after_astar = "seeking_toilet"
        #     elif DEBUG_AI: 
        #         print(f"AI DEBUG ({npc.name}): Bladder high ({npc.bladder.get_value():.0f}), but no walkable adjacent spot for Toilet.")
        # elif npc.hunger.get_value() > config.NPC_HUNGER_THRESHOLD and current_food_visible: # <--- COMMENTA QUESTA SEZIONE
        #     food_gx, food_gy = game_utils.world_to_grid(food_pos_tuple[0], food_pos_tuple[1])
        #     if 0<=food_gy<config.GRID_HEIGHT and 0<=food_gx<config.GRID_WIDTH and grid_matrix_ref[food_gy][food_gx]==1: # Usa config
        #         target_grid_for_astar = (food_gx, food_gy); action_after_astar = "seeking_food"
        #     elif DEBUG_AI: print(f"AI DEBUG ({npc.name}): Hungry, but food target grid ({food_gx},{food_gy}) not walkable or out of bounds.")
        # Priorità: Energia / Letto
        if npc.energy.get_value() < config.NPC_ENERGY_THRESHOLD and bed_rect_obj:
            chosen_slot_interaction_pos = None
            chosen_slot_id = None
            # Controlla slot 1
            if game_state_ref.bed_slot_1_occupied_by is None and game_state_ref.bed_slot_1_interaction_pos_world:
                chosen_slot_interaction_pos = game_state_ref.bed_slot_1_interaction_pos_world
                chosen_slot_id = 1
            # Se slot 1 occupato o non valido, controlla slot 2
            elif game_state_ref.bed_slot_2_occupied_by is None and game_state_ref.bed_slot_2_interaction_pos_world:
                chosen_slot_interaction_pos = game_state_ref.bed_slot_2_interaction_pos_world
                chosen_slot_id = 2
            
            if chosen_slot_interaction_pos and chosen_slot_id:
                target_grid_for_astar = game_utils.world_to_grid(chosen_slot_interaction_pos[0], chosen_slot_interaction_pos[1])
                action_after_astar = f"seeking_bed_slot_{chosen_slot_id}"
                # Potresti voler "prenotare" lo slot qui se più NPC decidono contemporaneamente,
                # ma per ora, la verifica all'arrivo gestirà i conflitti.
                # npc.target_bed_slot_id = chosen_slot_id # Un attributo temporaneo sull'NPC
                if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Low energy. Decided -> {action_after_astar} to interaction point grid {target_grid_for_astar}")
            elif DEBUG_AI:
                print(f"AI DEBUG ({npc.name}): Low energy, but no free bed slot or interaction points not set.")
        elif npc.hygiene.get_value() < config.NPC_HYGIENE_THRESHOLD and shower_rect_obj:
            target_grid_for_astar = _find_walkable_adjacent_target_grid_coords(shower_rect_obj, npc.x, npc.y, grid_matrix_ref)
            if target_grid_for_astar: action_after_astar = "seeking_shower"
        elif npc.fun.get_value() < config.NPC_FUN_THRESHOLD and fun_object_rect_obj:
            target_grid_for_astar = _find_walkable_adjacent_target_grid_coords(fun_object_rect_obj, npc.x, npc.y, grid_matrix_ref)
            if target_grid_for_astar: action_after_astar = "seeking_fun_activity"

        if target_grid_for_astar is None and npc.current_action == "idle": 
            if npc.intimacy.get_value() > config.NPC_INTIMACY_THRESHOLD:
                chosen_partner_for_intimacy = None
                for char_partner_candidate in all_characters_list:
                    if char_partner_candidate is not npc and \
                       ((npc.gender == "male" and char_partner_candidate.gender == "female") or \
                        (npc.gender == "female" and char_partner_candidate.gender == "male")):
                        if char_partner_candidate.current_action in ["idle", "seeking_partner", "wandering"] or \
                           char_partner_candidate.intimacy.get_value() > config.NPC_INTIMACY_THRESHOLD * 0.4:
                           chosen_partner_for_intimacy = char_partner_candidate; break 
                if chosen_partner_for_intimacy:
                    npc.target_partner = chosen_partner_for_intimacy; npc.current_action = "seeking_partner"
                    if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Decided -> seeking_partner ({npc.target_partner.name})")
                    return food_eaten_by_this_npc 
            # elif npc.social.get_value() < config.NPC_SOCIAL_THRESHOLD:
            #     npc.current_action = "phoning"
            #     if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Decided -> phoning")
            #     return food_eaten_by_this_npc 
            elif random.random() < getattr(config, 'NPC_IDLE_WANDER_CHANCE', 0.02):
                angle = random.uniform(0, 2 * math.pi)
                dist_tiles = random.uniform(config.NPC_WANDER_MIN_DIST_TILES, config.NPC_WANDER_MAX_DIST_TILES)
                dist_pixels = dist_tiles * config.TILE_SIZE 
                wander_target_x = npc.x + math.cos(angle) * dist_pixels
                wander_target_y = npc.y + math.sin(angle) * dist_pixels
                half_width = (npc.frame_width / 2) if npc.frame_width > 0 else getattr(npc, 'fallback_radius', 15)
                half_height = (npc.frame_height / 2) if npc.frame_height > 0 else getattr(npc, 'fallback_radius', 15)
                wander_target_x = max(half_width, min(wander_target_x, config.SCREEN_WIDTH - half_width))
                wander_target_y = max(half_height, min(wander_target_y, config.SCREEN_HEIGHT - half_height))
                wander_gx, wander_gy = game_utils.world_to_grid(wander_target_x, wander_target_y)
                if 0<=wander_gy<config.GRID_HEIGHT and 0<=wander_gx<config.GRID_WIDTH and grid_matrix_ref[wander_gy][wander_gx]==1:
                    target_grid_for_astar = (wander_gx, wander_gy); action_after_astar = "wandering"
                    # if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Decided -> wandering to grid ({wander_gx},{wander_gy})") # Può essere molto verboso

        if target_grid_for_astar:
            if DEBUG_AI and action_after_astar != "wandering": # Non stampare per ogni decisione di wandering
                 target_world_pos_for_print = game_utils.grid_to_world_center(target_grid_for_astar[0], target_grid_for_astar[1])
                 print(f"AI DEBUG ({npc.name}): Decided -> {action_after_astar} to grid {target_grid_for_astar} (world approx {target_world_pos_for_print})")
            
            start_gx, start_gy = game_utils.world_to_grid(npc.x, npc.y)
            end_gx, end_gy = target_grid_for_astar[0], target_grid_for_astar[1] 
            start_walkable = (0 <= start_gy < config.GRID_HEIGHT and 0 <= start_gx < config.GRID_WIDTH and grid_matrix_ref[start_gy][start_gx] == 1)
            end_walkable = (0 <= end_gy < config.GRID_HEIGHT and 0 <= end_gx < config.GRID_WIDTH and grid_matrix_ref[end_gy][end_gx] == 1)
            
            if start_walkable and end_walkable:
                grid_obj_pf = Grid(matrix=grid_matrix_ref)
                start_node = grid_obj_pf.node(start_gx, start_gy)
                end_node = grid_obj_pf.node(end_gx, end_gy)
                finder = AStarFinder(diagonal_movement=DiagonalMovement.always) 
                try:
                     path, runs = finder.find_path(start_node, end_node, grid_obj_pf)
                     if path and len(path) > 1: 
                        npc.current_path = path
                        npc.current_path_index = 0 # Inizierà dal primo (e forse unico) nodo
                        npc.current_action = action_after_astar
                        npc.target_destination = None # Verrà impostato da Character.update
                        if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Path found for '{action_after_astar}'. Length: {len(path)}")
                     else: 
                        npc.current_action = "idle"; npc.current_path = None; npc.current_path_index = 0
                        if DEBUG_AI:
                            if not path: print(f"AI DEBUG ({npc.name}): No path found for '{action_after_astar}' to ({end_gx},{end_gy}).")
                            #  elif len(path) <= 1: print(f"AI DEBUG ({npc.name}): Path too short for '{action_after_astar}' to ({end_gx},{end_gy}).")
                except Exception as e_astar: 
                    if DEBUG_AI: print(f"AI ERROR ({npc.name}): A* pathfinding failed for '{action_after_astar}': {e_astar}")
                    npc.current_action = "idle"; npc.current_path = None; npc.current_path_index = 0
            else: 
                if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Cannot start A* for '{action_after_astar}'. Start S:({start_gx},{start_gy}) W:{start_walkable} or End E:({end_gx},{end_gy}) W:{end_walkable} is not walkable.")
                npc.current_action = "idle"; npc.current_path = None; npc.current_path_index = 0
                 
    return food_eaten_by_this_npc