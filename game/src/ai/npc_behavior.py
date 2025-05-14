# simai/game/src/ai/npc_behavior.py
# MODIFIED: Refactored run_npc_ai_logic into private helper functions.
# (Assumes previous fixes for bed logic, conditional prints, and imports are in place)

import math
import random 
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from pathfinding.core.diagonal_movement import DiagonalMovement
import pygame
import sys 

try:
    from game import config as game_config
    from game import game_utils
    from game.main import GameState # Per il type hinting
    # Non importiamo Character direttamente per evitare potenziali import circolari
except ImportError as e:
    print(f"CRITICAL ERROR (npc_behavior.py): Could not import dependencies: {e}")
    sys.exit()

DEBUG_AI = getattr(game_config, 'DEBUG_AI_ACTIVE', False)

# --- Funzione Helper per Pathfinding (già esistente) ---
def _find_walkable_adjacent_target_grid_coords(obj_rect: pygame.Rect, npc_x: float, npc_y: float, grid_matrix_ref: list) -> tuple | None:
    if not obj_rect: return None
    obj_gx_min, obj_gy_min = game_utils.world_to_grid(obj_rect.left, obj_rect.top)
    obj_gx_max, obj_gy_max = game_utils.world_to_grid(obj_rect.right - 1, obj_rect.bottom - 1)
    potential_targets_grid = []
    if obj_gy_min > 0:
        for gx_candidate in range(obj_gx_min, obj_gx_max + 1): potential_targets_grid.append((gx_candidate, obj_gy_min - 1))
    if obj_gy_max < game_config.GRID_HEIGHT - 1:
        for gx_candidate in range(obj_gx_min, obj_gx_max + 1): potential_targets_grid.append((gx_candidate, obj_gy_max + 1))
    if obj_gx_min > 0:
        for gy_candidate in range(obj_gy_min, obj_gy_max + 1): potential_targets_grid.append((obj_gx_min - 1, gy_candidate))
    if obj_gx_max < game_config.GRID_WIDTH - 1:
        for gy_candidate in range(obj_gy_min, obj_gy_max + 1): potential_targets_grid.append((obj_gx_max + 1, gy_candidate))
    valid_targets_grid_coords = []
    for pt_gx, pt_gy in potential_targets_grid:
        if (0 <= pt_gy < game_config.GRID_HEIGHT and 0 <= pt_gx < game_config.GRID_WIDTH and grid_matrix_ref[pt_gy][pt_gx] == 1): 
            valid_targets_grid_coords.append((pt_gx, pt_gy))
    if not valid_targets_grid_coords: return None
    npc_gx, npc_gy = game_utils.world_to_grid(npc_x, npc_y)
    valid_targets_grid_coords.sort(key=lambda pos: math.sqrt((pos[0]-npc_gx)**2 + (pos[1]-npc_gy)**2))
    return valid_targets_grid_coords[0]

# --- Sezione 0: Gestione Azioni Bloccanti/Continue ---
def _handle_continuous_actions(npc: 'Character', game_state_ref: GameState) -> bool | None:
    """
    Gestisce azioni che bloccano altre decisioni finché non sono completate.
    Restituisce True/False (per food_eaten, anche se attualmente sempre False qui) se l'NPC era in un'azione
    bloccante gestita e il turno IA per questo NPC è concluso.
    Restituisce None se l'NPC non era in un'azione bloccante rilevante, permettendo alla logica IA di procedere.
    """
    food_eaten_this_tick = False 

    if npc.current_action == "resting_on_bed":
        if npc.energy.get_value() >= npc.energy.max_value: 
            woke_up_from_slot_id = None
            interaction_pos_on_wakeup = None
            if game_state_ref.bed_slot_1_occupied_by == npc.uuid:
                game_state_ref.bed_slot_1_occupied_by = None
                woke_up_from_slot_id = 1
                interaction_pos_on_wakeup = game_state_ref.bed_slot_1_interaction_pos_world
                if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Woke up, leaving bed slot 1.")
            elif game_state_ref.bed_slot_2_occupied_by == npc.uuid:
                game_state_ref.bed_slot_2_occupied_by = None
                woke_up_from_slot_id = 2
                interaction_pos_on_wakeup = game_state_ref.bed_slot_2_interaction_pos_world
                if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Woke up, leaving bed slot 2.")
            
            npc.target_bed_slot_id = None
            npc.current_action = "idle"
            npc.target_destination = None; npc.current_path = None; npc.current_path_index = 0
            if interaction_pos_on_wakeup:
                npc.x, npc.y = interaction_pos_on_wakeup
                npc.rect.center = (int(npc.x), int(npc.y))
                if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Moved to IP {interaction_pos_on_wakeup} after waking. Action -> idle.")
            elif DEBUG_AI: print(f"AI DEBUG ({npc.name}): Woke up, no IP for slot {woke_up_from_slot_id}. Staying. Action -> idle.")
        return food_eaten_this_tick 

    elif npc.current_action == "phoning": 
        if npc.social.get_value() >= npc.social.max_value: 
            npc.current_action = "idle"
            if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Finished phoning. Action -> idle")
        return food_eaten_this_tick

    elif npc.current_action in ["romantic_interaction_action", "affectionate_interaction_action"]:
        if npc.time_in_current_action >= getattr(game_config, 'INTIMACY_INTERACTION_DURATION_HOURS', 1.0):
            npc.current_action = "idle"; npc.time_in_current_action = 0.0
            if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Finished intimacy interaction. Action -> idle")
        return food_eaten_this_tick

    elif npc.current_action == "using_toilet": 
        if npc.time_in_current_action >= getattr(game_config, 'TOILET_USE_DURATION_HOURS', 0.25):
            npc.use_toilet(getattr(game_config, 'BLADDER_RELIEF_AMOUNT', 80)) 
            npc.current_action = "idle"; npc.time_in_current_action = 0.0
            if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Finished using toilet. Bladder: {npc.bladder.get_value():.0f}. Action -> idle")
        return food_eaten_this_tick
    
    return None # Nessuna azione bloccante rilevante

# --- Sezione 1: Gestione "Seeking Partner" ---
def _handle_partner_seeking(npc: 'Character', all_characters_list: list, game_state_ref: GameState) -> bool | None:
    food_eaten_this_tick = False
    if npc.current_action == "seeking_partner":
        if npc.target_partner:
            dist_to_partner = math.sqrt((npc.x - npc.target_partner.x)**2 + (npc.y - npc.target_partner.y)**2)
            if dist_to_partner < game_config.NPC_PARTNER_INTERACTION_DISTANCE:
                interaction_outcome_action = ""
                if random.random() < getattr(game_config, 'ROMANTIC_INTERACTION_CHANCE', 0.5): 
                    npc.satisfy_intimacy_drive(game_config.INTIMACY_SATISFACTION_ROMANTIC) 
                    if npc.target_partner: npc.target_partner.satisfy_intimacy_drive(game_config.INTIMACY_SATISFACTION_ROMANTIC) 
                    interaction_outcome_action = "romantic_interaction_action" 
                    female_npc = npc if npc.gender=="female" else (npc.target_partner if npc.target_partner and npc.target_partner.gender=="female" else None)
                    if female_npc and not female_npc.is_pregnant:
                         if random.random() < getattr(game_config, 'PREGNANCY_CHANCE_FEMALE', 0.25):
                             if hasattr(female_npc, 'become_pregnant'): female_npc.become_pregnant()
                else:
                    npc.satisfy_intimacy_drive(game_config.INTIMACY_SATISFACTION_AFFECTIONATE) 
                    npc.social.satisfy(game_config.SOCIAL_SATISFACTION_AFFECTIONATE)         
                    if npc.target_partner:
                        npc.target_partner.satisfy_intimacy_drive(game_config.INTIMACY_SATISFACTION_AFFECTIONATE) 
                        npc.target_partner.social.satisfy(game_config.SOCIAL_SATISFACTION_AFFECTIONATE)       
                    interaction_outcome_action = "affectionate_interaction_action" 
                
                if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Interacted with {npc.target_partner.name if npc.target_partner else 'None'}, outcome: {interaction_outcome_action}")
                npc.current_action = interaction_outcome_action; npc.time_in_current_action = 0.0
                if npc.target_partner:
                    npc.target_partner.current_action = interaction_outcome_action; npc.target_partner.time_in_current_action = 0.0
                    if hasattr(npc.target_partner, 'target_partner'): npc.target_partner.target_partner = None 
                    if hasattr(npc.target_partner, 'target_destination'): npc.target_partner.target_destination = None
                    if hasattr(npc.target_partner, 'current_path'): npc.target_partner.current_path = None; npc.target_partner.current_path_index = 0
                npc.target_partner = None
        else: 
            npc.current_action = "idle"; npc.target_partner = None
            if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Was seeking partner, but target_partner is None. Action -> idle")
        npc.target_destination = None; npc.current_path = None; npc.current_path_index = 0
        return food_eaten_this_tick
    return None

# --- Sezione 2: Interruzione Azioni A* ---
def _check_and_handle_interruptions(npc: 'Character', current_food_visible: bool, game_state_ref: GameState) -> bool:
    should_interrupt = False
    action_being_checked = npc.current_action

    if action_being_checked == "seeking_food" and \
       (not current_food_visible or npc.hunger.get_value() <= game_config.NPC_HUNGER_THRESHOLD * 0.5):
        should_interrupt = True
    elif action_being_checked.startswith("seeking_bed_slot_"):
        slot_id = int(action_being_checked.split("_")[-1])
        is_my_slot_taken_by_another = False
        if slot_id == 1 and game_state_ref.bed_slot_1_occupied_by != npc.uuid and game_state_ref.bed_slot_1_occupied_by is not None:
            is_my_slot_taken_by_another = True
        elif slot_id == 2 and game_state_ref.bed_slot_2_occupied_by != npc.uuid and game_state_ref.bed_slot_2_occupied_by is not None:
            is_my_slot_taken_by_another = True
        if npc.energy.get_value() >= game_config.NPC_ENERGY_THRESHOLD * 1.1 or is_my_slot_taken_by_another:
            should_interrupt = True
            if DEBUG_AI and is_my_slot_taken_by_another: print(f"AI DEBUG ({npc.name}): Bed slot {slot_id} taken by another. Interrupting.")
    elif action_being_checked == "seeking_toilet" and \
         npc.bladder.get_value() <= game_config.NPC_BLADDER_THRESHOLD * 0.5:
        should_interrupt = True

    if should_interrupt:
        if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Interrupting '{action_being_checked}'. Action -> idle")
        if npc.target_bed_slot_id == 1 and game_state_ref.bed_slot_1_occupied_by == npc.uuid:
            game_state_ref.bed_slot_1_occupied_by = None
            if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Interrupted seeking_bed_slot_1, releasing reservation.")
        elif npc.target_bed_slot_id == 2 and game_state_ref.bed_slot_2_occupied_by == npc.uuid:
            game_state_ref.bed_slot_2_occupied_by = None
            if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Interrupted seeking_bed_slot_2, releasing reservation.")
        npc.target_bed_slot_id = None
        npc.current_action = "idle"; npc.target_destination = None; npc.current_path = None; npc.current_path_index = 0
        return True
    return False

# --- Sezione 3: Gestione Arrivo a Destinazione A* ---
def _handle_arrival_at_destination(npc: 'Character', game_state_ref: GameState, 
                                   current_food_visible: bool, food_pos_tuple: tuple,
                                   param_toilet_rect: pygame.Rect | None) -> bool | None:
    food_eaten_this_tick = False
    action_at_arrival = npc.current_action

    if npc.current_action.startswith("seeking_bed_slot_"):
        slot_id_being_sought = int(npc.current_action.split("_")[-1])
        target_sleep_position = game_state_ref.bed_slot_1_sleep_pos_world if slot_id_being_sought == 1 else game_state_ref.bed_slot_2_sleep_pos_world
        if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Reached IP for bed slot {slot_id_being_sought}.")
        can_use_slot = False
        if slot_id_being_sought == 1 and (game_state_ref.bed_slot_1_occupied_by is None or game_state_ref.bed_slot_1_occupied_by == npc.uuid):
            game_state_ref.bed_slot_1_occupied_by = npc.uuid; can_use_slot = True
            if target_sleep_position: npc.x, npc.y = target_sleep_position; npc.rect.center = (int(npc.x), int(npc.y))
        elif slot_id_being_sought == 2 and (game_state_ref.bed_slot_2_occupied_by is None or game_state_ref.bed_slot_2_occupied_by == npc.uuid):
            game_state_ref.bed_slot_2_occupied_by = npc.uuid; can_use_slot = True
            if target_sleep_position: npc.x, npc.y = target_sleep_position; npc.rect.center = (int(npc.x), int(npc.y))
        if can_use_slot:
            npc.current_action = "resting_on_bed"
            if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Action -> resting_on_bed in slot {slot_id_being_sought}. Pos: ({npc.x:.0f},{npc.y:.0f})")
        else:
            if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Arrived bed slot {slot_id_being_sought}, but occupied. Action -> idle")
            npc.current_action = "idle"; npc.target_bed_slot_id = None
        npc.target_destination = None; npc.current_path = None; npc.current_path_index = 0 
        return food_eaten_this_tick

    elif action_at_arrival == "seeking_food":
        dist_to_food = math.sqrt((npc.x - food_pos_tuple[0])**2 + (npc.y - food_pos_tuple[1])**2)
        if current_food_visible and dist_to_food < game_config.NPC_EAT_REACH_DISTANCE:
            npc.eat(game_config.FOOD_VALUE); food_eaten_this_tick = True
            if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Ate food. Hunger: {npc.hunger.get_value():.0f}. Action -> idle")
        else:
            if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Arrived for food, but not visible/too far. Dist: {dist_to_food:.1f}")
        npc.current_action = "idle"
    elif action_at_arrival == "seeking_toilet" and param_toilet_rect:
        target_center_wc = param_toilet_rect.center 
        dist_to_wc_center = math.sqrt((npc.x - target_center_wc[0])**2 + (npc.y - target_center_wc[1])**2)
        if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Arrived near Toilet. Dist: {dist_to_wc_center:.1f}, Reach: {game_config.NPC_TOILET_REACH_DISTANCE}")
        if dist_to_wc_center < game_config.NPC_TOILET_REACH_DISTANCE: 
            npc.current_action = "using_toilet"; npc.time_in_current_action = 0.0 
            if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Action -> using_toilet")
        else:
            if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Reached toilet vicinity, NOT close enough. Action -> idle")
            npc.current_action = "idle"
    else: 
        if DEBUG_AI and action_at_arrival not in ["idle", "wandering"]:
             print(f"AI DEBUG ({npc.name}): Path A* ended for '{action_at_arrival}'. Setting to idle.")
        npc.current_action = "idle"

    npc.target_destination = None; npc.current_path = None; npc.current_path_index = 0
    return food_eaten_this_tick

# --- Sezione 4: Logica Decisionale (quando Idle) ---
def _make_idle_decision(npc: 'Character', all_characters_list: list, grid_matrix_ref: list, 
                        current_food_visible: bool, food_pos_tuple: tuple, 
                        game_state_ref: GameState,
                        param_toilet_rect: pygame.Rect | None, 
                        param_fun_object_rect: pygame.Rect | None, 
                        param_shower_rect: pygame.Rect | None):
    if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Is idle. Evaluating needs...")
    target_grid_for_astar = None; action_after_astar = "idle"
    bed_rect_obj = game_state_ref.bed_rect

    if npc.energy.get_value() < game_config.NPC_ENERGY_THRESHOLD and bed_rect_obj:
        chosen_slot_interaction_pos = None; chosen_slot_id = None
        if game_state_ref.bed_slot_1_occupied_by is None and game_state_ref.bed_slot_1_interaction_pos_world:
            chosen_slot_interaction_pos = game_state_ref.bed_slot_1_interaction_pos_world; chosen_slot_id = 1
            game_state_ref.bed_slot_1_occupied_by = npc.uuid; npc.target_bed_slot_id = 1
            if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Low energy. Reserved bed slot 1.")
        elif game_state_ref.bed_slot_2_occupied_by is None and game_state_ref.bed_slot_2_interaction_pos_world:
            chosen_slot_interaction_pos = game_state_ref.bed_slot_2_interaction_pos_world; chosen_slot_id = 2
            game_state_ref.bed_slot_2_occupied_by = npc.uuid; npc.target_bed_slot_id = 2
            if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Low energy. Reserved bed slot 2.")
        if chosen_slot_interaction_pos and chosen_slot_id:
            target_grid_for_astar = game_utils.world_to_grid(chosen_slot_interaction_pos[0], chosen_slot_interaction_pos[1])
            action_after_astar = f"seeking_bed_slot_{chosen_slot_id}"
        elif DEBUG_AI:
            print(f"AI DEBUG ({npc.name}): Low energy, but all bed slots occupied/IP not set. "
                  f"S1: {game_state_ref.bed_slot_1_occupied_by}, S2: {game_state_ref.bed_slot_2_occupied_by}")
    
    # Altre decisioni per bisogni (attualmente commentate per food, toilet, phone)
    # if target_grid_for_astar is None and ... (logica per toilet)
    # if target_grid_for_astar is None and ... (logica per food)
    # ... (Hygiene, Fun)

    if target_grid_for_astar is None: 
        if npc.intimacy.get_value() > game_config.NPC_INTIMACY_THRESHOLD:
            chosen_partner_for_intimacy = None
            for char_candidate in all_characters_list:
                if char_candidate is not npc: chosen_partner_for_intimacy = char_candidate; break
            if chosen_partner_for_intimacy:
                npc.target_partner = chosen_partner_for_intimacy; npc.current_action = "seeking_partner"
                if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Decided -> seeking_partner ({npc.target_partner.name})")
                return # Azione immediata
        # elif npc.social.get_value() < game_config.NPC_SOCIAL_THRESHOLD: # Phoning disabilitato
            # npc.current_action = "phoning"; return
        else: 
            if random.random() < getattr(game_config, 'NPC_IDLE_WANDER_CHANCE', 0.02):
                angle=random.uniform(0,2*math.pi); dist_tiles=random.uniform(game_config.NPC_WANDER_MIN_DIST_TILES,game_config.NPC_WANDER_MAX_DIST_TILES)
                dist_px=dist_tiles*game_config.TILE_SIZE; wander_tx=npc.x+math.cos(angle)*dist_px; wander_ty=npc.y+math.sin(angle)*dist_px
                half_w=(npc.frame_width/2)if npc.frame_width>0 else 15; half_h=(npc.frame_height/2)if npc.frame_height>0 else 15
                wander_tx=max(half_w,min(wander_tx,game_config.SCREEN_WIDTH-half_w)); wander_ty=max(half_h,min(wander_ty,game_config.SCREEN_HEIGHT-half_h))
                wander_gx,wander_gy=game_utils.world_to_grid(wander_tx,wander_ty)
                if 0<=wander_gy<game_config.GRID_HEIGHT and 0<=wander_gx<game_config.GRID_WIDTH and grid_matrix_ref[wander_gy][wander_gx]==1:
                    target_grid_for_astar=(wander_gx,wander_gy); action_after_astar="wandering"
                    if DEBUG_AI:print(f"AI DEBUG ({npc.name}): Decided -> wandering to grid ({wander_gx},{wander_gy})")

    if target_grid_for_astar:
        if DEBUG_AI and action_after_astar != "wandering":
             target_world_pos_for_print = game_utils.grid_to_world_center(target_grid_for_astar[0], target_grid_for_astar[1])
             print(f"AI DEBUG ({npc.name}): Decided -> {action_after_astar} to grid {target_grid_for_astar} (world approx {target_world_pos_for_print})")
        start_gx, start_gy = game_utils.world_to_grid(npc.x, npc.y)
        end_gx, end_gy = target_grid_for_astar[0], target_grid_for_astar[1] 
        start_walkable = (0 <= start_gy < game_config.GRID_HEIGHT and 0 <= start_gx < game_config.GRID_WIDTH and grid_matrix_ref[start_gy][start_gx] == 1)
        end_walkable = (0 <= end_gy < game_config.GRID_HEIGHT and 0 <= end_gx < game_config.GRID_WIDTH and grid_matrix_ref[end_gy][end_gx] == 1)
        if start_walkable and end_walkable:
            grid_obj_pf = Grid(matrix=grid_matrix_ref); start_node = grid_obj_pf.node(start_gx, start_gy); end_node = grid_obj_pf.node(end_gx, end_gy)
            finder = AStarFinder(diagonal_movement=DiagonalMovement.always) 
            try:
                 path, runs = finder.find_path(start_node, end_node, grid_obj_pf)
                 if path and len(path) >= 1: 
                     npc.current_path = path; npc.current_path_index = 0; npc.current_action = action_after_astar; npc.target_destination = None 
                     if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Path found for '{action_after_astar}'. Length: {len(path)}")
                 else: 
                     if DEBUG_AI:
                         err_msg = "No path" if not path else f"Path too short/invalid (len: {len(path) if path else 'None'})"
                         print(f"AI DEBUG ({npc.name}): {err_msg} for '{action_after_astar}' to ({end_gx},{end_gy}).")
                     if action_after_astar.startswith("seeking_bed_slot_") and npc.target_bed_slot_id is not None:
                         slot_id = npc.target_bed_slot_id
                         if slot_id == 1 and game_state_ref.bed_slot_1_occupied_by == npc.uuid: game_state_ref.bed_slot_1_occupied_by = None
                         elif slot_id == 2 and game_state_ref.bed_slot_2_occupied_by == npc.uuid: game_state_ref.bed_slot_2_occupied_by = None
                         if DEBUG_AI: print(f"AI DEBUG ({npc.name}): Pathfinding failed/short for slot {slot_id}, releasing reservation.")
                         npc.target_bed_slot_id = None
                     npc.current_action = "idle"; npc.current_path = None; npc.current_path_index = 0
            except Exception as e_astar: 
                if DEBUG_AI: print(f"AI ERROR ({npc.name}): A* pathfinding for '{action_after_astar}' failed: {e_astar}")
                if action_after_astar.startswith("seeking_bed_slot_") and npc.target_bed_slot_id is not None:
                    slot_id = npc.target_bed_slot_id
                    if slot_id == 1 and game_state_ref.bed_slot_1_occupied_by == npc.uuid: game_state_ref.bed_slot_1_occupied_by = None
                    elif slot_id == 2 and game_state_ref.bed_slot_2_occupied_by == npc.uuid: game_state_ref.bed_slot_2_occupied_by = None
                    if DEBUG_AI: print(f"AI DEBUG ({npc.name}): A* crashed for slot {slot_id}, releasing reservation.")
                    npc.target_bed_slot_id = None
                npc.current_action = "idle"; npc.current_path = None; npc.current_path_index = 0
        else: 
            if DEBUG_AI: print(f"AI DEBUG ({npc.name}): A* start/end not walkable for '{action_after_astar}'. S:({start_gx},{start_gy}) W:{start_walkable} E:({end_gx},{end_gy}) W:{end_walkable}.")
            if action_after_astar.startswith("seeking_bed_slot_") and npc.target_bed_slot_id is not None:
                slot_id = npc.target_bed_slot_id
                if slot_id == 1 and game_state_ref.bed_slot_1_occupied_by == npc.uuid: game_state_ref.bed_slot_1_occupied_by = None
                elif slot_id == 2 and game_state_ref.bed_slot_2_occupied_by == npc.uuid: game_state_ref.bed_slot_2_occupied_by = None
                if DEBUG_AI: print(f"AI DEBUG ({npc.name}): A* start/end not walkable for slot {slot_id}, releasing reservation.")
                npc.target_bed_slot_id = None
            npc.current_action = "idle"; npc.current_path = None; npc.current_path_index = 0
    # Non c'è un return esplicito qui; la funzione modifica lo stato dell'NPC.
    # La funzione run_npc_ai_logic restituirà food_eaten_by_this_npc.

# --- Funzione Principale di Orchestrazione dell'IA (Nuova Struttura) ---
def run_npc_ai_logic(npc: 'Character', 
                     all_characters_list: list, 
                     game_hours_advanced: float, 
                     grid_matrix_ref: list, 
                     current_food_visible: bool,
                     food_pos_tuple: tuple, 
                     game_state_ref: GameState, 
                     param_toilet_rect: pygame.Rect | None = None, 
                     param_fun_object_rect: pygame.Rect | None = None, 
                     param_shower_rect: pygame.Rect | None = None
                     ) -> bool:
    """
    Orchestra la logica IA per un NPC, chiamando funzioni helper per diverse fasi.
    Restituisce True se cibo è stato mangiato, False altrimenti.
    """
    # food_eaten_result traccia se cibo è stato mangiato in una delle sotto-funzioni.
    # Inizializzato a False perché nessuna delle azioni IA consuma cibo direttamente tranne _handle_arrival_at_destination per "seeking_food".
    food_eaten_this_tick = False

    # Sezione 0: Gestione Azioni Bloccanti/Continue
    action_handled = _handle_continuous_actions(npc, game_state_ref)
    if action_handled is not None: # Se True o False, l'azione bloccante ha gestito il tick
        return action_handled # Che sarà False, perché _handle_continuous_actions non gestisce il mangiare

    # Sezione 1: Gestione "Seeking Partner"
    action_handled = _handle_partner_seeking(npc, all_characters_list, game_state_ref)
    if action_handled is not None: 
        return action_handled # Anche qui, sarà False

    # Sezione 2: Interruzione Azioni A*
    action_was_interrupted = _check_and_handle_interruptions(npc, current_food_visible, game_state_ref)
    if action_was_interrupted:
        return False # L'azione è stata interrotta, nessun cibo mangiato

    # Sezione 3: Gestione Arrivo a Destinazione A* (se non in un'azione bloccante e path è finito)
    if npc.current_path is None and npc.target_destination is None and \
       npc.current_action not in ["idle", "resting_on_bed", "phoning", 
                                   "romantic_interaction_action", "affectionate_interaction_action", 
                                   "seeking_partner", "using_toilet"]:
        arrival_result = _handle_arrival_at_destination(
            npc, game_state_ref, current_food_visible, food_pos_tuple, param_toilet_rect
            # Aggiungere qui param_fun_object_rect e param_shower_rect se _handle_arrival_at_destination li usa
        )
        if arrival_result is not None: # Se _handle_arrival_at_destination ha gestito l'arrivo e ha un esito
             return arrival_result # Questo potrebbe essere True se è stato mangiato cibo


    # Sezione 4: Logica Decisionale (se l'NPC è "idle" dopo tutto quanto sopra)
    if npc.current_action == "idle":
        _make_idle_decision( 
            npc, all_characters_list, grid_matrix_ref, current_food_visible, food_pos_tuple,
            game_state_ref, param_toilet_rect, param_fun_object_rect, param_shower_rect
        )
        # _make_idle_decision ora modifica lo stato dell'NPC. Non ha bisogno di restituire food_eaten.
        # Se decide un'azione immediata (phoning, seeking_partner), queste escono prima dalla logica IA.
        # Se decide un'azione A*, lo stato dell'NPC viene aggiornato, e il loop principale continuerà.

    return food_eaten_this_tick # Default, che sarà False a meno che _handle_arrival_at_destination non lo imposti a True