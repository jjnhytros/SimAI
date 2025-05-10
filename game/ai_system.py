# simai/game/ai_system.py
import math
import random 
import pygame
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from pathfinding.core.diagonal_movement import DiagonalMovement

try:
    from game import config 
    from game import game_utils
except ImportError as e:
    print(f"ERRORE CRITICO (ai_system.py): Impossibile importare config o game_utils: {e}")
    # Fallback molto basilare
    class ConfigPlaceholder:
        def __getattr__(self, name):
            default_map = {
                "NPC_HUNGER_THRESHOLD": 70, "NPC_ENERGY_THRESHOLD": 30, "NPC_SOCIAL_THRESHOLD": 40,
                "NPC_BLADDER_THRESHOLD": 75, "NPC_FUN_THRESHOLD": 30, "NPC_HYGIENE_THRESHOLD": 25,
                "NPC_INTIMACY_THRESHOLD": 75, "FOOD_RADIUS": 10, "NPC_EAT_REACH_DISTANCE": 15,
                "BED_RECT": pygame.Rect(0,0,1,1) if 'pygame' in sys.modules else None, # Placeholder Rect
                "NPC_BED_REACH_DISTANCE": 25, "NPC_PARTNER_INTERACTION_DISTANCE": 40,
                "INTIMACY_SATISFACTION_FIKI_FIKI": 60, "FIKI_FIKI_CHANCE": 0.5,
                "PREGNANCY_CHANCE_FEMALE": 0.25, "INTIMACY_SATISFACTION_FLIRT": 15,
                "SOCIAL_SATISFACTION_FLIRT": 10, "INTIMACY_INTERACTION_DURATION_HOURS": 1.0,
                "NPC_IDLE_WANDER_CHANCE": 0.02, "NPC_WANDER_MIN_DIST_TILES": 3,
                "NPC_WANDER_MAX_DIST_TILES": 8, "TILE_SIZE": 32, "GRID_WIDTH": 25, "GRID_HEIGHT": 18,
                "FOOD_VALUE": 30, "ENERGY_RECOVERY_RATE_PER_HOUR": 15, 
                "SOCIAL_RECOVERY_RATE_PER_HOUR_PHONE": 20,
                "BLADDER_RELIEF_AMOUNT": 80, "FUN_GAINED_AMOUNT": 40, "HYGIENE_GAINED_AMOUNT": 70
            }
            if name in default_map: return default_map[name]
            if name.endswith("POS"): return (100,100)
            print(f"ATTENZIONE (AI): Accesso a config.{name} fallito, uso placeholder.")
            return 70 if name.endswith("THRESHOLD") else (15 if name.endswith("DISTANCE") else (10 if "RATE" in name or "SATISFACTION" in name or "VALUE" in name else None))
    config = ConfigPlaceholder()
    class GameUtilsPlaceholder:
        def world_to_grid(self, x, y): return (int(x//32), int(y//32))
        def grid_to_world_center(self, gx, gy): return (gx*32+16, gy*32+16)
    game_utils = GameUtilsPlaceholder()
    import pygame # Necessario per pygame.Rect nel placeholder

def _find_walkable_adjacent_target_grid_coords(obj_rect, npc_x, npc_y, grid_matrix_ref):
    """
    Trova una cella della GRIGLIA camminabile adiacente a obj_rect.
    Restituisce una tupla (gx, gy) o None se non ne trova.
    """
    if not obj_rect:
        return None

    obj_gx_min, obj_gy_min = game_utils.world_to_grid(obj_rect.left, obj_rect.top)
    obj_gx_max, obj_gy_max = game_utils.world_to_grid(obj_rect.right - 1, obj_rect.bottom - 1)
    
    obj_center_gx = (obj_gx_min + obj_gx_max) // 2
    obj_center_gy = (obj_gy_min + obj_gy_max) // 2

    potential_targets_grid = []
    # Cerca celle adiacenti (Nord, Sud, Ovest, Est rispetto al perimetro dell'oggetto)
    # Sopra l'oggetto
    if obj_gy_min > 0:
        for gx_candidate in range(obj_gx_min, obj_gx_max + 1):
            potential_targets_grid.append((gx_candidate, obj_gy_min - 1))
    # Sotto l'oggetto
    if obj_gy_max < config.GRID_HEIGHT - 1:
        for gx_candidate in range(obj_gx_min, obj_gx_max + 1):
            potential_targets_grid.append((gx_candidate, obj_gy_max + 1))
    # A sinistra dell'oggetto
    if obj_gx_min > 0:
        for gy_candidate in range(obj_gy_min, obj_gy_max + 1):
            potential_targets_grid.append((obj_gx_min - 1, gy_candidate))
    # A destra dell'oggetto
    if obj_gx_max < config.GRID_WIDTH - 1:
        for gy_candidate in range(obj_gy_min, obj_gy_max + 1):
            potential_targets_grid.append((obj_gx_max + 1, gy_candidate))
    
    valid_targets_grid_coords = []
    for pt_gx, pt_gy in potential_targets_grid:
        if (0 <= pt_gy < config.GRID_HEIGHT and
            0 <= pt_gx < config.GRID_WIDTH and
            grid_matrix_ref[pt_gy][pt_gx] == 1): # È camminabile?
            valid_targets_grid_coords.append((pt_gx, pt_gy))
    
    if not valid_targets_grid_coords:
        # print(f"AI WARN: Nessuna cella adiacente camminabile trovata per l'oggetto a {obj_rect.topleft}")
        return None

    # Scegli il target valido più vicino all'NPC attuale
    npc_gx, npc_gy = game_utils.world_to_grid(npc_x, npc_y)
    valid_targets_grid_coords.sort(key=lambda pos: math.sqrt((pos[0]-npc_gx)**2 + (pos[1]-npc_gy)**2))
    
    return valid_targets_grid_coords[0] # Restituisce (gx, gy) della cella scelta


def run_npc_ai_logic(npc, all_characters_list, game_hours_advanced, grid_matrix_ref, 
                    current_food_visible,
                    food_pos_tuple, bed_rect_obj, 
                    toilet_rect_obj=None, # Ora si aspetta un Rect o None
                    fun_object_rect_obj=None, 
                    shower_rect_obj=None 
                    ):
    food_eaten_by_this_npc = False

    print(f"--- AI Tick: {npc.name} | Azione: {npc.current_action} | TargetP: {npc.target_partner.name if npc.target_partner else 'No'} | TargetXY: {npc.target_destination} | PathLen: {len(npc.current_path) if npc.current_path else 0}, PathIdx: {npc.current_path_index} ---")
    print(f"    Needs: H:{npc.hunger.get_value():.0f} E:{npc.energy.get_value():.0f} S:{npc.social.get_value():.0f} B:{npc.bladder.get_value():.0f} Fun:{npc.fun.get_value():.0f} Hyg:{npc.hygiene.get_value():.0f} Int:{npc.intimacy.get_value():.0f}")

    # 0. Gestione Azioni Continue/Bloccanti che hanno la precedenza
    if npc.current_action == "resting_on_bed":
        if npc.energy.get_value() >= npc.energy.max_value:
            npc.current_action = "idle"; npc.target_destination = None; npc.current_path = None; npc.current_path_index = 0
        return food_eaten_by_this_npc 
    
    elif npc.current_action == "phoning":
        if npc.social.get_value() >= npc.social.max_value: npc.current_action = "idle"
        return food_eaten_by_this_npc
    
    elif npc.current_action in ["fiki_fiki_action", "flirting_action"]:
        if npc.time_in_current_action >= getattr(config, 'INTIMACY_INTERACTION_DURATION_HOURS', 1.0):
            npc.current_action = "idle"; npc.time_in_current_action = 0.0
        return food_eaten_by_this_npc
    
    elif npc.current_action == "using_toilet":
        if npc.time_in_current_action >= getattr(config, 'TOILET_USE_DURATION_HOURS', 0.25):
            npc.use_toilet(getattr(config, 'BLADDER_RELIEF_AMOUNT', 80))
            npc.current_action = "idle"; npc.time_in_current_action = 0.0
        return food_eaten_by_this_npc
    
    # Aggiungere qui using_shower, using_fun_object se diventano azioni con durata

    # 1. Gestione "Seeking Partner" (movimento diretto)
    if npc.current_action == "seeking_partner":
        if npc.target_partner:
            dist_to_partner = math.sqrt((npc.x - npc.target_partner.x)**2 + (npc.y - npc.target_partner.y)**2)
            if dist_to_partner < config.NPC_PARTNER_INTERACTION_DISTANCE:
                new_action_state = ""
                if random.random() < getattr(config, 'FIKI_FIKI_CHANCE', 0.5):
                    npc.satisfy_intimacy_drive(config.INTIMACY_SATISFACTION_FIKI_FIKI)
                    npc.target_partner.satisfy_intimacy_drive(config.INTIMACY_SATISFACTION_FIKI_FIKI)
                    new_action_state = "fiki_fiki_action"
                    female_npc = npc if npc.gender=="female" else (npc.target_partner if npc.target_partner.gender=="female" else None)
                    if female_npc and not female_npc.is_pregnant:
                        if random.random() < getattr(config, 'PREGNANCY_CHANCE_FEMALE', 0.25):
                            if hasattr(female_npc, 'become_pregnant'): female_npc.become_pregnant()
                else:
                    npc.satisfy_intimacy_drive(config.INTIMACY_SATISFACTION_FLIRT)
                    npc.social.satisfy(config.SOCIAL_SATISFACTION_FLIRT)
                    npc.target_partner.satisfy_intimacy_drive(config.INTIMACY_SATISFACTION_FLIRT)
                    npc.target_partner.social.satisfy(config.SOCIAL_SATISFACTION_FLIRT)
                    new_action_state = "flirting_action"
                
                npc.current_action = new_action_state; npc.time_in_current_action = 0.0
                npc.target_partner.current_action = new_action_state; npc.target_partner.time_in_current_action = 0.0
                if hasattr(npc.target_partner, 'target_partner'): npc.target_partner.target_partner = None 
                if hasattr(npc.target_partner, 'target_destination'): npc.target_partner.target_destination = None
                if hasattr(npc.target_partner, 'current_path'): npc.target_partner.current_path = None; npc.target_partner.current_path_index = 0
                npc.target_partner = None
            # else: NPC continua a cercare partner (movimento in Character.update)
        else: # Target partner perso/non valido
            npc.current_action = "idle"; npc.target_partner = None
        # Se seeking_partner, il suo turno AI finisce qui (non fa A* per altro)
        npc.target_destination = None; npc.current_path = None; npc.current_path_index = 0
        return food_eaten_by_this_npc

    # 2. Interruzione Azioni di Ricerca A*
    should_interrupt_astar_seek = False; action_being_checked = npc.current_action
    if action_being_checked == "seeking_food" and (not current_food_visible or npc.hunger.get_value() < config.NPC_HUNGER_THRESHOLD / 2): should_interrupt_astar_seek = True
    elif action_being_checked == "seeking_bed" and npc.energy.get_value() > config.NPC_ENERGY_THRESHOLD * 1.8: should_interrupt_astar_seek = True
    elif action_being_checked == "seeking_toilet" and (not toilet_rect_obj or npc.bladder.get_value() < config.NPC_BLADDER_THRESHOLD / 2): should_interrupt_astar_seek = True
    elif action_being_checked == "seeking_fun_activity" and (not fun_object_pos_or_rect or npc.fun.get_value() > config.NPC_FUN_THRESHOLD * 1.8): should_interrupt_astar_seek = True
    elif action_being_checked == "seeking_shower" and (not shower_pos_or_rect or npc.hygiene.get_value() > config.NPC_HYGIENE_THRESHOLD * 1.8): should_interrupt_astar_seek = True
    elif action_being_checked == "wandering": # Il wandering può essere interrotto se un bisogno diventa più forte
        # Questa interruzione è gestita dal fatto che il blocco decisionale successivo (se idle) ha la priorità
        pass # Non c'è una condizione di interruzione specifica per il wandering qui, se non che diventi idle
        
    if should_interrupt_astar_seek:
        print(f"AI: {npc.name} INTERRUPTED A* seek action '{action_being_checked}'. Action -> idle")
        npc.current_action = "idle"; npc.target_destination = None; npc.current_path = None; npc.current_path_index = 0

    # 3. Gestione Arrivo a Destinazione per percorsi A*
    # (Character.update imposta current_path e target_destination a None all'arrivo del percorso/nodo)
    elif npc.current_path is None and npc.target_destination is None and \
        npc.current_action not in ["idle", "resting_on_bed", "phoning", "fiki_fiki_action", "flirting_action", "seeking_partner", "using_toilet"]: # Aggiunto using_toilet
        
        action_at_arrival = npc.current_action
        print(f"AI: {npc.name} Path A* ended for '{action_at_arrival}'. Processing arrival...")
        # Default a idle, poi l'azione specifica potrebbe cambiare lo stato di nuovo
        npc.current_action = "idle" 
        
        if action_at_arrival == "seeking_food":
            dist_to_food = math.sqrt((npc.x - food_pos_tuple[0])**2 + (npc.y - food_pos_tuple[1])**2)
            if current_food_visible and dist_to_food < npc.radius + config.FOOD_RADIUS + config.NPC_EAT_REACH_DISTANCE:
                if npc.hunger.get_value() > 0: npc.eat(config.FOOD_VALUE); food_eaten_by_this_npc = True 
        elif action_at_arrival == "seeking_bed":
            dist_to_bed_center = math.sqrt((npc.x - bed_rect_obj.centerx)**2 + (npc.y - bed_rect_obj.centery)**2)
            if dist_to_bed_center < config.NPC_BED_REACH_DISTANCE: npc.current_action = "resting_on_bed"
        elif action_at_arrival == "seeking_toilet" and toilet_rect_obj:
            target_center = toilet_rect_obj.center if isinstance(toilet_rect_obj, pygame.Rect) else toilet_rect_obj
            dist = math.sqrt((npc.x - target_center[0])**2 + (npc.y - target_center[1])**2)
            if dist < getattr(config, 'NPC_TOILET_REACH_DISTANCE', 15): npc.current_action = "using_toilet"; npc.time_in_current_action = 0.0
        elif action_at_arrival == "seeking_fun_activity" and fun_object_pos_or_rect: 
            # npc.current_action = "using_fun_object"; npc.time_in_current_action = 0.0 (Esempio)
            pass # Implementare interazione
        elif action_at_arrival == "seeking_shower" and shower_pos_or_rect:
            # npc.current_action = "using_shower"; npc.time_in_current_action = 0.0 (Esempio)
            pass
        elif action_at_arrival == "wandering":
            pass # È arrivato, ora è idle e rivaluterà.

        if npc.current_action not in ["resting_on_bed", "using_toilet"]: # Aggiungere altri stati continui qui
            npc.current_action = "idle" # Assicura reset se non è un'azione continua
            
    # 4. Decision Making: Scegliere una NUOVA azione solo se l'NPC è "idle"
    if npc.current_action == "idle":
        print(f"AI: {npc.name} IDLING. Needs: H:{npc.hunger.get_value():.0f}(T{config.NPC_HUNGER_THRESHOLD}), E:{npc.energy.get_value():.0f}(T{config.NPC_ENERGY_THRESHOLD}), S:{npc.social.get_value():.0f}(T{config.NPC_SOCIAL_THRESHOLD}), B:{npc.bladder.get_value():.0f}(T{config.NPC_BLADDER_THRESHOLD}), Fun:{npc.fun.get_value():.0f}(T{config.NPC_FUN_THRESHOLD}), Hyg:{npc.hygiene.get_value():.0f}(T{config.NPC_HYGIENE_THRESHOLD}), Int:{npc.intimacy.get_value():.0f}(T{config.NPC_INTIMACY_THRESHOLD}) | FoodVis:{current_food_visible}")
        
        target_pos_for_astar = None 
        action_after_astar = "idle"     
        partner_for_intimacy = None

        # Priorità dei bisogni
        if npc.bladder.get_value() > config.NPC_BLADDER_THRESHOLD and toilet_rect_obj:
            target_pos_for_astar = _find_walkable_adjacent_target_grid_coords(toilet_rect_obj, npc.x, npc.y, grid_matrix_ref)
            if  target_pos_for_astar:action_after_astar="seeking_toilet"
        elif npc.hunger.get_value() > config.NPC_HUNGER_THRESHOLD and current_food_visible:
            # Il cibo è un punto, il target è la sua cella (se camminabile)
            food_gx, food_gy = game_utils.world_to_grid(food_pos_tuple[0], food_pos_tuple[1])
            if 0 <= food_gy < config.GRID_HEIGHT and 0 <= food_gx < config.GRID_WIDTH and \
            grid_matrix_ref[food_gy][food_gx] == 1:
                target_grid_coords_for_astar = (food_gx, food_gy)
                action_after_astar = "seeking_food"
            else: print(f"AI WARN ({npc.name}): Cella del cibo ({food_gx},{food_gy}) bloccata.")
        elif npc.energy.get_value() < config.NPC_ENERGY_THRESHOLD and bed_rect_obj:
            target_grid_coords_for_astar = _find_walkable_adjacent_target_grid_coords(bed_rect_obj, npc.x, npc.y, grid_matrix_ref)
            if target_grid_coords_for_astar: 
                action_after_astar = "seeking_bed"
                print(f"AI DEBUG ({npc.name}): LOW ENERGY. Chosen adjacent grid for bed: {target_grid_coords_for_astar}")
        elif npc.hygiene.get_value() < config.NPC_HYGIENE_THRESHOLD and shower_rect_obj:
            target_grid_coords_for_astar = _find_walkable_adjacent_target_grid_coords(shower_rect_obj, npc.x, npc.y, grid_matrix_ref)
            if target_grid_coords_for_astar: action_after_astar = "seeking_shower"
        elif npc.fun.get_value() < config.NPC_FUN_THRESHOLD and fun_object_rect_obj:
            target_grid_coords_for_astar = _find_walkable_adjacent_target_grid_coords(fun_object_rect_obj, npc.x, npc.y, grid_matrix_ref)
            if target_grid_coords_for_astar: action_after_astar = "seeking_fun_activity"
        elif npc.intimacy.get_value() > config.NPC_INTIMACY_THRESHOLD:
            for char in all_characters_list:
                if char is not npc and ((npc.gender=="male" and char.gender=="female") or (npc.gender=="female" and char.gender=="male")):
                    if char.current_action in ["idle", "seeking_partner"] or char.intimacy.get_value() > config.NPC_INTIMACY_THRESHOLD*0.4:
                        partner_for_intimacy = char; break 
            if partner_for_intimacy:
                npc.target_partner = partner_for_intimacy; npc.current_action = "seeking_partner"
                return food_eaten_by_this_npc 
        elif npc.social.get_value() < config.NPC_SOCIAL_THRESHOLD:
            npc.current_action = "phoning"; return food_eaten_by_this_npc 
        
        # Wandering se nessun bisogno primario o azione diretta scelta
        elif target_pos_for_astar is None and npc.current_action == "idle": 
            if random.random() < getattr(config, 'NPC_IDLE_WANDER_CHANCE', 0.02):
                angle = random.uniform(0, 2 * math.pi)
                dist_tiles = random.uniform(config.NPC_WANDER_MIN_DIST_TILES, config.NPC_WANDER_MAX_DIST_TILES)
                dist_pixels = dist_tiles * config.TILE_SIZE
                wander_target_x = npc.x + math.cos(angle) * dist_pixels
                wander_target_y = npc.y + math.sin(angle) * dist_pixels
                wander_target_x = max(npc.radius, min(wander_target_x, config.SCREEN_WIDTH - npc.radius))
                wander_target_y = max(npc.radius, min(wander_target_y, config.SCREEN_HEIGHT - npc.radius))
                target_pos_for_astar = (wander_target_x, wander_target_y)
                action_after_astar = "wandering"
        
        if target_pos_for_astar:
            start_gx, start_gy = game_utils.world_to_grid(npc.x, npc.y)
            end_gx, end_gy = game_utils.world_to_grid(target_pos_for_astar[0], target_pos_for_astar[1])
            start_walkable = 0<=start_gy<config.GRID_HEIGHT and 0<=start_gx<config.GRID_WIDTH and grid_matrix_ref[start_gy][start_gx]==1
            end_walkable = 0<=end_gy<config.GRID_HEIGHT and 0<=end_gx<config.GRID_WIDTH and grid_matrix_ref[end_gy][end_gx]==1
            
            print(f"AI: {npc.name} trying A* for '{action_after_astar}'. S:({start_gx},{start_gy}) W:{start_walkable}. E:({end_gx},{end_gy}) W:{end_walkable}.")

            if start_walkable and end_walkable:
                grid_obj = Grid(matrix=grid_matrix_ref);start_node = grid_obj.node(start_gx, start_gy);end_node = grid_obj.node(end_gx, end_gy)
                finder = AStarFinder(diagonal_movement=DiagonalMovement.always) 
                try:
                    path, runs = finder.find_path(start_node, end_node, grid_obj)
                    if path and len(path) > 1: 
                        npc.current_path = path; npc.current_path_index = 0; npc.current_action = action_after_astar
                        print(f"AI: ({npc.name}) Path found for {npc.current_action}. Len:{len(path)}.")
                    else: 
                        npc.current_action = "idle"; npc.current_path = None; npc.current_path_index = 0
                        print(f"AI: ({npc.name}) No valid A* path for {action_after_astar}.")
                except Exception as e: 
                    print(f"AI Path EXCEPTION for {npc.name} ({action_after_astar}): {e}")
                    npc.current_action = "idle"; npc.current_path = None; npc.current_path_index = 0
            else: 
                npc.current_action = "idle"; npc.current_path = None; npc.current_path_index = 0
                print(f"AI: ({npc.name}) Unwalkable start/end for A* for {action_after_astar}.")
    return food_eaten_by_this_npc





