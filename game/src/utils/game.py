# simai/game/game_utils.py
# MODIFIED: Moved interpolate_color and get_need_bar_color definition before their first call.
# MODIFIED: Removed ConfigPlaceholder; critical config import now causes sys.exit().
# MODIFIED: Made debug/warning prints conditional on config.DEBUG_AI_ACTIVE.

import pygame
import json
import os
import math
import random 
import pygame_gui 
import sys 
from collections import deque # Importa deque se lo usi per find_path_to_target
from typing import Optional

try:
    from game import config 
except ImportError as e:
    print(f"CRITICAL ERROR (game_utils.py): Could not import 'game.config': {e}")
    print("Ensure 'game.config' is accessible. SimAI cannot run without its configuration.")
    sys.exit()

DEBUG_VERBOSE = getattr(config, 'DEBUG_AI_ACTIVE', False)

try:
    import cairosvg
    from io import BytesIO 
    CAIROSVG_AVAILABLE = True
except ImportError:
    if DEBUG_VERBOSE: print("WARNING (game_utils.py): Library 'cairosvg' not found. SVG file loading will fail.")
    CAIROSVG_AVAILABLE = False

OBJECT_BLUEPRINTS_DATA = {}

def load_object_blueprints(filename="object_blueprints.json"):
    global OBJECT_BLUEPRINTS_DATA
    # Costruisci il percorso corretto per il file JSON
    # Assumendo che la directory 'data' sia dentro 'assets'
    data_path = os.path.join(config.BASE_ASSET_PATH, "data", filename)
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            OBJECT_BLUEPRINTS_DATA = json.load(f)
        if getattr(config, 'DEBUG_AI_ACTIVE', False): # Usa config per il flag di debug
            print(f"OBJECTS: Caricati {len(OBJECT_BLUEPRINTS_DATA)} blueprint di oggetti da {data_path}")
    except FileNotFoundError:
        print(f"ERRORE OGGETTI: File blueprint '{data_path}' non trovato.")
        OBJECT_BLUEPRINTS_DATA = {} # Resetta se il file non è trovato
    except json.JSONDecodeError as e:
        print(f"ERRORE OGGETTI: Errore nel parsing del JSON '{data_path}': {e}")
        OBJECT_BLUEPRINTS_DATA = {}
    except Exception as e:
        print(f"ERRORE OGGETTI: Errore imprevisto durante il caricamento dei blueprint: {e}")
        OBJECT_BLUEPRINTS_DATA = {}
    return OBJECT_BLUEPRINTS_DATA # Restituisci i dati caricati

# Potresti voler una funzione per accedere ai dati
def get_object_blueprint(type_key):
    return OBJECT_BLUEPRINTS_DATA.get(type_key)

def load_image(filename_with_ext: str, target_size: tuple = None, base_path: str = "."):
    full_path = os.path.join(base_path, filename_with_ext)
    if not os.path.exists(full_path):
        if DEBUG_VERBOSE: print(f"LOAD_IMAGE WARNING: Image file NOT FOUND at '{full_path}'")
        return None
    try:
        image_surface = None
        if filename_with_ext.lower().endswith(".svg"):
            if CAIROSVG_AVAILABLE:
                out_w = target_size[0] if target_size and target_size[0] is not None else None
                out_h = target_size[1] if target_size and target_size[1] is not None else None
                png_data = cairosvg.svg2png(url=full_path, output_width=out_w, output_height=out_h)
                png_file_like_object = BytesIO(png_data)
                image_surface = pygame.image.load(png_file_like_object, filename_with_ext)
            else:
                if DEBUG_VERBOSE: print(f"LOAD_IMAGE ERROR: 'cairosvg' not available for SVG: {filename_with_ext}.")
                return None
        else: 
            image_surface = pygame.image.load(full_path)
        
        if image_surface:
            if image_surface.get_alpha() is not None:
                 image_surface = image_surface.convert_alpha()
            else:
                 image_surface = image_surface.convert()
            if target_size and (image_surface.get_width() != target_size[0] or image_surface.get_height() != target_size[1]):
                image_surface = pygame.transform.smoothscale(image_surface, target_size)
        return image_surface
    except Exception as e: 
        if DEBUG_VERBOSE: print(f"LOAD_IMAGE ERROR loading '{filename_with_ext}' from '{full_path}': {e}")
        return None

def load_all_game_assets():
    loaded_icons_map = {}
    icon_size_time_btn = (30, 30); icon_size_prd = (28, 28); icon_size_nd = (22, 22)
    placeholder_sfc = pygame.Surface(icon_size_nd, pygame.SRCALPHA)
    pygame.draw.circle(placeholder_sfc, (100,100,100), (icon_size_nd[0]//2, icon_size_nd[1]//2), icon_size_nd[0]//2 - 1)
    if hasattr(config, 'RED'):
        pygame.draw.line(placeholder_sfc, config.RED, (3,3), (icon_size_nd[0]-3, icon_size_nd[1]-3), 1)
        pygame.draw.line(placeholder_sfc, config.RED, (3,icon_size_nd[1]-3), (icon_size_nd[0]-3, 3), 1)
    
    icon_files_cfg_map = {
        "pause":"pause-circle.svg", "speed_1":"1-circle.svg", "speed_2":"2-circle.svg", "speed_3":"3-circle.svg",
        "speed_4":"4-circle.svg", "speed_5":"5-circle.svg", "dawn":"sunrise.svg", "noon":"sun.svg",
        "sunset":"sunset.svg", "night":"moon.svg", "bladder":"toilet.svg", "hunger":"hunger.svg",
        "energy":"battery-charging.svg", "fun":"fun.svg", "social":"social.svg", "hygiene":"shower.svg",
        "intimacy": "intimacy.svg"}
    icon_sizes_cfg_map = {n: icon_size_nd for n in ["bladder","hunger","energy","fun","social","hygiene","intimacy"]}
    icon_sizes_cfg_map.update({n: icon_size_time_btn for n in ["pause","speed_1","speed_2","speed_3","speed_4","speed_5"]})
    icon_sizes_cfg_map.update({n: icon_size_prd for n in ["dawn","noon","sunset","night"]})
    
    for name, filename in icon_files_cfg_map.items():
        size = icon_sizes_cfg_map.get(name, icon_size_nd)
        loaded_icons_map[name] = load_image(filename, size, base_path=config.ICON_PATH)
        if loaded_icons_map[name] is None: loaded_icons_map[name] = placeholder_sfc
    
    speed_control_icons = [loaded_icons_map.get(s) for s in ["pause","speed_1","speed_2","speed_3","speed_4","speed_5"]]
    need_bar_icon_size_val = loaded_icons_map.get("hunger").get_size() if loaded_icons_map.get("hunger") else (22,22)
    
    game_bed_parts = {"base": None, "cover": None, "full_spritesheet_for_debug": None} 
    bed_spritesheet_filename = "double-blue.png" 
    bed_spritesheet_path = getattr(config, 'FURNITURE_IMAGE_PATH', os.path.join(getattr(config, 'IMAGE_PATH', 'assets/images'), 'furnitures'))
    full_bed_spritesheet_surf = load_image(bed_spritesheet_filename, None, base_path=bed_spritesheet_path)
    game_bed_parts["full_spritesheet_for_debug"] = full_bed_spritesheet_surf

    if full_bed_spritesheet_surf:
        base_coords = getattr(config, 'BED_SPRITESHEET_BASE_RECT_COORDS', (0, 0, 64, 81)) 
        base_surf = pygame.Surface((base_coords[2], base_coords[3]), pygame.SRCALPHA)
        base_surf.blit(full_bed_spritesheet_surf, (0,0), base_coords)
        game_bed_parts["base"] = base_surf

        cover_coords = getattr(config, 'BED_SPRITESHEET_COVER_RECT_COORDS', (0, 106, 64, 22))
        cover_surf = pygame.Surface((cover_coords[2], cover_coords[3]), pygame.SRCALPHA)
        cover_surf.blit(full_bed_spritesheet_surf, (0,0), cover_coords)
        game_bed_parts["cover"] = cover_surf
    else:
        if DEBUG_VERBOSE: print(f"GAME_UTILS WARNING: Bed spritesheet '{bed_spritesheet_filename}' not loaded. Using fallback color.")
        placeholder_base_w = getattr(config, 'BED_SPRITESHEET_BASE_RECT_COORDS', (0,0,64,81))[2]
        placeholder_base_h = getattr(config, 'BED_SPRITESHEET_BASE_RECT_COORDS', (0,0,64,81))[3]
        placeholder_base = pygame.Surface((placeholder_base_w, placeholder_base_h), pygame.SRCALPHA)
        placeholder_base.fill(getattr(config,'BED_COLOR_FALLBACK',(100,70,30)))
        game_bed_parts["base"] = placeholder_base
    
    return loaded_icons_map, speed_control_icons, game_bed_parts, need_bar_icon_size_val

def setup_pathfinding_grid(list_of_obstacle_rects: list) -> list:
    path_grid = [[1 for _ in range(config.GRID_WIDTH)] for _ in range(config.GRID_HEIGHT)]
    if list_of_obstacle_rects:
        for rect_obj_instance in list_of_obstacle_rects:
            if rect_obj_instance is None: continue
            start_gx, start_gy = world_to_grid(rect_obj_instance.left, rect_obj_instance.top) 
            end_gx, end_gy = world_to_grid(rect_obj_instance.right - 1, rect_obj_instance.bottom - 1) 
            for gy_idx in range(start_gy, end_gy + 1):
                for gx_idx in range(start_gx, end_gx + 1):
                    if 0 <= gx_idx < config.GRID_WIDTH and 0 <= gy_idx < config.GRID_HEIGHT:
                        path_grid[gy_idx][gx_idx] = 0 
    return path_grid

def setup_gui_elements(ui_manager_param: pygame_gui.UIManager, 
                       character_list_param: list, 
                       initial_selected_idx_param: int, 
                       icon_size_time_button_tuple_param: tuple, 
                       panel_height_param: int, 
                       screen_width_param: int, 
                       screen_height_param: int 
                       ) -> dict:
    gui_elems = {} 
    gui_elems['bottom_panel'] = pygame_gui.elements.UIPanel(
        relative_rect=pygame.Rect((0, screen_height_param - panel_height_param), 
                                  (screen_width_param, panel_height_param)), 
        manager=ui_manager_param,
        object_id="@bottom_panel"
    )
    btn_w, btn_h = icon_size_time_button_tuple_param[0], icon_size_time_button_tuple_param[1]
    btn_m = 5 
    time_ctrl_y = screen_height_param - panel_height_param - btn_h - btn_m 
    time_btn_rects_list = []
    current_x_button = btn_m 
    for _ in range(6): 
        rect = pygame.Rect(current_x_button, time_ctrl_y, btn_w, btn_h)
        time_btn_rects_list.append(rect)
        current_x_button += btn_w + btn_m
    gui_elems['time_button_rects'] = time_btn_rects_list
    time_label_x_start = current_x_button + 10 
    time_label_width = screen_width_param - time_label_x_start - btn_m 
    gui_elems['time_label'] = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((time_label_x_start, time_ctrl_y), (time_label_width, btn_h)),
        text="Loading...", 
        manager=ui_manager_param, 
        object_id="#time_label"
    )
    panel_margin_local = 10 
    char_info_width_local = screen_width_param // 3 
    gui_elems['char_status_label'] = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect(
            (panel_margin_local, panel_margin_local), 
            (char_info_width_local - panel_margin_local * 2, 30)
        ),
        text=f"Displaying: {character_list_param[initial_selected_idx_param].name} (Space)", 
        manager=ui_manager_param,
        container=gui_elems['bottom_panel'] 
    )
    gui_elems['action_label'] = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect(
            (panel_margin_local, gui_elems['char_status_label'].relative_rect.bottom + 5),
            (char_info_width_local - panel_margin_local * 2, 30)
        ),
        text="",
        manager=ui_manager_param,
        container=gui_elems['bottom_panel']
    )
    gui_elems['pregnancy_label'] = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect(
            (panel_margin_local, gui_elems['action_label'].relative_rect.bottom + 5),
            (char_info_width_local - panel_margin_local * 2, 30)
        ),
        text="", 
        manager=ui_manager_param, 
        container=gui_elems['bottom_panel'],
        visible=False 
    )
    gui_elems['needs_bar_area_x_in_panel'] = panel_margin_local + char_info_width_local + 10 
    gui_elems['needs_bar_area_y_in_panel'] = panel_margin_local + 5
    return gui_elems

# --- Funzioni di utility per colori e tempo ---
def interpolate_color(color1: tuple, color2: tuple, factor: float) -> tuple:
    """Linearly interpolates between two RGB colors."""
    factor = max(0.0, min(1.0, factor))
    r = int(color1[0] * (1.0 - factor) + color2[0] * factor)
    g = int(color1[1] * (1.0 - factor) + color2[1] * factor)
    b = int(color1[2] * (1.0 - factor) + color2[2] * factor)
    return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))

def get_need_bar_color(goodness_factor): 
    if goodness_factor < 0.25: 
        return interpolate_color(config.NEED_COLOR_VERY_BAD, config.NEED_COLOR_BAD, goodness_factor / 0.25)
    elif goodness_factor < 0.5: 
        return interpolate_color(config.NEED_COLOR_BAD, config.NEED_COLOR_MEDIUM, (goodness_factor - 0.25) / 0.25)
    elif goodness_factor < 0.75: 
        return interpolate_color(config.NEED_COLOR_MEDIUM, config.NEED_COLOR_OKAY, (goodness_factor - 0.5) / 0.25)
    else: 
        return interpolate_color(config.NEED_COLOR_OKAY, config.NEED_COLOR_GOOD, (goodness_factor - 0.75) / 0.25)

def get_sky_color_and_period_info(precise_game_hour: float) -> tuple:
    hour_for_sky_color = precise_game_hour % getattr(config, 'GAME_HOURS_IN_DAY', 28)
    sky_keyframes_list = getattr(config, 'SKY_KEYFRAMES', [])
    if not sky_keyframes_list or len(sky_keyframes_list) < 2:
        default_sky_color = (135, 206, 235) 
        default_period_name = "Daytime" 
        default_ui_text_color = getattr(config, 'TEXT_COLOR_DARK', (0,0,0))
        if DEBUG_VERBOSE: print(f"GAME_UTILS WARNING (get_sky_color): SKY_KEYFRAMES not properly defined in config. Using defaults.")
        return default_sky_color, default_period_name, default_ui_text_color
    
    current_sky_color = sky_keyframes_list[0][1] 
    for i in range(len(sky_keyframes_list)):
        h1, c1 = sky_keyframes_list[i]
        if i == len(sky_keyframes_list) - 1: 
            if hour_for_sky_color >= h1: current_sky_color = c1
            break 
        h2, c2 = sky_keyframes_list[i+1]
        if h1 <= hour_for_sky_color < h2:
            segment_duration = h2 - h1
            if segment_duration <= 0: current_sky_color = c1
            else:
                time_into_segment = hour_for_sky_color - h1
                interpolation_factor = time_into_segment / segment_duration
                current_sky_color = interpolate_color(c1, c2, interpolation_factor) # Chiamata corretta ora
            break 
            
    current_game_hour_int = int(precise_game_hour) % getattr(config, 'GAME_HOURS_IN_DAY', 28)
    period_name = "Night" 
    if 7 <= current_game_hour_int < 12: period_name = "Morning"
    elif 12 <= current_game_hour_int < 18: period_name = "Afternoon"
    elif 18 <= current_game_hour_int < 22: period_name = "Evening"
    brightness = (current_sky_color[0]*0.299 + current_sky_color[1]*0.587 + current_sky_color[2]*0.114)
    ui_text_color = getattr(config, 'TEXT_COLOR_DARK', (0,0,0)) if brightness > 140 \
                    else getattr(config, 'TEXT_COLOR_LIGHT', (255,255,255))
    return current_sky_color, period_name, ui_text_color

def world_to_grid(world_x: float, world_y: float) -> tuple:
    tile_s = getattr(config, 'TILE_SIZE', 32)
    grid_w = getattr(config, 'GRID_WIDTH', 1024 // tile_s if tile_s > 0 else 32) 
    grid_h = getattr(config, 'GRID_HEIGHT', 768 // tile_s if tile_s > 0 else 24) 
    if tile_s <= 0: 
        if DEBUG_VERBOSE: print("GAME_UTILS ERROR (world_to_grid): TILE_SIZE is invalid (<=0). Returning (0,0).")
        return (0, 0) 
    grid_x = int(world_x // tile_s)
    grid_y = int(world_y // tile_s)
    grid_x = max(0, min(grid_w - 1, grid_x)) 
    grid_y = max(0, min(grid_h - 1, grid_y)) 
    return grid_x, grid_y

def grid_to_world_center(grid_x: int, grid_y: int) -> tuple:
    tile_s = getattr(config, 'TILE_SIZE', 32)
    world_x = grid_x * tile_s + tile_s / 2.0 
    world_y = grid_y * tile_s + tile_s / 2.0
    return world_x, world_y

def update_game_time_state(
    time_delta_seconds: float, 
    current_speed_idx: int,
    current_total_sim_hours_elapsed_val: float,
    current_hour_float_val: float, 
    current_day_val: int,
    current_month_val: int,
    current_year_val: int
) -> tuple:
    hours_advanced_this_frame = 0.0
    if current_speed_idx > 0:
        seconds_per_game_hour = config.TIME_SPEED_SETTINGS[current_speed_idx]
        if seconds_per_game_hour > 0 and seconds_per_game_hour != float('inf'):
            hours_advanced_this_frame = time_delta_seconds / seconds_per_game_hour
    new_total_sim_hours = current_total_sim_hours_elapsed_val
    new_hour_float = current_hour_float_val 
    new_day = current_day_val
    new_month = current_month_val
    new_year = current_year_val
    if hours_advanced_this_frame > 0:
        new_total_sim_hours = current_total_sim_hours_elapsed_val + hours_advanced_this_frame
        total_hours_from_epoch = config.INITIAL_START_HOUR + new_total_sim_hours
        new_hour_float = total_hours_from_epoch % config.GAME_HOURS_IN_DAY
        total_days_passed_from_epoch = int(total_hours_from_epoch / config.GAME_HOURS_IN_DAY)
        new_year = 1 + total_days_passed_from_epoch // config.GAME_DAYS_PER_YEAR
        days_into_this_year = total_days_passed_from_epoch % config.GAME_DAYS_PER_YEAR
        new_month = 1 + days_into_this_year // config.DAYS_PER_MONTH
        new_day = 1 + days_into_this_year % config.DAYS_PER_MONTH
    return (hours_advanced_this_frame, int(new_hour_float), 
            new_day, new_month, new_year, 
            new_total_sim_hours, new_hour_float)

def draw_all_manual_ui_elements(screen_surface: pygame.Surface, loaded_icons_map: dict, 
                                speed_button_icons: list, current_selected_speed_idx: int, 
                                time_label_gui_obj: pygame_gui.elements.UILabel, current_day_period_name: str, 
                                selected_character_to_display: 'Character', 
                                bottom_panel_gui_obj: pygame_gui.elements.UIPanel, 
                                needs_bars_start_x_in_panel: int, needs_bars_start_y_in_panel: int, 
                                ui_current_text_color: tuple, default_ui_font: pygame.font.Font, 
                                time_control_buttons_rect_list: list, need_icon_dimensions: tuple):
    if time_control_buttons_rect_list and speed_button_icons:
        for idx, button_r in enumerate(time_control_buttons_rect_list):
            if idx < len(speed_button_icons) and speed_button_icons[idx]: screen_surface.blit(speed_button_icons[idx], button_r.topleft)
            if idx == current_selected_speed_idx: 
                pygame.draw.rect(screen_surface, (255,255,0), button_r, 2)
    
    period_icon_name_map = {"Morning":"dawn","Afternoon":"noon","Evening":"sunset","Night":"night"}
    period_icon_surface = loaded_icons_map.get(period_icon_name_map.get(current_day_period_name))

    if period_icon_surface and time_label_gui_obj: 
        period_icon_r = period_icon_surface.get_rect(centery=time_label_gui_obj.rect.centery)
        period_icon_r.right = time_label_gui_obj.rect.left - 5
        screen_surface.blit(period_icon_surface, period_icon_r)

    if selected_character_to_display and bottom_panel_gui_obj and \
       needs_bars_start_x_in_panel is not None and needs_bars_start_y_in_panel is not None:
        
        bar_max_width = 100; bar_height = 15; bar_vertical_spacing = 5 
        icon_w, icon_h = need_icon_dimensions
        col1_x_abs_screen = bottom_panel_gui_obj.rect.left + needs_bars_start_x_in_panel
        bar_start_y_abs_screen = bottom_panel_gui_obj.rect.top + needs_bars_start_y_in_panel
        col_h_space_between = icon_w + 5 + bar_max_width + 15

        needs_display_data_list = [
            ("Bladder", "bladder", selected_character_to_display.bladder), ("Hunger", "hunger", selected_character_to_display.hunger), 
            ("Energy", "energy", selected_character_to_display.energy),("Fun", "fun", selected_character_to_display.fun), 
            ("Social", "social", selected_character_to_display.social), ("Hygiene", "hygiene", selected_character_to_display.hygiene),
            ("Intimacy", "intimacy", selected_character_to_display.intimacy)
        ]
        cols_layout_data = [needs_display_data_list[0:3], needs_display_data_list[3:6], needs_display_data_list[6:7]]
        current_col_x_to_draw_at = col1_x_abs_screen
        for col_idx_val, needs_in_this_col in enumerate(cols_layout_data):
            current_need_y_to_draw_at = bar_start_y_abs_screen
            if col_idx_val == 0: current_col_x_to_draw_at = col1_x_abs_screen
            elif col_idx_val == 1: current_col_x_to_draw_at = col1_x_abs_screen + col_h_space_between
            elif col_idx_val == 2: current_col_x_to_draw_at = col1_x_abs_screen + 2 * col_h_space_between
            for _, icon_key_name, need_instance in needs_in_this_col:
                if not need_instance: continue
                icon_surf = loaded_icons_map.get(icon_key_name)
                color_goodness_factor = need_instance.get_goodness_factor()
                bar_actual_color = get_need_bar_color(color_goodness_factor)
                icon_display_rect=pygame.Rect(current_col_x_to_draw_at, current_need_y_to_draw_at + (bar_height - icon_h) // 2, icon_w, icon_h)
                if icon_surf: screen_surface.blit(icon_surf, icon_display_rect.topleft)
                bar_draw_start_x = icon_display_rect.right + 5
                bar_fill_rect = pygame.Rect(bar_draw_start_x, current_need_y_to_draw_at, bar_max_width, bar_height)
                pygame.draw.rect(screen_surface, bar_actual_color, bar_fill_rect)
                border_rect = pygame.Rect(bar_draw_start_x, current_need_y_to_draw_at, bar_max_width, bar_height)
                pygame.draw.rect(screen_surface, config.NEED_BAR_BORDER_COLOR, border_rect, 1)
                current_need_y_to_draw_at += bar_height + bar_vertical_spacing

def occupy_bed_slot_for_character(game_state: 'GameState', character: 'Character', slot_index: int) -> bool:
    """Tenta di occupare uno slot del letto per il personaggio."""
    if slot_index == 0 and not game_state.bed_slot_1_occupied_by:
        game_state.bed_slot_1_occupied_by = character.uuid
        character.bed_object_id = "main_bed" # o l'ID corretto del letto
        character.bed_slot_index = 0
        if DEBUG_VERBOSE: print(f"UTILS: {character.name} occupied bed slot 0.")
        return True
    elif slot_index == 1 and not game_state.bed_slot_2_occupied_by:
        game_state.bed_slot_2_occupied_by = character.uuid
        character.bed_object_id = "main_bed"
        character.bed_slot_index = 1
        if DEBUG_VERBOSE: print(f"UTILS: {character.name} occupied bed slot 1.")
        return True
    if DEBUG_VERBOSE: print(f"UTILS WARN: {character.name} failed to occupy bed slot {slot_index}.")
    return False
def print_debug_grid(grid_map_data, start_pos_grid=None, end_pos_grid=None):
    if not grid_map_data or not grid_map_data[0]:
        print("DEBUG GRID: Mappa vuota o non valida.")
        return
    print("\n--- GRIGLIA DI PATHFINDING (DEBUG) ---")
    for r_idx, row in enumerate(grid_map_data):
        row_str = []
        for c_idx, cell in enumerate(row):
            char_to_print = str(cell)
            if start_pos_grid and start_pos_grid == (c_idx, r_idx):
                char_to_print = "S" # Start
            elif end_pos_grid and end_pos_grid == (c_idx, r_idx):
                char_to_print = "E" # End
            elif cell == 0:
                char_to_print = "#" # Ostacolo
            else:
                char_to_print = "." # Calpestabile
            row_str.append(char_to_print)
        print(" ".join(row_str))
    print("--- FINE GRIGLIA ---")

def free_bed_slot_for_character(game_state: 'GameState', character: 'Character'):
    """Libera lo slot del letto precedentemente occupato dal personaggio."""
    if character.bed_object_id == "main_bed": # Controlla se era effettivamente su questo letto
        if character.bed_slot_index == 0 and game_state.bed_slot_1_occupied_by == character.uuid:
            game_state.bed_slot_1_occupied_by = None
            if DEBUG_VERBOSE: print(f"UTILS: {character.name} freed bed slot 0.")
        elif character.bed_slot_index == 1 and game_state.bed_slot_2_occupied_by == character.uuid:
            game_state.bed_slot_2_occupied_by = None
            if DEBUG_VERBOSE: print(f"UTILS: {character.name} freed bed slot 1.")
    character.bed_object_id = None
    character.bed_slot_index = -1 # o None
    character.is_on_bed = False

def is_close_to_point(point1: tuple[float, float], point2: tuple[float, float], tolerance: float) -> bool:
    """Controlla se due punti sono vicini entro una certa tolleranza."""
    if point1 is None or point2 is None:
        return False
    distance_sq = (point1[0] - point2[0])**2 + (point1[1] - point2[1])**2
    return distance_sq <= tolerance**2

def are_coords_equal(coord1: Optional[tuple[int, int]], coord2: Optional[tuple[int, int]], tolerance: float = 1.0) -> bool:
    """Controlla se due coordinate (tuple) sono uguali entro una piccola tolleranza."""
    if coord1 is None or coord2 is None:
        return coord1 == coord2 # Entrambi None sono considerati uguali, uno None e l'altro no -> diversi
    return math.isclose(coord1[0], coord2[0], abs_tol=tolerance) and \
           math.isclose(coord1[1], coord2[1], abs_tol=tolerance)
class AStarNode:
    """Nodo per l'algoritmo A*."""
    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position # Tupla (x, y) in coordinate della GRIGLIA
        self.g = 0 # Costo dal nodo di partenza al nodo corrente
        self.h = 0 # Costo stimato (euristica) dal nodo corrente al nodo di destinazione
        self.f = 0 # Costo totale (g + h)

    def __eq__(self, other):
        return self.position == other.position

    def __hash__(self):
        return hash(self.position)

    def __lt__(self, other): # Necessario per heapq
        return self.f < other.f

    # Metodo per la serializzazione (opzionale, se vuoi salvare i path)
    def to_tuple(self) -> tuple:
        return self.position

    @classmethod
    def from_tuple(cls, pos_tuple, parent=None): # Opzionale
        return cls(parent, pos_tuple)


def find_path_to_target(
    character_obj, # Character instance (per la posizione iniziale)
    target_world_pos: tuple[int, int],
    grid_map_data: list[list[int]], # La griglia da setup_pathfinding_grid (0=ostacolo, 1=calpestabile)
    world_dynamic_obstacles: Optional[list[pygame.Rect]] = None # Opzionale, per NPC
) -> Optional[deque[AStarNode]]:
    """
    Trova un percorso usando A* dalla posizione del personaggio a target_world_pos.
    Restituisce una deque di nodi (in coordinate della GRIGLIA) o None.
    """
    if grid_map_data is None or not grid_map_data or not grid_map_data[0]:
        if DEBUG_VERBOSE: print("PATHFINDING ERROR: grid_map_data non valida.")
        return None

    start_grid_pos = world_to_grid(character_obj.rect.centerx, character_obj.rect.centery)
    end_grid_pos = world_to_grid(target_world_pos[0], target_world_pos[1])

    start_node = AStarNode(None, start_grid_pos)
    start_node.g = start_node.h = start_node.f = 0
    end_node = AStarNode(None, end_grid_pos)
    end_node.g = end_node.h = end_node.f = 0

    open_list = [] # Tratteremo questa lista come una coda di priorità (heapq sarebbe meglio per le prestazioni)
    closed_list_positions = set() # Usiamo un set di posizioni per controlli O(1)

    open_list.append(start_node)

    max_iterations = getattr(config, "ASTAR_MAX_ITERATIONS", 1000) # Limita le iterazioni
    iterations = 0

    while open_list and iterations < max_iterations:
        iterations += 1

        # Trova il nodo con il costo f più basso (simulazione heapq)
        current_node = open_list[0]
        current_index = 0
        for index, item in enumerate(open_list):
            if item.f < current_node.f:
                current_node = item
                current_index = index

        open_list.pop(current_index)
        closed_list_positions.add(current_node.position)

        if current_node == end_node:
            path = deque()
            current = current_node
            while current is not None:
                path.appendleft(current) # Aggiunge all'inizio per avere il path nell'ordine corretto
                current = current.parent
            if DEBUG_VERBOSE and len(path) > 0: print(f"PATHFINDING: Path found from {start_grid_pos} to {end_grid_pos}, length: {len(path)}")
            return path

        children = []
        # Adiacenti (incluse diagonali)
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

            # Assicurati che sia dentro i limiti della mappa
            if not (0 <= node_position[0] < len(grid_map_data[0]) and \
                    0 <= node_position[1] < len(grid_map_data)):
                continue

            # Assicurati che sia calpestabile sulla griglia statica
            if grid_map_data[node_position[1]][node_position[0]] == 0: # 0 è ostacolo
                continue

            # Qui potresti aggiungere controlli per ostacoli dinamici (altri NPC),
            # se world_dynamic_obstacles è fornito e vuoi che A* li eviti.
            # Questo rende A* più costoso.

            new_node = AStarNode(current_node, node_position)
            children.append(new_node)

        for child in children:
            if child.position in closed_list_positions:
                continue

            # Calcolo dei costi
            # Movimento diagonale costa di più (sqrt(2) ~ 1.414)
            cost_g = 1.414 if abs(child.position[0] - current_node.position[0]) == 1 and \
                              abs(child.position[1] - current_node.position[1]) == 1 else 1.0
            child.g = current_node.g + cost_g
            child.h = math.sqrt(((child.position[0] - end_node.position[0]) ** 2) + \
                                ((child.position[1] - end_node.position[1]) ** 2))
            child.f = child.g + child.h

            # Se il figlio è già nella open_list con un costo f minore, salta
            for open_node in open_list:
                if child == open_node and child.g >= open_node.g: # Confronta g per trovare il percorso più breve
                    break
            else: # Se il loop non è stato interrotto da break
                open_list.append(child)

    if DEBUG_VERBOSE: print(f"PATHFINDING WARN: No path found from {start_grid_pos} to {end_grid_pos} after {iterations} iterations.")
    return None # Nessun percorso trovato


def get_random_walkable_tile_in_radius(
    origin_world_pos: tuple[float, float],
    grid_map_data: list[list[int]],
    min_dist_tiles: int,
    max_dist_tiles: int,
    world_obstacles: Optional[list[pygame.Rect]] = None, # Potrebbe essere usato per controlli più fini
    max_attempts: int = 20
) -> Optional[tuple[int, int]]:
    """
    Trova una cella calpestabile casuale entro un raggio specificato (in coordinate del mondo).
    Restituisce le coordinate MONDO del centro della cella trovata, o None.
    """
    if grid_map_data is None or not grid_map_data or not grid_map_data[0]:
        return None

    origin_grid_x, origin_grid_y = world_to_grid(origin_world_pos[0], origin_world_pos[1])
    grid_width = len(grid_map_data[0])
    grid_height = len(grid_map_data)
    tile_size = getattr(config, 'TILE_SIZE', 32)

    for _ in range(max_attempts):
        angle = random.uniform(0, 2 * math.pi)
        distance_tiles = random.uniform(min_dist_tiles, max_dist_tiles)

        offset_x = int(round(math.cos(angle) * distance_tiles))
        offset_y = int(round(math.sin(angle) * distance_tiles))

        target_grid_x = origin_grid_x + offset_x
        target_grid_y = origin_grid_y + offset_y

        # Controlla limiti della griglia
        if not (0 <= target_grid_x < grid_width and 0 <= target_grid_y < grid_height):
            continue

        # Controlla se la cella è calpestabile
        if grid_map_data[target_grid_y][target_grid_x] == 1: # 1 è calpestabile
            # Qui potresti aggiungere un controllo più fine usando world_obstacles se necessario,
            # per assicurarti che il centro della cella non sia troppo vicino a un ostacolo.
            return grid_to_world_center(target_grid_x, target_grid_y)

    if DEBUG_VERBOSE:
        print(f"RANDOM_WALKABLE: Failed to find walkable tile near ({origin_grid_x},{origin_grid_y}) after {max_attempts} attempts.")
    return None
