# simai/game/game_utils.py
# MODIFIED: Made debug/warning prints conditional on config.DEBUG_AI_ACTIVE (or a similar general debug flag).
# MODIFIED: Removed ConfigPlaceholder.

import pygame
import os
import math
import random 
import pygame_gui 
import sys 

try:
    from game import config 
except ImportError as e:
    print(f"CRITICAL ERROR (game_utils.py): Could not import 'game.config': {e}")
    # Se config è critico per il funzionamento di base di game_utils, uscire.
    # Per ora, procediamo con un config placeholder minimale se l'utente vuole testare game_utils isolatamente,
    # ma questo NON dovrebbe accadere in un'esecuzione normale.
    class ConfigPlaceholder: # Placeholder minimale SOLO per attributi usati da game_utils
        DEBUG_AI_ACTIVE = True # Assumiamo True per vedere gli warning del placeholder
        ICON_PATH = "assets/images/icons" # Esempio
        IMAGE_PATH = "assets/images"
        FURNITURE_IMAGE_PATH = os.path.join(IMAGE_PATH, "furnitures")
        BED_SPRITESHEET_BASE_RECT_COORDS = (0, 0, 64, 81)
        BED_SPRITESHEET_COVER_RECT_COORDS = (0, 106, 64, 22)
        BED_COLOR_FALLBACK = (100,70,30)
        GRID_WIDTH = 32
        GRID_HEIGHT = 24
        TILE_SIZE = 32
        GAME_HOURS_IN_DAY = 28
        SKY_KEYFRAMES = []
        TEXT_COLOR_DARK = (0,0,0)
        TEXT_COLOR_LIGHT = (255,255,255)
        RED = (255,0,0)
        NEED_BAR_BORDER_COLOR = (150,150,150)
        NEED_COLOR_VERY_BAD = (255,0,0)
        NEED_COLOR_BAD = (255,120,0)
        NEED_COLOR_MEDIUM = (255,255,0)
        NEED_COLOR_OKAY = (120,255,0)
        NEED_COLOR_GOOD = (0,200,0)
        def __getattr__(self, name): return None # Default per altri attributi non definiti
    config = ConfigPlaceholder()
    if config.DEBUG_AI_ACTIVE: print("WARNING (game_utils.py): Using FallbackConfig due to import error.")


# Leggi il flag di debug una volta, dopo aver importato (o usato il fallback) di config
DEBUG_VERBOSE = getattr(config, 'DEBUG_AI_ACTIVE', False)

try:
    import cairosvg
    from io import BytesIO 
    CAIROSVG_AVAILABLE = True
except ImportError:
    if DEBUG_VERBOSE: print("WARNING (game_utils.py): Library 'cairosvg' not found. SVG file loading will fail.")
    CAIROSVG_AVAILABLE = False

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
        # if DEBUG_VERBOSE: print(f"INFO: Bed parts loaded from '{bed_spritesheet_filename}'.") # Meno critico
    else:
        if DEBUG_VERBOSE: print(f"WARNING: Bed spritesheet '{bed_spritesheet_filename}' not loaded. Using fallback color.")
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
        
        bar_max_width = 100  
        bar_height = 15      
        bar_vertical_spacing = 5 
        icon_w, icon_h = need_icon_dimensions
        col1_x_abs_screen = bottom_panel_gui_obj.rect.left + needs_bars_start_x_in_panel
        bar_start_y_abs_screen = bottom_panel_gui_obj.rect.top + needs_bars_start_y_in_panel
        col_h_space_between = icon_w + 5 + bar_max_width + 15

        needs_display_data_list = [
            ("Bladder", "bladder", selected_character_to_display.bladder), 
            ("Hunger", "hunger", selected_character_to_display.hunger), 
            ("Energy", "energy", selected_character_to_display.energy),
            ("Fun", "fun", selected_character_to_display.fun), 
            ("Social", "social", selected_character_to_display.social), 
            ("Hygiene", "hygiene", selected_character_to_display.hygiene),
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
                
                icon_display_rect=pygame.Rect(current_col_x_to_draw_at, 
                                              current_need_y_to_draw_at + (bar_height - icon_h) // 2, 
                                              icon_w, icon_h)
                if icon_surf: 
                    screen_surface.blit(icon_surf, icon_display_rect.topleft)
                
                bar_draw_start_x = icon_display_rect.right + 5
                
                # La barra è sempre piena e il colore è determinato da bar_actual_color (come da tua richiesta)
                bar_fill_rect = pygame.Rect(bar_draw_start_x, current_need_y_to_draw_at, bar_max_width, bar_height)
                pygame.draw.rect(screen_surface, bar_actual_color, bar_fill_rect)

                border_rect = pygame.Rect(bar_draw_start_x, current_need_y_to_draw_at, bar_max_width, bar_height)
                pygame.draw.rect(screen_surface, config.NEED_BAR_BORDER_COLOR, border_rect, 1)
                
                current_need_y_to_draw_at += bar_height + bar_vertical_spacing

def get_need_bar_color(goodness_factor): 
    if goodness_factor < 0.25: 
        return interpolate_color(config.NEED_COLOR_VERY_BAD, config.NEED_COLOR_BAD, goodness_factor / 0.25)
    elif goodness_factor < 0.5: 
        return interpolate_color(config.NEED_COLOR_BAD, config.NEED_COLOR_MEDIUM, (goodness_factor - 0.25) / 0.25)
    elif goodness_factor < 0.75: 
        return interpolate_color(config.NEED_COLOR_MEDIUM, config.NEED_COLOR_OKAY, (goodness_factor - 0.5) / 0.25)
    else: 
        return interpolate_color(config.NEED_COLOR_OKAY, config.NEED_COLOR_GOOD, (goodness_factor - 0.75) / 0.25)

def interpolate_color(color1: tuple, color2: tuple, factor: float) -> tuple:
    factor = max(0.0, min(1.0, factor))
    r = int(color1[0] * (1.0 - factor) + color2[0] * factor)
    g = int(color1[1] * (1.0 - factor) + color2[1] * factor)
    b = int(color1[2] * (1.0 - factor) + color2[2] * factor)
    return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))

def get_sky_color_and_period_info(precise_game_hour: float) -> tuple:
    hour_for_sky_color = precise_game_hour % getattr(config, 'GAME_HOURS_IN_DAY', 28)
    sky_keyframes_list = getattr(config, 'SKY_KEYFRAMES', [])
    if not sky_keyframes_list or len(sky_keyframes_list) < 2:
        default_sky_color = (135, 206, 235) 
        default_period_name = "Daytime" 
        default_ui_text_color = getattr(config, 'TEXT_COLOR_DARK', (0,0,0))
        # if DEBUG_VERBOSE: print(f"WARNING (get_sky_color): SKY_KEYFRAMES not properly defined in config. Using defaults.") # Esempio
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
                current_sky_color = interpolate_color(c1, c2, interpolation_factor)
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
    grid_w = getattr(config, 'GRID_WIDTH', 1024 // tile_s) 
    grid_h = getattr(config, 'GRID_HEIGHT', 768 // tile_s) 
    if tile_s <= 0: 
        # if DEBUG_VERBOSE: print("ERROR (world_to_grid): TILE_SIZE is invalid (<=0). Returning (0,0).") # Esempio
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