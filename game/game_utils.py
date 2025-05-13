# simai/game/game_utils.py
# Last Updated: 2025-05-12 (Moved all helper functions here, English translation)

import pygame
import os
import math
import random # Needed for initialize_characters if using random elements later
import pygame_gui # Needed for setup_gui_elements

try:
    from game import config # Assuming config.py is in 'game' package
    # Character class might be needed if initialize_characters creates them directly
    # and not just returns parameters. Let's assume main.py calls Character directly.
    # from game.src.entities.character import Character 
except ImportError as e:
    print(f"CRITICAL ERROR (game_utils.py): Could not import 'game.config': {e}")
    # Minimal FallbackConfig for constants used directly BY game_utils functions
    class ConfigPlaceholder:
        def __getattr__(self, name):
            print(f"Warning (GameUtils FallbackConfig): Access to undefined config attribute '{name}'")
            if name == "TILE_SIZE": return 32
            if name == "GRID_WIDTH": return 32 # Based on 1024/32
            if name == "GRID_HEIGHT": return 24 # Based on 768/32
            if name == "GAME_HOURS_IN_DAY": return 28
            if name == "SKY_KEYFRAMES": return []
            if name == "TEXT_COLOR_DARK": return (0,0,0)
            if name == "TEXT_COLOR_LIGHT": return (255,255,255)
            if name == "RED": return (255,0,0)
            if name.endswith("_PATH"): return "assets/images/icons" # Generic path
            if name.startswith("DESIRED_BED_"): return 100 # Generic size
            if name.startswith("GRADIENT_COLOR_") or name.startswith("NEED_BAR_"): return (128,128,128)
            return None
    config = ConfigPlaceholder()

# SVG Handling
try:
    import cairosvg
    from io import BytesIO 
    CAIROSVG_AVAILABLE = True
except ImportError:
    print("WARNING (game_utils.py): Library 'cairosvg' not found. SVG file loading will fail.")
    CAIROSVG_AVAILABLE = False

# --- Image Loading Function (Handles SVG and PNG) ---
def load_image(filename_with_ext: str, target_size: tuple = None, base_path: str = "."):
    full_path = os.path.join(base_path, filename_with_ext)
    if not os.path.exists(full_path):
        print(f"LOAD_IMAGE WARNING: Image file NOT FOUND at '{full_path}'")
        return None
    try:
        image_surface = None
        if filename_with_ext.lower().endswith(".svg"):
            if CAIROSVG_AVAILABLE:
                png_data = cairosvg.svg2png(url=full_path, output_width=target_size[0] if target_size else None, output_height=target_size[1] if target_size else None)
                png_file_like_object = BytesIO(png_data)
                image_surface = pygame.image.load(png_file_like_object, filename_with_ext)
            else:
                print(f"LOAD_IMAGE ERROR: 'cairosvg' not available for SVG: {filename_with_ext}.")
                return None
        else: 
            image_surface = pygame.image.load(full_path)
        if image_surface.get_alpha(): image_surface = image_surface.convert_alpha()
        else: image_surface = image_surface.convert()
        if target_size and (image_surface.get_width() != target_size[0] or image_surface.get_height() != target_size[1]):
            image_surface = pygame.transform.smoothscale(image_surface, target_size)
        return image_surface
    except Exception as e: 
        print(f"LOAD_IMAGE ERROR loading '{filename_with_ext}' from '{full_path}': {e}")
        return None

# --- Asset Loading Helper ---
def load_all_game_assets():
    """Loads all UI icons and static object images."""
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
        loaded_icons_map[name] = load_image(filename, size, base_path=config.ICON_PATH) # Direct call
        if loaded_icons_map[name] is None: loaded_icons_map[name] = placeholder_sfc
    speed_control_icons = [loaded_icons_map.get(s) for s in ["pause","speed_1","speed_2","speed_3","speed_4","speed_5"]]
    need_bar_icon_size_val = loaded_icons_map.get("hunger").get_size() if loaded_icons_map.get("hunger") else (22,22)
    
    # --- Caricamento Letto a Due Parti ---
    game_bed_parts = {"base": None, "cover": None, "full_spritesheet_for_debug": None} # Aggiunto per debug
    bed_spritesheet_filename = "double-blue.png" # O il tuo file letto di default
    
    bed_spritesheet_path = getattr(config, 'FURNITURE_IMAGE_PATH', 
                                   os.path.join(getattr(config, 'IMAGE_PATH', 'assets/images'), 'furnitures'))

    full_bed_spritesheet_surf = load_image(
        bed_spritesheet_filename, 
        None, # Carica l'intero spritesheet alla sua dimensione originale
        base_path=bed_spritesheet_path
    )
    game_bed_parts["full_spritesheet_for_debug"] = full_bed_spritesheet_surf # Per debug

    if full_bed_spritesheet_surf:
        # Base del letto
        base_coords = getattr(config, 'BED_SPRITESHEET_BASE_RECT_COORDS', (0, 0, 64, 81)) 
        base_surf = pygame.Surface((base_coords[2], base_coords[3]), pygame.SRCALPHA)
        base_surf.blit(full_bed_spritesheet_surf, (0,0), base_coords)
        game_bed_parts["base"] = base_surf

        # Coperta
        cover_coords = getattr(config, 'BED_SPRITESHEET_COVER_RECT_COORDS', (0, 106, 64, 22))
        cover_surf = pygame.Surface((cover_coords[2], cover_coords[3]), pygame.SRCALPHA)
        cover_surf.blit(full_bed_spritesheet_surf, (0,0), cover_coords)
        game_bed_parts["cover"] = cover_surf
        
        # print(f"INFO: Parti del letto caricate e tagliate da '{bed_spritesheet_filename}'.")
    else:
        # print(f"ATTENZIONE: Spritesheet del letto '{bed_spritesheet_filename}' non caricato.")
        # Fallback per la base se il caricamento fallisce
        placeholder_base_w = getattr(config, 'BED_SPRITESHEET_BASE_RECT_COORDS', (0,0,64,81))[2]
        placeholder_base_h = getattr(config, 'BED_SPRITESHEET_BASE_RECT_COORDS', (0,0,64,81))[3]
        placeholder_base = pygame.Surface((placeholder_base_w, placeholder_base_h), pygame.SRCALPHA)
        placeholder_base.fill(getattr(config,'BED_COLOR_FALLBACK',(100,70,30)))
        game_bed_parts["base"] = placeholder_base
    
    return loaded_icons_map, speed_control_icons, game_bed_parts, need_bar_icon_size_val

# --- Pathfinding Grid Setup Helper ---
def setup_pathfinding_grid(list_of_obstacle_rects: list) -> list:
    """Creates and configures the pathfinding grid."""
    path_grid = [[1 for _ in range(config.GRID_WIDTH)] for _ in range(config.GRID_HEIGHT)]
    if list_of_obstacle_rects:
        for rect_obj_instance in list_of_obstacle_rects:
            if rect_obj_instance is None: continue
            start_gx, start_gy = world_to_grid(rect_obj_instance.left, rect_obj_instance.top) # Direct call
            end_gx, end_gy = world_to_grid(rect_obj_instance.right - 1, rect_obj_instance.bottom - 1) # Direct call
            for gy_idx in range(start_gy, end_gy + 1):
                for gx_idx in range(start_gx, end_gx + 1):
                    if 0 <= gx_idx < config.GRID_WIDTH and 0 <= gy_idx < config.GRID_HEIGHT: 
                        path_grid[gy_idx][gx_idx] = 0 
    return path_grid

# --- GUI Elements Setup Helper ---
def setup_gui_elements(ui_manager_param: pygame_gui.UIManager, 
                       character_list_param: list, 
                       initial_selected_idx_param: int, 
                       icon_size_time_button_tuple_param: tuple, 
                       panel_height_param: int, 
                       screen_width_param: int, # Parametro per larghezza schermo
                       screen_height_param: int # Parametro per altezza schermo
                       ) -> dict:
    """Creates all GUI elements and returns a dictionary of their references."""
    gui_elems = {} 

    # Bottom Panel
    gui_elems['bottom_panel'] = pygame_gui.elements.UIPanel(
        relative_rect=pygame.Rect((0, screen_height_param - panel_height_param), # Qui usa panel_height_param
                                  (screen_width_param, panel_height_param)), 

        object_id="@bottom_panel"
    )

    # Time Control Buttons (manual Rects for blitting icons)
    btn_w, btn_h = icon_size_time_button_tuple_param[0], icon_size_time_button_tuple_param[1]
    btn_m = 5 
    time_ctrl_y = screen_height_param - panel_height_param - btn_h - btn_m 

    time_btn_rects_list = []
    current_x_button = btn_m 
    for _ in range(6): # 6 speed buttons
        rect = pygame.Rect(current_x_button, time_ctrl_y, btn_w, btn_h)
        time_btn_rects_list.append(rect)
        current_x_button += btn_w + btn_m
    gui_elems['time_button_rects'] = time_btn_rects_list

    # Time Label (pygame_gui)
    time_label_x_start = current_x_button + 10 
    time_label_width = screen_width_param - time_label_x_start - btn_m 
    gui_elems['time_label'] = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((time_label_x_start, time_ctrl_y), (time_label_width, btn_h)),
        text="Loading...", 
        manager=ui_manager_param, 
        object_id="#time_label"
    )

    # Elements inside the bottom panel
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

# --- Manual UI Drawing Helper ---
def draw_all_manual_ui_elements(screen_surface: pygame.Surface, loaded_icons_map: dict, 
                                speed_button_icons: list, current_selected_speed_idx: int, 
                                time_label_gui_obj: pygame_gui.elements.UILabel, current_day_period_name: str, 
                                selected_character_to_display: 'Character', # Type hint come stringa
                                bottom_panel_gui_obj: pygame_gui.elements.UIPanel, 
                                needs_bars_start_x_in_panel: int, needs_bars_start_y_in_panel: int, 
                                ui_current_text_color: tuple, default_ui_font: pygame.font.Font, 
                                time_control_buttons_rect_list: list, need_icon_dimensions: tuple):
    # Speed Control Buttons
    if time_control_buttons_rect_list and speed_button_icons:
        for idx, button_r in enumerate(time_control_buttons_rect_list):
            if idx < len(speed_button_icons) and speed_button_icons[idx]: screen_surface.blit(speed_button_icons[idx], button_r.topleft)
            if idx == current_selected_speed_idx: 
                pygame.draw.rect(screen_surface, (255,255,0), button_r, 2)
    # Period Icon
    period_icon_surface = loaded_icons_map.get({"Morning":"dawn","Afternoon":"noon","Evening":"sunset","Night":"night"}.get(current_day_period_name))
    if period_icon_surface and time_label_gui_obj: 
        period_icon_r = period_icon_surface.get_rect(centery=time_label_gui_obj.rect.centery); period_icon_r.right = time_label_gui_obj.rect.left - 5
        screen_surface.blit(period_icon_surface, period_icon_r)
    # Need Bars
    if selected_character_to_display and bottom_panel_gui_obj and \
       needs_bars_start_x_in_panel is not None and needs_bars_start_y_in_panel is not None:
        
        bar_max_width = 100  # Larghezza massima (e ora costante) della barra bisogno
        bar_height = 15      # Altezza della barra bisogno
        bar_vertical_spacing = 5 # Spazio verticale tra le barre
        
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
                
                # Ottieni il "goodness factor" per determinare il colore
                # get_goodness_factor() restituisce 0.0 (male) a 1.0 (bene)
                color_goodness_factor = need_instance.get_goodness_factor()
                
                # Interpola il colore della barra
                bar_actual_color = get_need_bar_color(color_goodness_factor)
                
                # Posizione Icona
                icon_display_rect=pygame.Rect(current_col_x_to_draw_at, 
                                              current_need_y_to_draw_at + (bar_height - icon_h) // 2, 
                                              icon_w, icon_h)
                if icon_surf: 
                    screen_surface.blit(icon_surf, icon_display_rect.topleft)
                
                bar_draw_start_x = icon_display_rect.right + 5
                
                # --- MODIFICA QUI: LA BARRA È SEMPRE PIENA ---
                # Disegna lo sfondo (può essere omesso se la barra colorata copre sempre tutto)
                # background_bar_rect = pygame.Rect(bar_draw_start_x, current_need_y_to_draw_at, bar_max_width, bar_height)
                # pygame.draw.rect(screen_surface, config.NEED_BAR_BG_COLOR, background_bar_rect)
                
                # Disegna la barra, ora sempre di lunghezza bar_max_width, ma con il colore calcolato
                bar_fill_rect = pygame.Rect(bar_draw_start_x, current_need_y_to_draw_at, bar_max_width, bar_height)
                pygame.draw.rect(screen_surface, bar_actual_color, bar_fill_rect)

                # Disegna il bordo della barra
                border_rect = pygame.Rect(bar_draw_start_x, current_need_y_to_draw_at, bar_max_width, bar_height)
                pygame.draw.rect(screen_surface, config.NEED_BAR_BORDER_COLOR, border_rect, 1)
                
                current_need_y_to_draw_at += bar_height + bar_vertical_spacing

def get_need_bar_color(goodness_factor): # goodness_factor da 0 (male) a 1 (bene)
    if goodness_factor < 0.25: # Da VERY_BAD ad BAD
        return interpolate_color(config.NEED_COLOR_VERY_BAD, config.NEED_COLOR_BAD, goodness_factor / 0.25)
    elif goodness_factor < 0.5: # Da BAD a MEDIUM
        return interpolate_color(config.NEED_COLOR_BAD, config.NEED_COLOR_MEDIUM, (goodness_factor - 0.25) / 0.25)
    elif goodness_factor < 0.75: # Da MEDIUM ad OKAY
        return interpolate_color(config.NEED_COLOR_MEDIUM, config.NEED_COLOR_OKAY, (goodness_factor - 0.5) / 0.25)
    else: # Da OKAY a GOOD
        return interpolate_color(config.NEED_COLOR_OKAY, config.NEED_COLOR_GOOD, (goodness_factor - 0.75) / 0.25)

# --- Time and Coordinate Utility Functions (già presenti o da qui) ---
def interpolate_color(color1: tuple, color2: tuple, factor: float) -> tuple:
    """Linearly interpolates between two RGB colors."""
    factor = max(0.0, min(1.0, factor))
    r = int(color1[0] * (1.0 - factor) + color2[0] * factor)
    g = int(color1[1] * (1.0 - factor) + color2[1] * factor)
    b = int(color1[2] * (1.0 - factor) + color2[2] * factor)
    return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))

def get_sky_color_and_period_info(precise_game_hour: float) -> tuple:
    """
    Calculates the interpolated sky color, the name of the current period of the day,
    and an appropriate UI text color based on sky brightness.
    Returns: (sky_color_tuple, period_name_string, ui_text_color_tuple)
    """
    # Ensure game_hour wraps around the 24-hour cycle for color calculation
    # GAME_HOURS_IN_DAY is 28 in our config
    hour_for_sky_color = precise_game_hour % getattr(config, 'GAME_HOURS_IN_DAY', 28)
    
    sky_keyframes_list = getattr(config, 'SKY_KEYFRAMES', [])
    if not sky_keyframes_list or len(sky_keyframes_list) < 2:
        # Fallback if SKY_KEYFRAMES is missing, empty, or has too few points
        default_sky_color = (135, 206, 235) 
        default_period_name = "Daytime" # English
        default_ui_text_color = getattr(config, 'TEXT_COLOR_DARK', (0,0,0))
        # print(f"WARNING (get_sky_color): SKY_KEYFRAMES not properly defined in config. Using defaults.")
        return default_sky_color, default_period_name, default_ui_text_color

    # Find the two keyframes to interpolate between
    # Initialize with the first keyframe's color as a starting default
    current_sky_color = sky_keyframes_list[0][1] 

    for i in range(len(sky_keyframes_list)):
        h1, c1 = sky_keyframes_list[i]
        # For the last segment, interpolate towards the first keyframe's color if it wraps around
        # or use the last keyframe's color if hour_for_sky_color is beyond the last defined hour.
        if i == len(sky_keyframes_list) - 1: # Last keyframe
            # If the last keyframe's hour is less than GAME_HOURS_IN_DAY,
            # it implies a wrap-around to the first keyframe for interpolation.
            # However, our SKY_KEYFRAMES should ideally have the last hour match GAME_HOURS_IN_DAY
            # and its color match the first keyframe's color for a seamless loop.
            # For simplicity here, if we are past or at the last keyframe's hour, we use its color.
            if hour_for_sky_color >= h1:
                current_sky_color = c1
            # If the keyframes don't span the full day, this logic might need adjustment
            # or ensure the first keyframe is (0, color) and last is (GAME_HOURS_IN_DAY, same_color)
            break 
        
        h2, c2 = sky_keyframes_list[i+1]
        if h1 <= hour_for_sky_color < h2:
            segment_duration = h2 - h1
            if segment_duration <= 0:
                current_sky_color = c1
            else:
                time_into_segment = hour_for_sky_color - h1
                interpolation_factor = time_into_segment / segment_duration
                current_sky_color = interpolate_color(c1, c2, interpolation_factor)
            break 
    # If no segment was matched (e.g. hour_for_sky_color is exactly the last keyframe's hour
    # or slightly beyond due to modulo and float precision, but loop condition was < h2),
    # current_sky_color might still be from the previous valid segment or the initial default.
    # Ensuring the last keyframe hour is >= GAME_HOURS_IN_DAY or that the first and last colors match
    # for a 0-GAME_HOURS_IN_DAY cycle is important in config.py.

    # Determine Period Name
    current_game_hour_int = int(precise_game_hour) % getattr(config, 'GAME_HOURS_IN_DAY', 28)
    period_name = "Night" # Default
    if 7 <= current_game_hour_int < 12: # Example: Morning 7 AM to 11:59 AM
        period_name = "Morning"
    elif 12 <= current_game_hour_int < 18: # Example: Afternoon 12 PM to 5:59 PM
        period_name = "Afternoon"
    elif 18 <= current_game_hour_int < 22: # Example: Evening 6 PM to 9:59 PM
        period_name = "Evening"
    # else it remains "Night" (e.g., 22:00 - 06:59)
    
    # Determine UI Text Color based on sky brightness
    brightness = (current_sky_color[0]*0.299 + current_sky_color[1]*0.587 + current_sky_color[2]*0.114)
    ui_text_color = getattr(config, 'TEXT_COLOR_DARK', (0,0,0)) if brightness > 140 \
                    else getattr(config, 'TEXT_COLOR_LIGHT', (255,255,255)) # Adjusted brightness threshold
    
    return current_sky_color, period_name, ui_text_color

def world_to_grid(world_x: float, world_y: float) -> tuple:
    """Converts world coordinates to grid coordinates, ensuring they are within grid bounds."""
    tile_s = getattr(config, 'TILE_SIZE', 32)
    grid_w = getattr(config, 'GRID_WIDTH', 1024 // tile_s) 
    grid_h = getattr(config, 'GRID_HEIGHT', 768 // tile_s) 

    if tile_s <= 0:
        print("ERROR (world_to_grid): TILE_SIZE is invalid (<=0). Returning (0,0).")
        return (0, 0) 

    grid_x = int(world_x // tile_s)
    grid_y = int(world_y // tile_s)
    
    grid_x = max(0, min(grid_w - 1, grid_x)) # Clamp to [0, GRID_WIDTH-1]
    grid_y = max(0, min(grid_h - 1, grid_y)) # Clamp to [0, GRID_HEIGHT-1]
    
    return grid_x, grid_y

def grid_to_world_center(grid_x: int, grid_y: int) -> tuple:
    """Returns the world coordinates of the center of a grid cell."""
    tile_s = getattr(config, 'TILE_SIZE', 32)
    world_x = grid_x * tile_s + tile_s / 2.0 # Use float division for center
    world_y = grid_y * tile_s + tile_s / 2.0
    return world_x, world_y

def update_game_time_state(
    time_delta_seconds: float, 
    current_speed_idx: int,
    current_total_sim_hours_elapsed_val: float,
    current_hour_float_val: float, # Non strettamente necessario passarlo, ma per completezza
    current_day_val: int,
    current_month_val: int,
    current_year_val: int
) -> tuple:
    """
    Updates game time variables based on parameters and returns new values.
    Returns: (hours_advanced_this_frame, new_current_hour_int, 
              new_day, new_month, new_year, new_total_sim_hours_elapsed, new_current_hour_float)
    """
    hours_advanced_this_frame = 0.0
    
    # Usa i parametri passati, non le globali
    if current_speed_idx > 0:
        seconds_per_game_hour = config.TIME_SPEED_SETTINGS[current_speed_idx]
        if seconds_per_game_hour > 0 and seconds_per_game_hour != float('inf'):
            hours_advanced_this_frame = time_delta_seconds / seconds_per_game_hour
    
    # Inizializza i valori di ritorno con quelli attuali
    new_total_sim_hours = current_total_sim_hours_elapsed_val
    new_hour_float = current_hour_float_val # Questo verrà ricalcolato
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
            new_total_sim_hours, new_hour_float) # Restituisce tutti i valori aggiornati
