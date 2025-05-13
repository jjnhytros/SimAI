# simai/game/src/ai/npc_behavior.py
# Last Updated: 2025-05-12 (Moved to src/ai/, imports updated, English translation)

import math
import random 
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from pathfinding.core.diagonal_movement import DiagonalMovement
import pygame

# Imports from the 'game' package
try:
    from game import config 
    from game import game_utils
except ImportError as e:
    print(f"CRITICAL ERROR (npc_behavior.py): Could not import config or game_utils: {e}")
    # Fallback Placeholder (NOT for production)
    class ConfigPlaceholder:
        def __getattr__(self, name):
            # Provide minimal defaults
            defaults = {
                "NPC_HUNGER_THRESHOLD": 70, "NPC_ENERGY_THRESHOLD": 30, 
                "NPC_SOCIAL_THRESHOLD": 40, "NPC_BLADDER_THRESHOLD": 75,
                "NPC_FUN_THRESHOLD": 30, "NPC_HYGIENE_THRESHOLD": 25,
                "NPC_INTIMACY_THRESHOLD": 75, "FOOD_RADIUS": 10,
                "NPC_EAT_REACH_DISTANCE": 15, "NPC_BED_REACH_DISTANCE": 40,
                "NPC_PARTNER_INTERACTION_DISTANCE": 40,
                "INTIMACY_SATISFACTION_ROMANTIC": 60, "ROMANTIC_INTERACTION_CHANCE": 0.5,
                "PREGNANCY_CHANCE_FEMALE": 0.25, "INTIMACY_SATISFACTION_AFFECTIONATE": 15,
                "SOCIAL_SATISFACTION_AFFECTIONATE": 10, "INTIMACY_INTERACTION_DURATION_HOURS": 1.0,
                "TOILET_USE_DURATION_HOURS": 0.20, "BLADDER_RELIEF_AMOUNT": 80,
                "NPC_IDLE_WANDER_CHANCE": 0.02, "NPC_WANDER_MIN_DIST_TILES": 3,
                "NPC_WANDER_MAX_DIST_TILES": 8, "TILE_SIZE": 32, 
                "GRID_WIDTH": 32, "GRID_HEIGHT": 24, # Based on 1024x768
                "FOOD_VALUE": 30, "ENERGY_RECOVERY_RATE_PER_HOUR": 15, 
                "SOCIAL_RECOVERY_RATE_PER_HOUR_PHONE": 40,
                "FUN_GAINED_AMOUNT": 40, "HYGIENE_GAINED_AMOUNT": 70,
                "NPC_TOILET_REACH_DISTANCE": 32,
            }
            if name in defaults: return defaults[name]
            if name.endswith("POS"): return (100,100)
            return 70 if name.endswith("THRESHOLD") else (15 if name.endswith("DISTANCE") else (10 if "RATE" in name or "SATISFACTION" in name or "VALUE" in name else None))
    config = ConfigPlaceholder()
    class GameUtilsPlaceholder:
        def world_to_grid(self, x, y): ts = getattr(config, 'TILE_SIZE', 32); return (int(x//ts), int(y//ts))
        def grid_to_world_center(self, gx, gy): ts = getattr(config, 'TILE_SIZE', 32); return (gx*ts+16, gy*ts+16)
    game_utils = GameUtilsPlaceholder()
    import pygame # Required for pygame.Rect in placeholder


def _find_walkable_adjacent_target_grid_coords(obj_rect: pygame.Rect, npc_x: float, npc_y: float, grid_matrix_ref: list) -> tuple | None:
    """
    Finds a walkable grid cell adjacent to obj_rect, preferably close to (npc_x, npc_y).
    Returns (grid_x, grid_y) tuple or None if no suitable cell is found.
    """
    if not obj_rect:
        return None

    obj_gx_min, obj_gy_min = game_utils.world_to_grid(obj_rect.left, obj_rect.top)
    obj_gx_max, obj_gy_max = game_utils.world_to_grid(obj_rect.right - 1, obj_rect.bottom - 1)
    
    potential_targets_grid = []
    # Check cells adjacent to the perimeter of the object
    # Top row (above object)
    if obj_gy_min > 0:
        for gx_candidate in range(obj_gx_min, obj_gx_max + 1):
            potential_targets_grid.append((gx_candidate, obj_gy_min - 1))
    # Bottom row (below object)
    if obj_gy_max < config.GRID_HEIGHT - 1:
        for gx_candidate in range(obj_gx_min, obj_gx_max + 1):
            potential_targets_grid.append((gx_candidate, obj_gy_max + 1))
    # Left column (to the left of object)
    if obj_gx_min > 0:
        for gy_candidate in range(obj_gy_min, obj_gy_max + 1):
            potential_targets_grid.append((obj_gx_min - 1, gy_candidate))
    # Right column (to the right of object)
    if obj_gx_max < config.GRID_WIDTH - 1:
        for gy_candidate in range(obj_gy_min, obj_gy_max + 1):
            potential_targets_grid.append((obj_gx_max + 1, gy_candidate))
    
    valid_targets_grid_coords = []
    for pt_gx, pt_gy in potential_targets_grid:
        if (0 <= pt_gy < config.GRID_HEIGHT and
            0 <= pt_gx < config.GRID_WIDTH and
            grid_matrix_ref[pt_gy][pt_gx] == 1): # Is walkable?
            valid_targets_grid_coords.append((pt_gx, pt_gy))
    
    if not valid_targets_grid_coords:
        return None

    npc_gx, npc_gy = game_utils.world_to_grid(npc_x, npc_y)
    valid_targets_grid_coords.sort(key=lambda pos: math.sqrt((pos[0]-npc_gx)**2 + (pos[1]-npc_gy)**2))
    
    return valid_targets_grid_coords[0]


def run_npc_ai_logic(npc, all_characters_list: list, game_hours_advanced: float, grid_matrix_ref: list, 
                     current_food_visible: bool,
                     food_pos_tuple: tuple, bed_rect_obj: pygame.Rect, 
                     toilet_rect_obj: pygame.Rect = None, 
                     fun_object_rect_obj: pygame.Rect = None, 
                     shower_rect_obj: pygame.Rect = None 
                     ):
    """
    Manages the decision-making and action logic for a single NPC.
    Returns a boolean: True if food was eaten by this NPC this tick, False otherwise.
    """
    food_eaten_by_this_npc = False

    # Section 0: Handle Blocking/Continuous Actions (NPC is busy, returns early)
    if npc.current_action == "resting_on_bed":
        if npc.energy.get_value() >= npc.energy.max_value:
            npc.current_action = "idle"; npc.target_destination = None; npc.current_path = None; npc.current_path_index = 0
        return food_eaten_by_this_npc 
    elif npc.current_action == "phoning":
        if npc.social.get_value() >= npc.social.max_value: npc.current_action = "idle"
        return food_eaten_by_this_npc
    elif npc.current_action in ["romantic_interaction_action", "affectionate_interaction_action"]: # Renamed from fiki_fiki/flirt
        if npc.time_in_current_action >= getattr(config, 'INTIMACY_INTERACTION_DURATION_HOURS', 1.0):
            npc.current_action = "idle"; npc.time_in_current_action = 0.0
        return food_eaten_by_this_npc
    elif npc.current_action == "using_toilet":
        if npc.time_in_current_action >= getattr(config, 'TOILET_USE_DURATION_HOURS', 0.25):
            npc.use_toilet(getattr(config, 'BLADDER_RELIEF_AMOUNT', 80)) # Chiama il metodo di Character
            npc.current_action = "idle"
            npc.time_in_current_action = 0.0
            print(f"AI DEBUG ({npc.name}): Finished using toilet. Bladder: {npc.bladder.get_value():.0f}. Action -> idle")
        return food_eaten_by_this_npc 
    
    # Section 1: Handle "Seeking Partner" logic
    if npc.current_action == "seeking_partner":
        if npc.target_partner:
            dist_to_partner = math.sqrt((npc.x - npc.target_partner.x)**2 + (npc.y - npc.target_partner.y)**2)
            if dist_to_partner < config.NPC_PARTNER_INTERACTION_DISTANCE:
                interaction_outcome_action = ""
                if random.random() < getattr(config, 'ROMANTIC_INTERACTION_CHANCE', 0.5): # Using new constant name
                    npc.satisfy_intimacy_drive(config.INTIMACY_SATISFACTION_ROMANTIC) # New constant name
                    npc.target_partner.satisfy_intimacy_drive(config.INTIMACY_SATISFACTION_ROMANTIC) # New constant name
                    interaction_outcome_action = "romantic_interaction_action" # New action name
                    female_npc = npc if npc.gender=="female" else (npc.target_partner if npc.target_partner.gender=="female" else None)
                    if female_npc and not female_npc.is_pregnant:
                         if random.random() < getattr(config, 'PREGNANCY_CHANCE_FEMALE', 0.25):
                             if hasattr(female_npc, 'become_pregnant'): female_npc.become_pregnant()
                else:
                    npc.satisfy_intimacy_drive(config.INTIMACY_SATISFACTION_AFFECTIONATE) # New constant name
                    npc.social.satisfy(config.SOCIAL_SATISFACTION_AFFECTIONATE)         # New constant name
                    npc.target_partner.satisfy_intimacy_drive(config.INTIMACY_SATISFACTION_AFFECTIONATE) # New constant name
                    npc.target_partner.social.satisfy(config.SOCIAL_SATISFACTION_AFFECTIONATE)       # New constant name
                    interaction_outcome_action = "affectionate_interaction_action" # New action name
                
                npc.current_action = interaction_outcome_action; npc.time_in_current_action = 0.0
                npc.target_partner.current_action = interaction_outcome_action; npc.target_partner.time_in_current_action = 0.0
                if hasattr(npc.target_partner, 'target_partner'): npc.target_partner.target_partner = None 
                if hasattr(npc.target_partner, 'target_destination'): npc.target_partner.target_destination = None
                if hasattr(npc.target_partner, 'current_path'): npc.target_partner.current_path = None; npc.target_partner.current_path_index = 0
                npc.target_partner = None
        else: npc.current_action = "idle"; npc.target_partner = None
        npc.target_destination = None; npc.current_path = None; npc.current_path_index = 0
        return food_eaten_by_this_npc

    # Section 2: Interrupt A*-based Seeking Actions
    should_interrupt_astar_seek = False; action_being_checked = npc.current_action
    # ... (Full interruption logic for seeking_food, bed, toilet, fun_activity, shower as in last complete version) ...
    if should_interrupt_astar_seek:
        npc.current_action = "idle"; npc.target_destination = None; npc.current_path = None; npc.current_path_index = 0

    # Section 3: Handle Arrival at Destination for A* paths
    elif npc.current_path is None and npc.target_destination is None and \
         npc.current_action not in ["idle", "resting_on_bed", "phoning", 
                                   "romantic_interaction_action", "affectionate_interaction_action", 
                                   "seeking_partner", "using_toilet", 
                                   "using_shower", "using_fun_object"]: # Aggiungi tutti gli stati "using"
        action_at_arrival = npc.current_action
        # print(f"AI: {npc.name} Path A* ended for '{action_at_arrival}'. Processing arrival...")
        npc.current_action = "idle" # IMPOSTA A IDLE TEMPORANEAMENTE
        
        if action_at_arrival == "seeking_food":
            # ... logica cibo ...
            pass
        elif action_at_arrival == "seeking_bed": # <-- IL NOSTRO CASO
            dist_to_bed_center = math.sqrt((npc.x - bed_rect_obj.centerx)**2 + (npc.y - bed_rect_obj.centery)**2)
            # DEBUG: Stampa la distanza e la soglia
            print(f"AI DEBUG ({npc.name}): Arrived at bed's adjacent cell. Dist to bed center: {dist_to_bed_center:.1f}, Bed Reach Distance: {config.NPC_BED_REACH_DISTANCE}")
            if dist_to_bed_center < config.NPC_BED_REACH_DISTANCE: 
                npc.current_action = "resting_on_bed" # Transizione allo stato di riposo
                # Non servono più path/destination per questa azione
                npc.target_destination = None
                npc.current_path = None
                npc.current_path_index = 0 
                print(f"AI DEBUG ({npc.name}): Action -> resting_on_bed")
        elif action_at_arrival == "seeking_toilet" and toilet_rect_obj: # <-- FOCUS QUI
            # Verifica distanza dal centro del WC o da un punto di interazione definito
            # Il pathfinding ha portato a una cella ADIACENTE.
            # Ora controlliamo se è abbastanza vicino all'oggetto stesso per interagire.
            target_center_wc = toilet_rect_obj.center 
            dist_to_wc_center = math.sqrt((npc.x - target_center_wc[0])**2 + (npc.y - target_center_wc[1])**2)

            print(f"AI DEBUG ({npc.name}): Arrived near Toilet. NPC pos: ({npc.x:.0f},{npc.y:.0f}). Toilet center: ({target_center_wc[0]:.0f},{target_center_wc[1]:.0f}). Dist: {dist_to_wc_center:.1f}, Reach Thresh: {config.NPC_TOILET_REACH_DISTANCE}")

            if dist_to_wc_center < config.NPC_TOILET_REACH_DISTANCE: 
                npc.current_action = "using_toilet"
                npc.time_in_current_action = 0.0 # Inizia il timer per l'uso
                npc.target_destination = None # Ferma ogni movimento residuo
                npc.current_path = None
                npc.current_path_index = 0
                print(f"AI DEBUG ({npc.name}): Action -> using_toilet")
            else:
                print(f"AI DEBUG ({npc.name}): Reached toilet vicinity for '{action_at_arrival}', but NOT close enough. Action -> idle")
                npc.current_action = "idle" 
        # ... (logica per fun, shower, wandering) ...

        # Questo if potrebbe resettare "resting_on_bed" a "idle" se non gestito attentamente
        if npc.current_action not in ["resting_on_bed", "using_toilet"]: # Aggiungi altri stati "using_X" qui
            npc.current_action = "idle" # Assicura reset se non è un'azione continua di "utilizzo"
        
        npc.current_path_index = 0 # Resetta sempre l'indice dopo che un percorso è finito
            
    # Section 4: Decision Making (if NPC is "idle")
    if npc.current_action == "idle":
        # print(f"AI: {npc.name} IDLING. Needs: ... Int:{npc.intimacy.get_value():.0f}(T{config.NPC_INTIMACY_THRESHOLD}) ...")
        
        target_grid_for_astar = None; action_after_astar = "idle"; chosen_partner_for_intimacy = None
        
        # Priority of needs
        if npc.bladder.get_value() > config.NPC_BLADDER_THRESHOLD and toilet_rect_obj:
            target_grid_for_astar = _find_walkable_adjacent_target_grid_coords(toilet_rect_obj, npc.x, npc.y, grid_matrix_ref)
            if target_grid_for_astar: action_after_astar = "seeking_toilet"
        elif npc.hunger.get_value() > config.NPC_HUNGER_THRESHOLD and current_food_visible:
            food_gx, food_gy = game_utils.world_to_grid(food_pos_tuple[0], food_pos_tuple[1])
            if 0<=food_gy<config.GRID_HEIGHT and 0<=food_gx<config.GRID_WIDTH and grid_matrix_ref[food_gy][food_gx]==1:
                target_grid_for_astar = (food_gx, food_gy); action_after_astar = "seeking_food"
        elif npc.energy.get_value() < config.NPC_ENERGY_THRESHOLD and bed_rect_obj:
            target_grid_for_astar = _find_walkable_adjacent_target_grid_coords(bed_rect_obj, npc.x, npc.y, grid_matrix_ref)
            if target_grid_for_astar: action_after_astar = "seeking_bed"
        elif npc.hygiene.get_value() < config.NPC_HYGIENE_THRESHOLD and shower_rect_obj:
            target_grid_for_astar = _find_walkable_adjacent_target_grid_coords(shower_rect_obj, npc.x, npc.y, grid_matrix_ref)
            if target_grid_for_astar: action_after_astar = "seeking_shower"
        elif npc.fun.get_value() < config.NPC_FUN_THRESHOLD and fun_object_rect_obj:
            target_grid_for_astar = _find_walkable_adjacent_target_grid_coords(fun_object_rect_obj, npc.x, npc.y, grid_matrix_ref)
            if target_grid_for_astar: action_after_astar = "seeking_fun_activity"
        
        if target_grid_for_astar is None and npc.current_action == "idle": # If no object-based need, check social/intimacy
            if npc.intimacy.get_value() > config.NPC_INTIMACY_THRESHOLD:
                for char_partner_candidate in all_characters_list:
                    if char_partner_candidate is not npc and \
                       ((npc.gender == "male" and char_partner_candidate.gender == "female") or \
                        (npc.gender == "female" and char_partner_candidate.gender == "male")):
                        if char_partner_candidate.current_action in ["idle", "seeking_partner", "wandering"] or \
                           char_partner_candidate.intimacy.get_value() > config.NPC_INTIMACY_THRESHOLD * 0.4:
                           chosen_partner_for_intimacy = char_partner_candidate; break 
                if chosen_partner_for_intimacy:
                    npc.target_partner = chosen_partner_for_intimacy; npc.current_action = "seeking_partner"
                    return food_eaten_by_this_npc 
            elif npc.social.get_value() < config.NPC_SOCIAL_THRESHOLD:
                npc.current_action = "phoning"; return food_eaten_by_this_npc 
            elif npc.current_action == "idle": 
                if random.random() < getattr(config, 'NPC_IDLE_WANDER_CHANCE', 0.02):
                    angle = random.uniform(0, 2 * math.pi)
                    dist_tiles = random.uniform(config.NPC_WANDER_MIN_DIST_TILES, config.NPC_WANDER_MAX_DIST_TILES)
                    dist_pixels = dist_tiles * config.TILE_SIZE # Assicurati che config.TILE_SIZE sia accessibile
                    
                    wander_target_x = npc.x + math.cos(angle) * dist_pixels
                    wander_target_y = npc.y + math.sin(angle) * dist_pixels
                    half_width = (npc.frame_width / 2) if npc.frame_width > 0 else getattr(npc, 'fallback_radius', 15)
                    half_height = (npc.frame_height / 2) if npc.frame_height > 0 else getattr(npc, 'fallback_radius', 15)

                    wander_target_x = max(half_width, min(wander_target_x, config.SCREEN_WIDTH - half_width))
                    wander_target_y = max(half_height, min(wander_target_y, config.SCREEN_HEIGHT - half_height))
                    wander_gx, wander_gy = game_utils.world_to_grid(wander_target_x, wander_target_y)
                    if 0<=wander_gy<config.GRID_HEIGHT and 0<=wander_gx<config.GRID_WIDTH and grid_matrix_ref[wander_gy][wander_gx]==1:
                        target_grid_for_astar = (wander_gx, wander_gy); action_after_astar = "wandering"
    if npc.current_action == "idle":
        # print(f"AI DEBUG ({npc.name}) IDLING. Needs: ... B:{npc.bladder.get_value():.0f}(T{config.NPC_BLADDER_THRESHOLD}) ...")
        target_grid_for_astar = None; action_after_astar = "idle"; # ...

        if npc.bladder.get_value() > config.NPC_BLADDER_THRESHOLD and toilet_rect_obj: # <-- FOCUS QUI
            target_grid_for_astar = _find_walkable_adjacent_target_grid_coords(
                toilet_rect_obj, npc.x, npc.y, grid_matrix_ref
            )
            if target_grid_for_astar: 
                action_after_astar = "seeking_toilet"
                # target_world_pos_for_print = game_utils.grid_to_world_center(target_grid_for_astar[0], target_grid_for_astar[1])
                print(f"AI DEBUG ({npc.name}): Decided -> {action_after_astar} to grid {target_grid_for_astar} (world {target_world_pos_for_print})")
            # else:
                print(f"AI DEBUG ({npc.name}): Bladder high, but no walkable adjacent spot for Toilet.")
        # ... (elif per fame, energia, ecc. COME PRIMA) ...

        if target_grid_for_astar:
            target_world_pos_for_movement = game_utils.grid_to_world_center(target_grid_for_astar[0], target_grid_for_astar[1])
            start_gx, start_gy = game_utils.world_to_grid(npc.x, npc.y)
            end_gx, end_gy = target_grid_for_astar[0], target_grid_for_astar[1] 
            start_walkable = grid_matrix_ref[start_gy][start_gx] == 1
            end_walkable = grid_matrix_ref[end_gy][end_gx] == 1 # Should be true
            
            # print(f"AI: {npc.name} trying A* for '{action_after_astar}'. S:({start_gx},{start_gy}) W:{start_walkable}. E:({end_gx},{end_gy}) W:{end_walkable}.")
            if start_walkable and end_walkable:
                grid_obj = Grid(matrix=grid_matrix_ref); start_node = grid_obj.node(start_gx, start_gy); end_node = grid_obj.node(end_gx, end_gy)
                finder = AStarFinder(diagonal_movement=DiagonalMovement.always) 
                try:
                     path, runs = finder.find_path(start_node, end_node, grid_obj)
                     if path and len(path) > 1: 
                         npc.current_path = path; npc.current_path_index = 0; npc.current_action = action_after_astar; npc.target_destination = None 
                     else: npc.current_action = "idle"; npc.current_path = None; npc.current_path_index = 0
                except Exception: npc.current_action = "idle"; npc.current_path = None; npc.current_path_index = 0
            else: npc.current_action = "idle"; npc.current_path = None; npc.current_path_index = 0
                 
    return food_eaten_by_this_npc