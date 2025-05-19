# game/src/utils/game.py
import pygame
import os
import json
import random
import math
import heapq
import logging
from typing import List, Optional, Tuple, Dict, Any, TYPE_CHECKING
from collections import deque

import pygame_gui # Importa pygame_gui

# Importa dal package 'game'
from game import config

if TYPE_CHECKING:
    from game.src.entities.character import Character
    from game.src.modules.game_state_module import GameState
    from pygame_gui.core import UIElement
    from pygame_gui.elements import UIPanel, UITextBox, UIButton # Aggiungi UIButton

logger = logging.getLogger(__name__)
DEBUG_VERBOSE = getattr(config, 'DEBUG_AI_ACTIVE', False)
OBJECT_BLUEPRINTS: Optional[Dict[str, Dict[str, Any]]] = None

# --- Costanti per UI (definite qui o meglio in config.py) ---
NEEDS_BAR_WIDTH = getattr(config, 'UI_NEEDS_BAR_WIDTH', 100)
NEEDS_BAR_HEIGHT = getattr(config, 'UI_NEEDS_BAR_HEIGHT', 15)
NEEDS_BAR_PADDING_Y = getattr(config, 'UI_NEEDS_BAR_PADDING_Y', 3)
NEEDS_BAR_PADDING_X = getattr(config, 'UI_NEEDS_BAR_PADDING_X', 5)
ICON_TEXT_SPACING = getattr(config, 'UI_ICON_TEXT_SPACING', 3)

# Mappa per visualizzazione bisogni - 'icon_char_config_key' per Unicode
NEED_DISPLAY_ORDER_AND_INFO = [
    {"attr": "hunger",   "icon_key_for_map": "hunger_icon",   "icon_char_config_key": "ICON_CHAR_HUNGER",   "label": "Fame",   "color_config_key": "HUNGER_BAR_COLOR",   "fallback_color": getattr(config,"RED",(255,0,0)),    "show_label": getattr(config, "UI_SHOW_NEED_LABEL_TEXT", False)},
    {"attr": "energy",   "icon_key_for_map": "energy_icon",   "icon_char_config_key": "ICON_CHAR_ENERGY",   "label": "Energia","color_config_key": "ENERGY_BAR_COLOR",   "fallback_color": getattr(config,"BLUE",(0,0,255)),   "show_label": getattr(config, "UI_SHOW_NEED_LABEL_TEXT", False)},
    {"attr": "social",   "icon_key_for_map": "social_icon",   "icon_char_config_key": "ICON_CHAR_SOCIAL",   "label": "Social", "color_config_key": "SOCIAL_BAR_COLOR",   "fallback_color": getattr(config,"GREEN",(0,255,0)),  "show_label": getattr(config, "UI_SHOW_NEED_LABEL_TEXT", False)},
    {"attr": "bladder",  "icon_key_for_map": "bladder_icon",  "icon_char_config_key": "ICON_CHAR_BLADDER",  "label": "Vescica","color_config_key": "BLADDER_BAR_COLOR",  "fallback_color": getattr(config,"YELLOW",(255,255,0)), "show_label": getattr(config, "UI_SHOW_NEED_LABEL_TEXT", False)},
    {"attr": "fun",      "icon_key_for_map": "fun_icon",      "icon_char_config_key": "ICON_CHAR_FUN",      "label": "Divert.","color_config_key": "FUN_BAR_COLOR",      "fallback_color": getattr(config,"ORANGE",(255,165,0)), "show_label": getattr(config, "UI_SHOW_NEED_LABEL_TEXT", False)},
    {"attr": "hygiene",  "icon_key_for_map": "hygiene_icon",  "icon_char_config_key": "ICON_CHAR_HYGIENE",  "label": "Igiene", "color_config_key": "HYGIENE_BAR_COLOR",  "fallback_color": getattr(config,"CYAN",(0,255,255)),   "show_label": getattr(config, "UI_SHOW_NEED_LABEL_TEXT", False)},
    {"attr": "intimacy", "icon_key_for_map": "intimacy_icon", "icon_char_config_key": "ICON_CHAR_INTIMACY", "label": "Intim.", "color_config_key": "INTIMACY_BAR_COLOR", "fallback_color": getattr(config,"PINK",(255,192,203)),   "show_label": getattr(config, "UI_SHOW_NEED_LABEL_TEXT", False)},
]

OBJECT_BLUEPRINTS_DATA: Dict[str, Any] = {}

class AStarNode:
    def __init__(self, position: Tuple[int, int], parent=None):
        self.position = position; self.parent = parent
        self.g = 0; self.h = 0; self.f = 0
    def __lt__(self, other): return self.f < other.f
    def __eq__(self, other): return self.position == other.position if isinstance(other, AStarNode) else False
    def __hash__(self): return hash(self.position)

# --- Funzioni di Utilità Generiche ---

def load_image(filename: str, desired_size: Optional[Tuple[int, int]] = None,
               base_path: Optional[str] = None) -> Optional[pygame.Surface]:
    """Carica un'immagine, opzionalmente la ridimensiona."""
    path_to_use = base_path if base_path is not None else getattr(config, 'IMAGE_PATH', os.path.join(config.ASSETS_PATH, 'images'))

    # Se filename è già un percorso assoluto o relativo che include "assets", non aggiungere path_to_use
    # Questa è una semplificazione; una gestione più robusta dei percorsi potrebbe essere necessaria
    # se filename a volte include parti del percorso.
    # Per ora, assumiamo che filename sia solo il nome del file dentro path_to_use.
    full_path = os.path.join(path_to_use, filename)

    try:
        image = pygame.image.load(full_path)
        image = image.convert_alpha() # Sempre convert_alpha per trasparenza
        if desired_size:
            image = pygame.transform.smoothscale(image, desired_size)
        return image
    except pygame.error as e:
        logger.error(f"LOAD_IMAGE ERROR: Impossibile caricare l'immagine '{full_path}': {e}")
    except FileNotFoundError:
        logger.error(f"LOAD_IMAGE ERROR: File immagine NON TROVATO a '{full_path}'")
    return None

def render_unicode_icon(ui_icon_font: Optional[pygame.font.Font], unicode_char: str,
                        color: Tuple[int,int,int], desired_size: Tuple[int,int]) -> pygame.Surface:
    """Renderizza un carattere Unicode in una Surface della dimensione desiderata."""
    # Crea sempre una surface placeholder, anche se il font fallisce
    surf = pygame.Surface(desired_size, pygame.SRCALPHA)
    surf.fill((0,0,0,0)) # Trasparente di default

    if not ui_icon_font:
        logger.warning(f"render_unicode_icon: Font per icone non fornito. Impossibile renderizzare '{unicode_char}'.")
        # Disegna un placeholder grafico
        pygame.draw.rect(surf, getattr(config, "GREY", (128,128,128)), (1, 1, desired_size[0]-2, desired_size[1]-2), 1)
        pygame.draw.line(surf, getattr(config, "RED", (255,0,0)), (1,1), (desired_size[0]-1, desired_size[1]-1), 1)
        pygame.draw.line(surf, getattr(config, "RED", (255,0,0)), (1,desired_size[1]-1), (desired_size[0]-1, 1), 1)
        return surf

    if not unicode_char or unicode_char == "?": # Carattere di fallback per errore di config
        pygame.draw.rect(surf, getattr(config, "GREY", (128,128,128)), (1, 1, desired_size[0]-2, desired_size[1]-2), 1)
        try:
            q_mark_surf = ui_icon_font.render("?", True, getattr(config, "RED", (255,0,0)))
            surf.blit(q_mark_surf, ( (desired_size[0] - q_mark_surf.get_width()) // 2, (desired_size[1] - q_mark_surf.get_height()) // 2))
        except Exception as e_qmark:
             logger.error(f"Errore rendering placeholder '?' per icona: {e_qmark}")
        return surf

    try:
        char_surf = ui_icon_font.render(unicode_char, True, color)
        # Scala alla dimensione desiderata
        scaled_surf = pygame.transform.smoothscale(char_surf, desired_size)
        return scaled_surf
    except Exception as e:
        logger.error(f"Errore rendering icona Unicode '{unicode_char}' con font '{ui_icon_font.name if ui_icon_font else 'N/A'}': {e}")
        # Restituisce il placeholder già creato
        pygame.draw.rect(surf, getattr(config, "GREY", (128,128,128)), (1, 1, desired_size[0]-2, desired_size[1]-2), 1)
        return surf

def world_to_grid(world_x: float, world_y: float) -> Tuple[int, int]:
    return int(world_x // config.TILE_SIZE), int(world_y // config.TILE_SIZE)

def grid_to_world_center(grid_x: int, grid_y: int) -> Tuple[float, float]:
    return (grid_x * config.TILE_SIZE) + config.TILE_SIZE / 2, (grid_y * config.TILE_SIZE) + config.TILE_SIZE / 2

def is_close_to_point(current_pos_tuple: Tuple[float, float], target_pos_tuple: Optional[Tuple[float, float]],
                      threshold_distance: float = config.NPC_TARGET_REACH_THRESHOLD) -> bool:
    if not target_pos_tuple or not current_pos_tuple: return False
    dist_sq = (current_pos_tuple[0] - target_pos_tuple[0])**2 + (current_pos_tuple[1] - target_pos_tuple[1])**2
    return dist_sq <= threshold_distance**2

def get_random_walkable_tile_in_radius(
    center_pos_world: Tuple[float, float],
    pf_grid: List[List[int]],
    min_dist_tiles: int = getattr(config, 'NPC_WANDER_MIN_DIST_TILES', 3),
    max_dist_tiles: int = getattr(config, 'NPC_WANDER_MAX_DIST_TILES', 8),
    max_attempts: int = 20
) -> Optional[Tuple[float, float]]:
    center_gx, center_gy = world_to_grid(center_pos_world[0], center_pos_world[1])
    for _ in range(max_attempts):
        angle = random.uniform(0, 2 * math.pi); distance_tiles = random.uniform(min_dist_tiles, max_dist_tiles)
        offset_gx = int(round(math.cos(angle) * distance_tiles)); offset_gy = int(round(math.sin(angle) * distance_tiles))
        target_gx, target_gy = center_gx + offset_gx, center_gy + offset_gy
        if 0 <= target_gx < config.GRID_WIDTH and 0 <= target_gy < config.GRID_HEIGHT and \
           len(pf_grid) > target_gy and len(pf_grid[target_gy]) > target_gx and \
           pf_grid[target_gy][target_gx] == 1:
            return grid_to_world_center(target_gx, target_gy)
    if DEBUG_VERBOSE: logger.debug(f"WANDER: Impossibile trovare cella camminabile dopo {max_attempts} tentativi da ({center_gx},{center_gy}).")
    return None

# --- Pathfinding A* ---
def find_path_to_target(
    character_obj: 'Character',
    target_world_pos: Tuple[int, int],
    grid_map_data: List[List[int]],
    world_dynamic_obstacles: Optional[List[pygame.Rect]] = None
) -> Optional[deque]:
    if not grid_map_data or not grid_map_data[0]:
        logger.error("PATHFINDING: Griglia mappa dati vuota o non valida.")
        return None
    grid_height = len(grid_map_data)
    grid_width = len(grid_map_data[0])

    start_pos_grid = world_to_grid(character_obj.rect.centerx, character_obj.rect.centery)
    end_pos_grid = world_to_grid(target_world_pos[0], target_world_pos[1])

    if not (0 <= start_pos_grid[0] < grid_width and 0 <= start_pos_grid[1] < grid_height):
        logger.warning(f"PATHFINDING: Partenza {start_pos_grid} fuori griglia ({grid_width}x{grid_height}).")
        return None
    if not (0 <= end_pos_grid[0] < grid_width and 0 <= end_pos_grid[1] < grid_height):
        logger.warning(f"PATHFINDING: Destinazione {end_pos_grid} fuori griglia ({grid_width}x{grid_height}).")
        return None
    if grid_map_data[end_pos_grid[1]][end_pos_grid[0]] == 0:
        logger.warning(f"PATHFINDING: Destinazione {end_pos_grid} è un ostacolo.")
        return None
    if grid_map_data[start_pos_grid[1]][start_pos_grid[0]] == 0:
        logger.warning(f"PATHFINDING: Partenza {start_pos_grid} è un ostacolo. NPC bloccato?")
        return None

    start_node = AStarNode(start_pos_grid); end_node = AStarNode(end_pos_grid)
    open_list_heap = []; closed_set = set() # Usare set per closed_list è più efficiente
    open_list_dict = {} # Per tracciare nodi in open_list e i loro costi g per aggiornamenti

    heapq.heappush(open_list_heap, start_node)
    open_list_dict[start_node.position] = start_node.g
    
    iterations = 0
    max_iterations = getattr(config, 'ASTAR_MAX_ITERATIONS', 1000)

    while open_list_heap and iterations < max_iterations:
        iterations += 1
        current_node = heapq.heappop(open_list_heap)
        
        if current_node.position in open_list_dict: # Rimuovi da dict quando estratto dall'heap
            del open_list_dict[current_node.position]
        
        closed_set.add(current_node.position)

        if current_node == end_node:
            path = deque()
            temp = current_node
            while temp: path.appendleft(temp); temp = temp.parent
            if DEBUG_VERBOSE: logger.debug(f"PATHFINDING: Path trovato da {start_pos_grid} a {end_pos_grid}, lunghezza: {len(path)} nodi, iter: {iterations}")
            return path

        for offset_x, offset_y in [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            node_pos = (current_node.position[0] + offset_x, current_node.position[1] + offset_y)

            if not (0 <= node_pos[0] < grid_width and 0 <= node_pos[1] < grid_height): continue
            if grid_map_data[node_pos[1]][node_pos[0]] == 0: continue
            if node_pos in closed_set: continue

            move_cost = 1.414 if offset_x != 0 and offset_y != 0 else 1.0
            tentative_g_score = current_node.g + move_cost

            if node_pos in open_list_dict and tentative_g_score >= open_list_dict[node_pos]:
                continue # Percorso non migliore

            child_node = AStarNode(node_pos, current_node)
            child_node.g = tentative_g_score
            child_node.h = math.sqrt((child_node.position[0] - end_node.position[0])**2 + (child_node.position[1] - end_node.position[1])**2)
            child_node.f = child_node.g + child_node.h
            
            # Rimuovi vecchio nodo dall'heap se esiste (heapq non supporta decrease-key facilmente)
            # È più semplice aggiungere il nuovo e lasciare che l'heap gestisca la priorità.
            # Il controllo `tentative_g_score >= open_list_dict[node_pos]` previene la ri-aggiunta se non è migliore.
            # Ma se è migliore e già in heap, andrebbe aggiornato.
            # Per semplicità, aggiungiamo e lasciamo che open_list_dict prevenga l'esplorazione di percorsi peggiori.
            heapq.heappush(open_list_heap, child_node)
            open_list_dict[child_node.position] = child_node.g
            
    logger.warning(f"PATHFINDING WARN: No path found from {start_pos_grid} to {end_pos_grid} after {iterations} iterations.")
    return None

# --- Funzioni di Setup e Gestione Stato Gioco ---
def setup_pathfinding_grid(list_of_obstacle_rects: List[pygame.Rect]) -> List[List[int]]:
    logger.debug(f"Inizio setup_pathfinding_grid con {len(list_of_obstacle_rects)} ostacoli.")
    path_grid = [[1 for _ in range(config.GRID_WIDTH)] for _ in range(config.GRID_HEIGHT)]
    if list_of_obstacle_rects:
        for i, rect_obj in enumerate(list_of_obstacle_rects):
            if rect_obj is None: logger.warning(f"Ostacolo {i} è None."); continue
            if DEBUG_VERBOSE: logger.debug(f"Pathfinding Grid: Processo Ostacolo {i}: World Rect {rect_obj}")
            start_gx, start_gy = world_to_grid(rect_obj.left, rect_obj.top)
            end_gx, end_gy = world_to_grid(rect_obj.right - 1, rect_obj.bottom - 1)
            if DEBUG_VERBOSE: logger.debug(f"Pathfinding Grid: Ostacolo {i} Grid Coords ({start_gx},{start_gy}) to ({end_gx},{end_gy})")
            for gy in range(start_gy, end_gy + 1):
                for gx in range(start_gx, end_gx + 1):
                    if 0 <= gx < config.GRID_WIDTH and 0 <= gy < config.GRID_HEIGHT: path_grid[gy][gx] = 0
                    elif DEBUG_VERBOSE: logger.warning(f"Pathfinding Grid: Ostacolo {i} tentato fuori griglia: ({gx},{gy})")
        if DEBUG_VERBOSE: logger.debug("Fine marcatura ostacoli.")
    else: logger.info("Nessun ostacolo fornito a setup_pathfinding_grid.")
    return path_grid

def print_debug_grid(grid_map_data: List[List[int]], start_pos: Optional[Tuple[int,int]] = None, 
                     end_pos: Optional[Tuple[int,int]] = None, path: Optional[deque] = None):
    if not grid_map_data or not grid_map_data[0]: logger.warning("PRINT_DEBUG_GRID: Griglia vuota."); return
    h, w = len(grid_map_data), len(grid_map_data[0])
    display = [['.' for _ in range(w)] for _ in range(h)]
    for r in range(h):
        for c in range(w):
            if grid_map_data[r][c] == 0: display[r][c] = '#'
    if path:
        for node in path:
            px, py = node.position
            if (px,py) != start_pos and (px,py) != end_pos: display[py][px] = '*'
    if start_pos: display[start_pos[1]][start_pos[0]] = 'S'
    if end_pos: display[end_pos[1]][end_pos[0]] = 'E'
    grid_str = "\n--- GRIGLIA DI PATHFINDING (DEBUG) ---\n" + "\n".join(" ".join(row) for row in display) + "\n--- FINE GRIGLIA ---"
    logger.info(grid_str)


def load_object_blueprints():
    global OBJECT_BLUEPRINTS
    if OBJECT_BLUEPRINTS is None: # Carica solo una volta
        filepath = os.path.join(config.DATA_PATH, config.OBJECT_BLUEPRINTS_FILENAME)
        try:
            with open(filepath, 'r') as f:
                OBJECT_BLUEPRINTS = json.load(f)
            logger.info(f"Object blueprints caricati da '{filepath}'.")
        except FileNotFoundError:
            logger.error(f"File object blueprints '{filepath}' non trovato.")
            OBJECT_BLUEPRINTS = {}
        except json.JSONDecodeError:
            logger.error(f"Errore decoding JSON per object blueprints in '{filepath}'.")
            OBJECT_BLUEPRINTS = {}
        except Exception as e:
            logger.error(f"Errore generico caricamento object blueprints: {e}")
            OBJECT_BLUEPRINTS = {}

def get_object_blueprint(object_id: str) -> Optional[Dict[str, Any]]:
    global OBJECT_BLUEPRINTS
    if OBJECT_BLUEPRINTS is None:
        load_object_blueprints() # Assicurati che siano caricati

    if OBJECT_BLUEPRINTS:
        blueprint = OBJECT_BLUEPRINTS.get(object_id)
        if blueprint:
            logger.debug(f"Blueprint trovato per ID '{object_id}': {blueprint}")
        else:
            logger.warning(f"Nessun blueprint trovato per ID '{object_id}' in OBJECT_BLUEPRINTS.")
        return blueprint
    else:
        logger.error("OBJECT_BLUEPRINTS è vuoto o None dopo il tentativo di caricamento.")
    return None

def setup_object_interaction_points(game_state: 'GameState', object_type: str, 
                                    blueprint_data: Optional[Dict[str, Any]], 
                                    object_world_rect: pygame.Rect):
    if not blueprint_data:
        logger.warning(f"UTILS: Blueprint dati mancante per {object_type} a {object_world_rect.topleft}. Impossibile impostare punti interazione.")
        return

    blueprint_id = blueprint_data.get("id", f"UnknownBlueprint_{object_type}")
    logger.debug(f"UTILS: Setup punti interazione per '{object_type}' (ID: '{blueprint_id}') a ({object_world_rect.left},{object_world_rect.top})")

    obj_l, obj_t = object_world_rect.left, object_world_rect.top
    interaction_points_data = blueprint_data.get("interaction_points", {})

    if object_type == "bed":
        sleep_slots_data = interaction_points_data.get("sleep_slots", [])
        interaction_slots_data = interaction_points_data.get("interaction_slots", [])

        game_state.bed_slot_0_sleep_pos_world = None
        game_state.bed_slot_0_interaction_pos_world = None
        game_state.bed_slot_1_sleep_pos_world = None
        game_state.bed_slot_1_interaction_pos_world = None

        if len(sleep_slots_data) >= 1 and "offset" in sleep_slots_data[0]:
            s0_off = sleep_slots_data[0]["offset"]
            if isinstance(s0_off, list) and len(s0_off) == 2:
                game_state.bed_slot_0_sleep_pos_world = (obj_l + s0_off[0], obj_t + s0_off[1])
        
        if len(interaction_slots_data) >= 1 and "offset" in interaction_slots_data[0]:
            i0_off = interaction_slots_data[0]["offset"]
            if isinstance(i0_off, list) and len(i0_off) == 2:
                game_state.bed_slot_0_interaction_pos_world = (obj_l + i0_off[0], obj_t + i0_off[1])

        if len(sleep_slots_data) >= 2 and "offset" in sleep_slots_data[1]:
            s1_off = sleep_slots_data[1]["offset"]
            if isinstance(s1_off, list) and len(s1_off) == 2:
                game_state.bed_slot_1_sleep_pos_world = (obj_l + s1_off[0], obj_t + s1_off[1])

        if len(interaction_slots_data) >= 2 and "offset" in interaction_slots_data[1]:
            i1_off = interaction_slots_data[1]["offset"]
            if isinstance(i1_off, list) and len(i1_off) == 2:
                game_state.bed_slot_1_interaction_pos_world = (obj_l + i1_off[0], obj_t + i1_off[1])
            
        log_msg_bed = "    Bed Slots - "
        log_msg_bed += f"Interaction: [{game_state.bed_slot_0_interaction_pos_world}, {game_state.bed_slot_1_interaction_pos_world if game_state.bed_slot_1_interaction_pos_world else 'N/A'}]. "
        log_msg_bed += f"Sleep: [{game_state.bed_slot_0_sleep_pos_world}, {game_state.bed_slot_1_sleep_pos_world if game_state.bed_slot_1_sleep_pos_world else 'N/A'}]"
        logger.debug(log_msg_bed)

    elif object_type == "toilet":
        # 'interaction_use_points' è definita e usata SOLO dentro questo blocco 'elif'
        interaction_use_points = interaction_points_data.get("use", []) 
        
        # Tutta la logica che usa 'interaction_use_points' deve essere indentata qui sotto
        if interaction_use_points and isinstance(interaction_use_points, list) and len(interaction_use_points) > 0:
            first_use_point = interaction_use_points[0] 
            if isinstance(first_use_point, dict) and "offset" in first_use_point and \
               isinstance(first_use_point["offset"], (list, tuple)) and len(first_use_point["offset"]) == 2:
                
                offset_x = first_use_point["offset"][0]
                offset_y = first_use_point["offset"][1]
                game_state.toilet_interaction_point_world = (obj_l + offset_x, obj_t + offset_y)
                logger.debug(f"    Toilet Interaction Point ('use'[0]): World ({game_state.toilet_interaction_point_world[0]:.0f},{game_state.toilet_interaction_point_world[1]:.0f}) from offset [{offset_x},{offset_y}]")
                
                if "facing" in first_use_point:
                    if not hasattr(game_state, 'toilet_facing_direction'): # Aggiungi l'attributo a GameState se non esiste
                        game_state.toilet_facing_direction = None
                    game_state.toilet_facing_direction = first_use_point.get("facing")
                    logger.debug(f"    Toilet Facing Direction: {game_state.toilet_facing_direction}")
            else:
                logger.warning(f"    Blueprint 'toilet' ('{blueprint_id}'): punto 'use'[0] malformato o offset mancante. Uso fallback.")
                game_state.toilet_interaction_point_world = (object_world_rect.centerx, object_world_rect.bottom + config.TILE_SIZE // 4)
        else:
            logger.warning(f"    Blueprint 'toilet' ('{blueprint_id}'): 'interaction_points.use' non trovato o vuoto. Uso fallback per interaction point.")
            game_state.toilet_interaction_point_world = (object_world_rect.centerx, object_world_rect.bottom + config.TILE_SIZE // 4)
            
    else:
        logger.warning(f"UTILS: Tipo oggetto '{object_type}' (ID: '{blueprint_id}') non ha una gestione specifica per i punti di interazione in setup_object_interaction_points.")

def occupy_bed_slot_for_character(game_state: 'GameState', character: 'Character', slot_idx: int) -> bool:
    if not game_state.bed_rect: return False
    if slot_idx == 0:
        if not game_state.bed_slot_1_occupied_by: game_state.bed_slot_1_occupied_by = character.uuid; char_setup = True
        elif game_state.bed_slot_1_occupied_by == character.uuid: char_setup = True; # Già lì
        else: return False # Occupato da altri
    elif slot_idx == 1:
        if not game_state.bed_slot_2_occupied_by: game_state.bed_slot_2_occupied_by = character.uuid; char_setup = True
        elif game_state.bed_slot_2_occupied_by == character.uuid: char_setup = True;
        else: return False
    else: return False # Slot non valido
    
    if char_setup:
        character.bed_object_id = "main_bed"; character.bed_slot_index = slot_idx; character.is_on_bed = True
        if DEBUG_VERBOSE: logger.debug(f"UTILS: {character.name} occupa slot letto {slot_idx}.")
    return True


def free_bed_slot_for_character(game_state: 'GameState', character: 'Character'):
    freed = False
    if character.bed_object_id == "main_bed":
        if character.bed_slot_index == 0 and game_state.bed_slot_1_occupied_by == character.uuid:
            game_state.bed_slot_1_occupied_by = None; freed = True
        elif character.bed_slot_index == 1 and game_state.bed_slot_2_occupied_by == character.uuid:
            game_state.bed_slot_2_occupied_by = None; freed = True
    character.bed_object_id = None; character.bed_slot_index = -1; character.is_on_bed = False
    if freed and DEBUG_VERBOSE: logger.debug(f"UTILS: {character.name} ha liberato lo slot letto.")

# --- Funzioni UI ---
def load_all_game_assets(ui_icon_font: Optional[pygame.font.Font]
                        ) -> Tuple[Dict[str, pygame.Surface], List[pygame.Surface], Dict[str, Optional[pygame.Surface]], Tuple[int,int]]:
    """Carica asset UI, usando caratteri Unicode per le icone."""
    loaded_icons_map: Dict[str, pygame.Surface] = {}
    speed_button_icon_surfaces: List[pygame.Surface] = []
    bed_images: Dict[str, Optional[pygame.Surface]] = {"base": None, "cover": None}
    
    # Dimensioni per le icone
    default_icon_size = (getattr(config, 'UI_ICON_SIZE', 24), getattr(config, 'UI_ICON_SIZE', 24))
    time_button_icon_size = (getattr(config, 'UI_ICON_SIZE_TIME_BUTTONS', 30), getattr(config, 'UI_ICON_SIZE_TIME_BUTTONS', 30))
    
    # Definizione CORRETTA della variabile:
    needs_icon_size = (getattr(config, 'UI_ICON_SIZE_NEEDS', 20), getattr(config, 'UI_ICON_SIZE_NEEDS', 20)) 
    
    icon_color = getattr(config, 'UI_UNICODE_ICON_COLOR', config.BLACK if hasattr(config, 'BLACK') else (0,0,0))

    # Icone Velocità (Unicode)
    speed_icon_definitions = [
        ("pause", "ICON_CHAR_PAUSE", "\u23F8"),
        ("play", "ICON_CHAR_PLAY", "\u25B6"),
        ("ffwd", "ICON_CHAR_FFWD", "\u23E9"),
        ("ffwd_2x", "ICON_CHAR_FFWD2", getattr(config, "ICON_CHAR_FFWD2_FALLBACK", "\u23E9\u23E9")),
        ("ffwd_3x", "ICON_CHAR_FFWD3", getattr(config, "ICON_CHAR_FFWD3_FALLBACK", "\u23E9\u23E9\u23E9")),
        ("ffwd_sleep", "ICON_CHAR_SLEEP_SPEED", "\U0001F4A4")
    ]
    for key, char_conf_key, fallback_char in speed_icon_definitions:
        unicode_char = getattr(config, char_conf_key, fallback_char)
        surf = render_unicode_icon(ui_icon_font, unicode_char, icon_color, time_button_icon_size)
        loaded_icons_map[key] = surf
        loaded_icons_map[key+"_char_surf"] = surf 
        speed_button_icon_surfaces.append(surf)

    # Icone Bisogni (Unicode)
    for need_data in NEED_DISPLAY_ORDER_AND_INFO: 
        icon_map_storage_key = need_data["icon_key_for_map"]
        char_conf_key = need_data["icon_char_config_key"]
        fallback_char = "?"
        
        unicode_char = getattr(config, char_conf_key, fallback_char)
        # Usa il nome corretto della variabile per la dimensione:
        surf = render_unicode_icon(ui_icon_font, unicode_char, icon_color, needs_icon_size) # <-- CORRETTO QUI
        loaded_icons_map[icon_map_storage_key] = surf
    
    # La variabile da restituire per le dimensioni delle icone dei bisogni
    need_icon_dim_final = needs_icon_size # <-- CORRETTO QUI

    # Icona periodo giorno (Unicode)
    default_period_char_key = getattr(config, 'DEFAULT_PERIOD_ICON_CHAR_KEY', "ICON_CHAR_SUN")
    default_period_char_val = getattr(config, default_period_char_key, "\u2600") 
    loaded_icons_map["period_icon_default"] = render_unicode_icon(ui_icon_font, default_period_char_val, icon_color, default_icon_size)
    
    for _start_h, _p_name, p_icon_char_cfg_key in getattr(config, "PERIOD_DEFINITIONS", []):
        if isinstance(p_icon_char_cfg_key, str) and p_icon_char_cfg_key.startswith("ICON_CHAR_"):
             char_val = getattr(config, p_icon_char_cfg_key, "?")
             if char_val not in loaded_icons_map: 
                 loaded_icons_map[p_icon_char_cfg_key] = render_unicode_icon(ui_icon_font, char_val, icon_color, default_icon_size)

    # Immagini Letto
    bed_images["base"] = load_image(getattr(config, 'BED_IMAGE_BASE_FILENAME', "bed_base.png"))
    bed_images["cover"] = load_image(getattr(config, 'BED_IMAGE_COVER_FILENAME', "bed_cover.png"))
    
    logger.info("Asset UI (icone Unicode e immagini) caricati.")
    return loaded_icons_map, speed_button_icon_surfaces, bed_images, need_icon_dim_final


def setup_gui_elements(ui_manager: 'pygame_gui.UIManager', all_npcs: List['Character'], 
                       selected_npc_idx: int, time_button_dimensions: Tuple[int, int], 
                       panel_height: int, screen_width: int, screen_height: int) -> Dict[str, Any]:
    gui_elements: Dict[str, Any] = {}
    panel_pad = config.UI_BOTTOM_PANEL_PADDING; section_space = config.UI_SECTION_SPACING
    panel_rect = pygame.Rect(0, screen_height - panel_height, screen_width, panel_height)
    gui_elements['bottom_panel'] = pygame_gui.elements.UIPanel(
        relative_rect=panel_rect, manager=ui_manager, object_id="#bottom_panel")
    
    panel_iw = panel_rect.width - (2 * panel_pad); panel_ih = panel_rect.height - (2 * panel_pad)
    base_y_in_panel = panel_pad
    
    # Sezione Sinistra
    left_x = panel_pad; left_w = int(panel_iw * config.UI_LEFT_SECTION_WIDTH_PERCENT)
    curr_y_l = base_y_in_panel; lbl_h = 25; lbl_space = 3
    gui_elements['char_status_label'] = pygame_gui.elements.UITextBox("NPC: -", pygame.Rect(left_x, curr_y_l, left_w, lbl_h), ui_manager, container=gui_elements['bottom_panel'], object_id="#char_name_label"); curr_y_l += lbl_h + lbl_space
    gui_elements['action_label'] = pygame_gui.elements.UITextBox(config.UI_LABEL_ACTION + "-", pygame.Rect(left_x, curr_y_l, left_w, lbl_h), ui_manager, container=gui_elements['bottom_panel'], object_id="#action_label"); curr_y_l += lbl_h + lbl_space
    gui_elements['finance_label'] = pygame_gui.elements.UITextBox(config.UI_LABEL_FINANCE + "-", pygame.Rect(left_x, curr_y_l, left_w, lbl_h), ui_manager, container=gui_elements['bottom_panel'], object_id="#finance_label"); curr_y_l += lbl_h + lbl_space
    gui_elements['mood_label'] = pygame_gui.elements.UITextBox(config.UI_LABEL_MOOD + "-", pygame.Rect(left_x, curr_y_l, left_w, lbl_h), ui_manager, container=gui_elements['bottom_panel'], object_id="#mood_label"); curr_y_l += lbl_h + lbl_space
    gui_elements['pregnancy_label'] = pygame_gui.elements.UITextBox("", pygame.Rect(left_x, curr_y_l, left_w, lbl_h), ui_manager, container=gui_elements['bottom_panel'], object_id="#pregnancy_label"); gui_elements['pregnancy_label'].visible = False

    # Sezione Centrale
    center_x = left_x + left_w + section_space; center_w = int(panel_iw * config.UI_CENTER_SECTION_WIDTH_PERCENT)
    time_btn_w, time_btn_h = time_button_dimensions
    num_btns = len(getattr(config, 'TIME_SPEED_SETTINGS', {})); total_btn_w = (num_btns * time_btn_w) + ((num_btns - 1) * 5)
    btns_start_x_panel = center_x + (center_w - total_btn_w) // 2
    btns_y_panel = base_y_in_panel
    gui_elements['time_button_rects'] = [pygame.Rect(btns_start_x_panel + i * (time_btn_w + 5), btns_y_panel, time_btn_w, time_btn_h) for i in range(num_btns)]
    time_disp_y = btns_y_panel + time_btn_h + 10; time_disp_h = 35
    gui_elements['time_label'] = pygame_gui.elements.UITextBox("Ora...", pygame.Rect(center_x, time_disp_y, center_w, time_disp_h), ui_manager, container=gui_elements['bottom_panel'], object_id="#time_display_panel")

    # Sezione Destra
    right_x = center_x + center_w + section_space
    right_w = panel_iw - (left_w + center_w + (2 * section_space))
    curr_y_r = base_y_in_panel
    btn_h_r = config.UI_RIGHT_SECTION_BUTTON_HEIGHT; btn_space_r = config.UI_RIGHT_SECTION_BUTTON_SPACING_Y
    cats_right = [("aspirations_btn", config.UI_LABEL_ASPIRATIONS), ("career_btn", config.UI_LABEL_CAREER),
                  ("skills_btn", config.UI_LABEL_SKILLS), ("relationships_btn", config.UI_LABEL_RELATIONSHIPS),
                  ("inventory_btn", config.UI_LABEL_INVENTORY), ("needs_display_btn", config.UI_LABEL_NEEDS_BUTTON)]
    for id_key, lbl_txt in cats_right:
        btn_rect = pygame.Rect(right_x, curr_y_r, right_w, btn_h_r)
        gui_elements[id_key] = pygame_gui.elements.UIButton(relative_rect=btn_rect, text=lbl_txt, manager=ui_manager, container=gui_elements['bottom_panel'], object_id=f"#{id_key}")
        curr_y_r += btn_h_r + btn_space_r
        if id_key == "needs_display_btn": gui_elements['needs_button_rect_abs_for_positioning'] = gui_elements[id_key].get_abs_rect()
    
    gui_elements['needs_bar_area_x_in_panel'] = right_x # X relativo al pannello
    gui_elements['needs_bar_area_y_in_panel'] = curr_y_r # Y relativo al pannello, sotto i pulsanti
        
    logger.info(f"Elementi GUI pannello ({len(gui_elements)}) creati.")
    return gui_elements


def draw_all_manual_ui_elements(
    screen_surface: pygame.Surface,
    loaded_icons_map: Dict[str, pygame.Surface], 
    speed_button_icons: List[pygame.Surface],
    current_selected_speed_idx: int,
    current_day_period_name: str, 
    selected_character_to_display: Optional['Character'],
    bottom_panel_gui_obj: Optional['pygame_gui.elements.UIPanel'],
    needs_bars_start_x_in_panel: int, 
    needs_bars_start_y_in_panel: int,
    ui_current_text_color: Tuple[int,int,int],
    default_ui_font: Optional[pygame.font.Font],
    time_control_buttons_rect_list: List[pygame.Rect], 
    need_icon_dimensions: Tuple[int,int], # Questa è la dimensione a cui sono state renderizzate le icone
    gui_elements_ref: Dict[str, Any]
    ):
    """Disegna gli elementi UI manuali come barre dei bisogni, pulsanti velocità e icona periodo."""
    
    panel_abs_x, panel_abs_y = 0, 0
    if bottom_panel_gui_obj:
        # get_abs_rect() restituisce il rettangolo in coordinate assolute dello schermo
        panel_abs_rect = bottom_panel_gui_obj.get_abs_rect()
        panel_abs_x, panel_abs_y = panel_abs_rect.topleft
    else:
        logger.warning("draw_all_manual_ui_elements: bottom_panel_gui_obj non fornito. Il posizionamento potrebbe essere errato.")
        # Se il pannello non c'è, disegna rispetto a (0,0) dello schermo, il che probabilmente non è desiderato.

    # --- 1. Disegna Pulsanti Velocità ---
    # Questi sono disegnati manualmente usando le icone (ora Surface Unicode) e i rect calcolati.
    if speed_button_icons and time_control_buttons_rect_list and \
       len(speed_button_icons) >= len(getattr(config, 'TIME_SPEED_SETTINGS', {})):
        for idx, panel_relative_rect in enumerate(time_control_buttons_rect_list):
            if idx < len(speed_button_icons): # Protezione indice
                icon_to_draw = speed_button_icons[idx]
                # Converte il rect relativo al pannello in rect assoluto sullo schermo
                absolute_button_rect = pygame.Rect(panel_abs_x + panel_relative_rect.left,
                                                 panel_abs_y + panel_relative_rect.top,
                                                 panel_relative_rect.width,
                                                 panel_relative_rect.height)
                screen_surface.blit(icon_to_draw, absolute_button_rect.topleft)
                if idx == current_selected_speed_idx: # Evidenzia il pulsante selezionato
                    highlight_color = getattr(config, "YELLOW", (255,255,0)) # Usa config.YELLOW se definito
                    pygame.draw.rect(screen_surface, highlight_color, absolute_button_rect, 2) # Bordo

    # --- 2. Disegna Icona Periodo Giorno (accanto alla label dell'ora nel pannello) ---
    time_label_pygame_gui_element = gui_elements_ref.get('time_label') # Questo è il UITextBox nel pannello
    if time_label_pygame_gui_element and default_ui_font: # Assicurati che il font per il testo UI esista
        period_icon_char_key_from_config = None
        # Trova la chiave del carattere Unicode per il periodo corrente
        for _start_hour, period_name_iter, icon_char_key_iter in getattr(config, "PERIOD_DEFINITIONS", []):
            if period_name_iter == current_day_period_name:
                period_icon_char_key_from_config = icon_char_key_iter
                break
        
        period_icon_to_draw_surface = None
        if period_icon_char_key_from_config:
            period_icon_to_draw_surface = loaded_icons_map.get(period_icon_char_key_from_config)
        
        if not period_icon_to_draw_surface: # Fallback all'icona di default se quella specifica non è trovata
            period_icon_to_draw_surface = loaded_icons_map.get(getattr(config, 'DEFAULT_PERIOD_ICON_CHAR_KEY', "ICON_CHAR_SUN"))
        if not period_icon_to_draw_surface: # Ulteriore fallback all'icona "period_icon_default" se esiste
            period_icon_to_draw_surface = loaded_icons_map.get("period_icon_default")


        if period_icon_to_draw_surface:
            icon_absolute_rect = period_icon_to_draw_surface.get_rect()
            time_label_absolute_rect = time_label_pygame_gui_element.get_abs_rect()
            
            # Posiziona a sinistra della label dell'ora (che è nel pannello)
            icon_absolute_rect.right = time_label_absolute_rect.left - getattr(config, "UI_PERIOD_ICON_TIME_LABEL_SPACING", 10)
            icon_absolute_rect.centery = time_label_absolute_rect.centery
            screen_surface.blit(period_icon_to_draw_surface, icon_absolute_rect)
        elif DEBUG_VERBOSE:
            logger.debug(f"Icona per il periodo '{current_day_period_name}' non trovata o non renderizzata.")

    # --- 3. Disegno Barre dei Bisogni ---
    if selected_character_to_display and \
       bottom_panel_gui_obj and \
       default_ui_font and \
       hasattr(selected_character_to_display, 'needs') and \
       selected_character_to_display.needs:
        
        # Punto di partenza assoluto per la prima barra dei bisogni
        start_x_for_bars_absolute = panel_abs_x + needs_bars_start_x_in_panel
        current_draw_y_absolute = panel_abs_y + needs_bars_start_y_in_panel
        
        icon_width, icon_height = need_icon_dimensions

        for need_info in NEED_DISPLAY_ORDER_AND_INFO:
            need_attribute_name = need_info["attr"]
            # La chiave per recuperare la Surface dell'icona da loaded_icons_map
            icon_map_key_to_retrieve = need_info["icon_key_for_map"] 
            show_text_label = need_info.get("show_label", False)
            need_text_label_string = need_info.get("label", need_attribute_name.capitalize())

            if hasattr(selected_character_to_display.needs, need_attribute_name):
                need_object = getattr(selected_character_to_display.needs, need_attribute_name)
                
                current_item_drawing_start_x = start_x_for_bars_absolute

                # a. Disegna Icona (ora una Surface Unicode)
                icon_surface_to_blit = loaded_icons_map.get(icon_map_key_to_retrieve)
                if icon_surface_to_blit:
                    # Allinea verticalmente l'icona con la barra del bisogno
                    icon_y_position = current_draw_y_absolute + (NEEDS_BAR_HEIGHT - icon_height) // 2
                    screen_surface.blit(icon_surface_to_blit, (current_item_drawing_start_x, icon_y_position))
                current_item_drawing_start_x += icon_width + NEEDS_BAR_PADDING_X # Spazio dopo l'icona

                # b. (Opzionale) Disegna Etichetta Testuale del Bisogno
                if show_text_label:
                    label_text_surface = default_ui_font.render(f"{need_text_label_string}:", True, ui_current_text_color)
                    label_y_position = current_draw_y_absolute + (NEEDS_BAR_HEIGHT - label_text_surface.get_height()) // 2
                    screen_surface.blit(label_text_surface, (current_item_drawing_start_x, label_y_position))
                    current_item_drawing_start_x += label_text_surface.get_width() + NEEDS_BAR_PADDING_X

                # c. Disegna Barra del Bisogno
                value_percentage = need_object.get_value() / need_object.max_value
                bar_color_config_key = need_info["color_config_key"]
                bar_fill_color_actual = getattr(config, bar_color_config_key, need_info["fallback_color"])
                bar_background_color = tuple(max(0, c - 70) for c in bar_fill_color_actual) # Sfondo più scuro
                
                # Disegna sfondo barra
                pygame.draw.rect(screen_surface, bar_background_color, 
                                 (current_item_drawing_start_x, current_draw_y_absolute, NEEDS_BAR_WIDTH, NEEDS_BAR_HEIGHT))
                
                # Disegna barra del valore attuale
                current_bar_fill_actual_width = int(NEEDS_BAR_WIDTH * value_percentage)
                if current_bar_fill_actual_width > 0:
                    pygame.draw.rect(screen_surface, bar_fill_color_actual, 
                                     (current_item_drawing_start_x, current_draw_y_absolute, current_bar_fill_actual_width, NEEDS_BAR_HEIGHT))
                
                # Disegna bordo attorno alla barra
                bar_border_color_actual = getattr(config, 'UI_NEEDS_BAR_BORDER_COLOR', (50,50,50))
                pygame.draw.rect(screen_surface, bar_border_color_actual, 
                                 (current_item_drawing_start_x, current_draw_y_absolute, NEEDS_BAR_WIDTH, NEEDS_BAR_HEIGHT), 1)
                
                current_item_drawing_start_x += NEEDS_BAR_WIDTH + NEEDS_BAR_PADDING_X # Spazio dopo la barra

                # d. (Opzionale) Disegna Testo Valore Percentuale o Numerico
                if getattr(config, "UI_SHOW_NEED_VALUE_TEXT", True):
                    value_display_string = f"{need_object.get_value():.0f}%" if need_object.max_value == 100 else f"{need_object.get_value():.0f}/{need_object.max_value:.0f}"
                    value_text_surface_rendered = default_ui_font.render(value_display_string, True, ui_current_text_color)
                    value_text_y_position = current_draw_y_absolute + (NEEDS_BAR_HEIGHT - value_text_surface_rendered.get_height()) // 2
                    screen_surface.blit(value_text_surface_rendered, (current_item_drawing_start_x, value_text_y_position))

                # Aggiorna la posizione Y per la prossima barra
                current_draw_y_absolute += NEEDS_BAR_HEIGHT + NEEDS_BAR_PADDING_Y
            else:
                if DEBUG_VERBOSE: 
                    logger.warning(f"UTILS: NPC selezionato ({selected_character_to_display.name}) non ha il bisogno '{need_attribute_name}' nel suo NeedsComponent o NeedsComponent non è inizializzato.")
    
    elif selected_character_to_display and \
         (not hasattr(selected_character_to_display, 'needs') or not selected_character_to_display.needs) and \
         DEBUG_VERBOSE:
        logger.warning(f"UTILS: NPC selezionato ({selected_character_to_display.name}) non ha un NeedsComponent valido per disegnare le barre.")

def get_sprite_from_blueprint(object_blueprint: Dict[str, Any], 
                              sprite_sheet_manager_instance: 'SpriteSheetManager') -> Optional[pygame.Surface]:
    """
    Estrae una singola sprite Surface basandosi sulle informazioni di un object blueprint
    e uno SpriteSheetManager.

    Args:
        object_blueprint: Il dizionario del blueprint per l'oggetto.
                          Si aspetta chiavi come "sprite_sheet_key" e "sprite_rect_in_sheet".
        sprite_sheet_manager_instance: L'istanza di SpriteSheetManager.

    Returns:
        Optional[pygame.Surface]: La Surface dello sprite se trovato, altrimenti None.
    """
    if not object_blueprint or not sprite_sheet_manager_instance:
        logger.warning("get_sprite_from_blueprint: blueprint o sprite_sheet_manager mancanti.")
        return None

    sheet_key = object_blueprint.get("sprite_sheet_key")
    rect_in_sheet_data = object_blueprint.get("sprite_rect_in_sheet") # Dovrebbe essere [x, y, w, h]

    if not sheet_key:
        logger.warning(f"get_sprite_from_blueprint: 'sprite_sheet_key' non trovato nel blueprint: {object_blueprint.get('id', 'ID Sconosciuto')}")
        return None
    
    if not rect_in_sheet_data or not isinstance(rect_in_sheet_data, list) or len(rect_in_sheet_data) != 4:
        logger.warning(f"get_sprite_from_blueprint: 'sprite_rect_in_sheet' non valido o mancante per blueprint: {object_blueprint.get('id', 'ID Sconosciuto')}")
        return None

    # Lo SpriteSheetManager.get_sprite si aspetta indici di frame, non coordinate pixel.
    # Dobbiamo convertire o assicurarci che il blueprint contenga gli indici corretti
    # O, più semplicemente, se SpriteSheetManager può estrarre un rettangolo specifico.

    # Il tuo SpriteSheetManager.get_sprite(sheet_key, frame_x_index, frame_y_index)
    # si aspetta indici di frame.
    # Se "sprite_rect_in_sheet" nel blueprint contiene le coordinate x,y,w,h *pixel* sullo sheet,
    # allora dobbiamo usare un metodo diverso o adattare SpriteSheetManager.
    #
    # Assumiamo per ora che il tuo SpriteSheetManager abbia un modo (o che lo aggiungiamo)
    # per estrarre una regione specifica, o che "sprite_rect_in_sheet" in realtà
    # contenga qualcosa che può essere convertito in indici di frame.
    #
    # SOLUZIONE PIÙ DIRETTA: SpriteSheetManager dovrebbe avere un metodo
    # per prendere un rettangolo pixel esatto. Se non ce l'ha, lo implementiamo lì.
    #
    # Per ora, proviamo a fare un'ipotesi: se `sprite_rect_in_sheet` definisce un singolo frame
    # e il tuo `SpriteSheetManager` ha già caricato lo sheet e conosce le dimensioni dei frame,
    # potremmo calcolare l'indice.
    # Ma è più pulito se SpriteSheetManager ha un metodo come `get_sprite_by_rect`.

    # >>> Modifichiamo SpriteSheetManager per aggiungere get_sprite_by_pixel_rect <<<
    # Vai in asset_manager.py e aggiungi questo metodo a SpriteSheetManager:
    """
    # In SpriteSheetManager (asset_manager.py)
    def get_sprite_by_pixel_rect(self, sheet_key: str, rect_on_sheet: pygame.Rect) -> Optional[pygame.Surface]:
        if sheet_key not in self.sprite_sheets:
            # ... (log error) ...
            return None
        sheet = self.sprite_sheets[sheet_key]
        if rect_on_sheet.right > sheet.get_width() or rect_on_sheet.bottom > sheet.get_height() or \
           rect_on_sheet.left < 0 or rect_on_sheet.top < 0:
            # ... (log error: rect out of bounds) ...
            return None
        
        sprite_surface = pygame.Surface(rect_on_sheet.size, pygame.SRCALPHA)
        sprite_surface.blit(sheet, (0, 0), rect_on_sheet)
        return sprite_surface
    """
    # Dopo aver aggiunto quel metodo a SpriteSheetManager, possiamo usarlo qui:
    try:
        sprite_rect = pygame.Rect(rect_in_sheet_data[0], rect_in_sheet_data[1], rect_in_sheet_data[2], rect_in_sheet_data[3])
        
        # Verifica se SpriteSheetManager ha il metodo get_sprite_by_pixel_rect
        if hasattr(sprite_sheet_manager_instance, 'get_sprite_by_pixel_rect'):
            sprite_surface = sprite_sheet_manager_instance.get_sprite_by_pixel_rect(sheet_key, sprite_rect)
            if sprite_surface:
                logger.debug(f"Sprite per '{object_blueprint.get('id')}' caricato da sheet '{sheet_key}' usando rect {sprite_rect}")
                return sprite_surface
            else:
                logger.warning(f"Fallito get_sprite_by_pixel_rect per sheet '{sheet_key}', rect {sprite_rect}")
                return None
        else:
            # Fallback se get_sprite_by_pixel_rect non esiste (NON IDEALE, ma per far procedere)
            # Questo assume che sprite_rect_in_sheet contenga l'indice x,y del frame
            # e che le dimensioni del frame siano quelle di default dello sheet.
            # Questo probabilmente NON è corretto per oggetti con dimensioni diverse dai personaggi.
            logger.warning(f"Metodo 'get_sprite_by_pixel_rect' non trovato in SpriteSheetManager. "
                                      f"Tentativo di fallback con get_sprite usando indici (potrebbe fallire).")
            frame_dims = sprite_sheet_manager_instance.get_frame_dimensions(sheet_key)
            if frame_dims and frame_dims[0] > 0 and frame_dims[1] > 0:
                frame_x_index = rect_in_sheet_data[0] // frame_dims[0]
                frame_y_index = rect_in_sheet_data[1] // frame_dims[1]
                sprite_surface = sprite_sheet_manager_instance.get_sprite(sheet_key, frame_x_index, frame_y_index)
                if sprite_surface:
                    logger.debug(f"Sprite per '{object_blueprint.get('id')}' caricato da sheet '{sheet_key}' usando indici ({frame_x_index},{frame_y_index})")
                    return sprite_surface
            
            logger.error(f"Impossibile estrarre lo sprite per '{object_blueprint.get('id')}' da sheet '{sheet_key}' con dati {rect_in_sheet_data}")
            return None

    except Exception as e:
        logger.error(f"Errore in get_sprite_from_blueprint per '{object_blueprint.get('id')}': {e}", exc_info=True)
        return None
