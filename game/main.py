# simai/game/main.py
# MODIFIED: Extended conditional debug prints using config.DEBUG_AI_ACTIVE.
# MODIFIED: Corrected NameError from main_screen to main_screen_surface in NPC debug rendering.
# MODIFIED: Unified NPC debug flag to 'show_npc_on_screen_debug_info'
# MODIFIED: Encapsulated global game state variables into a GameState class

import pygame
import sys
import math 
import os 
import random 
import datetime 
import pygame_gui

try:
    from game.src.entities.character import Character 
    from game import config # Import config first
    from game import game_utils
    from game.src.ai import npc_behavior as ai_system 
    from game import simai_save_load_system as sl_system 
except ImportError as e:
    # Questa è un'importazione critica. Se fallisce, il gioco non può partire.
    print(f"CRITICAL ERROR (main.py - Initial Import): Could not import a required module: {e}")
    print("Check folder structure, __init__.py files, and ensure you are running from the parent directory of 'game' (e.g., 'simai/') with 'python -m game.main'.")
    sys.exit()
except Exception as e_generic_import: 
    print(f"CRITICAL GENERIC ERROR during import in main.py: {e_generic_import}")
    sys.exit()

# Leggi il flag di debug una volta, dopo aver importato config
DEBUG_VERBOSE = getattr(config, 'DEBUG_AI_ACTIVE', False) # Usa lo stesso flag dell'IA o uno dedicato come DEBUG_MAIN_VERBOSE

from pathfinding.core.grid import Grid 
from pathfinding.finder.a_star import AStarFinder
from pathfinding.core.diagonal_movement import DiagonalMovement 
import pygame_gui

# --- GameState Class ---
class GameState:
    def __init__(self):
        self.current_time_speed_index: int = 0 
        self.previous_time_speed_index_before_sleep_ffwd: int = 0 # Memorizza la velocità precedente
        self.is_sleep_fast_forward_active: bool = False # Flag per l'accelerazione
        self.current_game_total_sim_hours_elapsed: float = 0.0 
        self.current_game_hour_float: float = config.INITIAL_START_HOUR 
        self.current_game_day: int = 1
        self.current_game_month: int = 1 
        self.current_game_year: int = 1
        self.food_visible: bool = True 
        self.food_cooldown_timer: float = 0.0 
        self.bed_rect: pygame.Rect | None = None
        self.bed_images: dict = {"base": None, "cover": None}

        self.bed_slot_1_occupied_by: str | None = None # UUID dell'NPC o None
        self.bed_slot_2_occupied_by: str | None = None # UUID dell'NPC o None

        self.bed_slot_1_interaction_pos_world: tuple | None = None # (x, y)
        self.bed_slot_2_interaction_pos_world: tuple | None = None # (x, y)

        self.bed_slot_1_sleep_pos_world: tuple | None = None  # (x, y)
        self.bed_slot_2_sleep_pos_world: tuple | None = None  # (x, y)
        self.toilet_rect_instance: pygame.Rect | None = None
        self.db_connection: 'sqlite3.Connection | None' = None

# --- Main Game Function ---
def main():
    game_state = GameState()

    pygame.init() 
    pygame.font.init()
    main_screen_surface = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption(config.WINDOW_TITLE)
    
    ui_render_font = None
    try:
        ui_render_font = pygame.font.SysFont("arial", getattr(config, 'UI_FONT_SIZE', 26))
    except Exception as e_font_sys:
        if DEBUG_VERBOSE: print(f"MAIN WARNING: System font 'arial' not found ({e_font_sys}). Trying default.")
        try:
            ui_render_font = pygame.font.Font(None, getattr(config, 'UI_FONT_SIZE', 26) + 2)
        except Exception as e_font_none:
            print(f"CRITICAL UI FONT ERROR: Could not load sysfont or default font ({e_font_none}). Exiting.")
            pygame.quit(); sys.exit()
            
    if not ui_render_font: # Dovrebbe essere coperto dal sys.exit() sopra, ma per sicurezza
        print("CRITICAL UI FONT ERROR: No font could be loaded. Exiting."); pygame.quit(); sys.exit()


    gui_theme_file_path = 'theme.json' 
    if not os.path.exists(gui_theme_file_path) and DEBUG_VERBOSE:
        print(f"MAIN INFO: Pygame GUI theme file '{gui_theme_file_path}' not found. Using default theme.")
        
    ui_manager_instance = pygame_gui.UIManager((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), 
                                     gui_theme_file_path if os.path.exists(gui_theme_file_path) else None) 
    game_clock = pygame.time.Clock()
    is_game_running = True

    game_state.db_connection = sl_system.connect_db(sl_system.DB_FILENAME) # connect_db ora gestisce la sua stampa condizionale
    if game_state.db_connection:
        sl_system.create_tables_if_not_exist(game_state.db_connection) # create_tables ora gestisce la sua stampa condizionale
    else:
        # connect_db dovrebbe aver già stampato l'errore se DEBUG_VERBOSE è True
        # Ma questo è un errore critico per il gioco.
        print("CRITICAL DB ERROR: Could not connect to database. Check simai_save_load_system.py for details. Exiting.")
        pygame.quit(); sys.exit()

    loaded_ui_icons, ui_speed_icons, game_state.bed_images, need_bar_icon_dimensions = \
        game_utils.load_all_game_assets() 
    
    if game_state.bed_images and game_state.bed_images.get("base"):
        base_bed_width = game_state.bed_images["base"].get_width()
        base_bed_height = game_state.bed_images["base"].get_height()
    else: 
        base_bed_width = config.DESIRED_BED_WIDTH
        base_bed_height = config.DESIRED_BED_HEIGHT
        if DEBUG_VERBOSE: print("MAIN WARNING: Bed base image not loaded, using fallback dimensions from config.")
        
    game_state.bed_rect = pygame.Rect(config.DESIRED_BED_X, config.DESIRED_BED_Y, base_bed_width, base_bed_height)
    if DEBUG_VERBOSE and game_state.bed_rect: # Assumendo che DEBUG_VERBOSE sia definito
        bed_grid_x, bed_grid_y = game_utils.world_to_grid(game_state.bed_rect.left, game_state.bed_rect.top)
        print(f"DEBUG MAIN: Bed topleft at grid ({bed_grid_x}, {bed_grid_y})")
        print(f"DEBUG MAIN: Bed world rect: {game_state.bed_rect}")
    if game_state.bed_rect:
        # Usa 'config.' perché siamo in main.py dove config è importato direttamente
        s1_inter_offset = getattr(config, 'BED_SLOT_1_INTERACTION_OFFSET', (config.TILE_SIZE * 0.5, config.TILE_SIZE * 2.2))
        s2_inter_offset = getattr(config, 'BED_SLOT_2_INTERACTION_OFFSET', (config.TILE_SIZE * 1.5, config.TILE_SIZE * 2.2))
        s1_sleep_offset = getattr(config, 'BED_SLOT_1_SLEEP_POS_OFFSET', (config.TILE_SIZE * 0.5, config.TILE_SIZE * 0.8))
        s2_sleep_offset = getattr(config, 'BED_SLOT_2_SLEEP_POS_OFFSET', (config.TILE_SIZE * 1.5, config.TILE_SIZE * 0.8))

        game_state.bed_slot_1_interaction_pos_world = (
            game_state.bed_rect.left + s1_inter_offset[0],
            game_state.bed_rect.top + s1_inter_offset[1]
        )
        game_state.bed_slot_2_interaction_pos_world = (
            game_state.bed_rect.left + s2_inter_offset[0],
            game_state.bed_rect.top + s2_inter_offset[1]
        )
        game_state.bed_slot_1_sleep_pos_world = (
            game_state.bed_rect.left + s1_sleep_offset[0],
            game_state.bed_rect.top + s1_sleep_offset[1]
        )
        game_state.bed_slot_2_sleep_pos_world = (
            game_state.bed_rect.left + s2_sleep_offset[0],
            game_state.bed_rect.top + s2_sleep_offset[1]
        )
        # Inizializza slot (già fatto nella definizione di GameState, ma per chiarezza)
        game_state.bed_slot_1_occupied_by = None
        game_state.bed_slot_2_occupied_by = None

    if hasattr(config, 'TOILET_RECT_PARAMS'):
        params = config.TOILET_RECT_PARAMS
        game_state.toilet_rect_instance = pygame.Rect(params["x"], params["y"], params["w"], params["h"])
    
    world_obstacle_rects = [game_state.bed_rect]
    if game_state.toilet_rect_instance: world_obstacle_rects.append(game_state.toilet_rect_instance)
    main_pathfinding_grid = game_utils.setup_pathfinding_grid(world_obstacle_rects)
    
    show_debug_grid = False 
    show_npc_on_screen_debug_info = False

    def _initialize_npcs_local():
        char_fb_radius = min(15,config.TILE_SIZE//2-2)
        alpha_npc = Character(name="Alpha", gender="male", 
                              x=config.SCREEN_WIDTH//3, y=config.SCREEN_HEIGHT//2, 
                              color=config.NPC_ALPHA_COLOR_MALE, radius=char_fb_radius, 
                              speed=config.NPC_SPEED, spritesheet_filename="male.png",
                              sleep_spritesheet_filename=getattr(config, "SLEEP_SPRITESHEET_MALE_FILENAME", None))
        beta_npc = Character(name="Beta", gender="female", 
                             x=config.SCREEN_WIDTH-150, y=150,
                             color=config.NPC_BETA_COLOR_FEMALE, radius=char_fb_radius-1, 
                             speed=config.NPC_SPEED-10, spritesheet_filename="female.png",
                             sleep_spritesheet_filename=getattr(config, "SLEEP_SPRITESHEET_FEMALE_FILENAME", None))
        return [alpha_npc, beta_npc]
    all_npc_characters = _initialize_npcs_local()
    current_selected_npc_idx_ui = 0 
    
    ui_panel_height = 150 
    time_btn_dims = loaded_ui_icons.get("pause").get_size() if loaded_ui_icons.get("pause") else (30,30)
    gui_elements_dict = game_utils.setup_gui_elements(
        ui_manager_instance, all_npc_characters, current_selected_npc_idx_ui, 
        time_btn_dims, ui_panel_height, config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
    
    while is_game_running:
        delta_time_seconds = game_clock.tick(config.FPS)/1000.0
        
        (game_hours_this_tick, current_int_hour, 
         new_day, new_month, new_year, 
         new_total_sim_hours, new_hour_float) = \
            game_utils.update_game_time_state(
                delta_time_seconds,
                game_state.current_time_speed_index,
                game_state.current_game_total_sim_hours_elapsed,
                game_state.current_game_hour_float,
                game_state.current_game_day,
                game_state.current_game_month,
                game_state.current_game_year
            )
        game_state.current_game_day = new_day
        game_state.current_game_month = new_month
        game_state.current_game_year = new_year
        game_state.current_game_total_sim_hours_elapsed = new_total_sim_hours
        game_state.current_game_hour_float = new_hour_float

        sky_color, period_name, ui_text_color = game_utils.get_sky_color_and_period_info(game_state.current_game_hour_float)

        all_npcs_sleeping_now = False # Rinominato per chiarezza
        if all_npc_characters: # Solo se ci sono NPC
            all_npcs_sleeping_now = all(npc.current_action == "resting_on_bed" for npc in all_npc_characters)

        user_manually_changed_speed_this_frame = False 

        for event in pygame.event.get():
            if event.type == pygame.QUIT: is_game_running = False
            ui_manager_instance.process_events(event) 
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect_btn in enumerate(gui_elements_dict.get('time_button_rects',[])):
                    if rect_btn.collidepoint(event.pos): 
                        if game_state.current_time_speed_index != i:
                            game_state.current_time_speed_index = i
                            user_manually_changed_speed_this_frame = True
                            if game_state.is_sleep_fast_forward_active: # Se l'utente cambia velocità mentre è attivo il FF
                                game_state.is_sleep_fast_forward_active = False 
                                if DEBUG_VERBOSE: print("MAIN INFO: User changed speed during sleep fast-forward. Deactivating auto FF.")
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: is_game_running = False
                if event.key == pygame.K_g: show_debug_grid = not show_debug_grid
                if event.key == pygame.K_d: show_npc_on_screen_debug_info = not show_npc_on_screen_debug_info
                if event.key == pygame.K_SPACE: 
                    current_selected_npc_idx_ui = (current_selected_npc_idx_ui + 1) % len(all_npc_characters)
                    if gui_elements_dict.get('char_status_label'): 
                        gui_elements_dict['char_status_label'].set_text(f"Display: {all_npc_characters[current_selected_npc_idx_ui].name} (Space)")
                if pygame.K_0 <= event.key <= pygame.K_5:
                    new_speed_idx = event.key - pygame.K_0
                    if game_state.current_time_speed_index != new_speed_idx:
                        game_state.current_time_speed_index = new_speed_idx
                        user_manually_changed_speed_this_frame = True
                        if game_state.is_sleep_fast_forward_active: # Se l'utente cambia velocità mentre è attivo il FF
                            game_state.is_sleep_fast_forward_active = False
                            if DEBUG_VERBOSE: print("MAIN INFO: User changed speed during sleep fast-forward. Deactivating auto FF.")
                if event.key == pygame.K_r and getattr(config, 'DEBUG_MODE_ACTIVE', False):
                    for char_obj in all_npc_characters: char_obj.randomize_needs() # randomize_needs ha la sua stampa condizionale
                if event.key == pygame.K_F5: 
                    gs_data_to_save = {
                        "year": game_state.current_game_year, "month": game_state.current_game_month,
                        "day": game_state.current_game_day, "hour_float": game_state.current_game_hour_float,
                        "total_sim_hours": game_state.current_game_total_sim_hours_elapsed,
                        "speed_index": game_state.current_time_speed_index,
                        "food_visible": game_state.food_visible, "food_cooldown": game_state.food_cooldown_timer,
                        "selected_char_uuid": all_npc_characters[current_selected_npc_idx_ui].uuid if all_npc_characters else None
                    }
                    if sl_system.save_current_game_state(game_state.db_connection, "quicksave", gs_data_to_save, all_npc_characters): 
                        if DEBUG_VERBOSE : print("MAIN INFO: Game state saved (F5).")
                    else: 
                        if DEBUG_VERBOSE : print("MAIN ERROR: Save failed (F5).")
                if event.key == pygame.K_F9: 
                    saves = sl_system.get_available_save_slots(game_state.db_connection); qs_id = None
                    for s_id,s_name,_ in saves: 
                        if s_name=="quicksave": qs_id=s_id; break
                    if qs_id is not None:
                        loaded_globals_dict, loaded_chars_list = sl_system.load_game_state_from_db(game_state.db_connection, qs_id)
                        if loaded_globals_dict and loaded_chars_list is not None:
                            game_state.current_game_year = loaded_globals_dict["year"]
                            game_state.current_game_month = loaded_globals_dict["month"]
                            game_state.current_game_day = loaded_globals_dict["day"]
                            game_state.current_game_hour_float = loaded_globals_dict["hour_float"]
                            game_state.current_game_total_sim_hours_elapsed = loaded_globals_dict["total_sim_hours"]
                            game_state.current_time_speed_index = loaded_globals_dict["speed_index"]
                            game_state.food_visible = loaded_globals_dict["food_visible"]
                            game_state.food_cooldown_timer = loaded_globals_dict["food_cooldown"]
                            all_npc_characters = loaded_chars_list 
                            
                            sel_uuid = loaded_globals_dict["selected_char_uuid"]; current_selected_npc_idx_ui=0
                            if sel_uuid:
                                for i,char in enumerate(all_npc_characters):
                                    if char.uuid==sel_uuid: current_selected_npc_idx_ui=i; break
                            if gui_elements_dict.get('char_status_label'): 
                                gui_elements_dict['char_status_label'].set_text(f"Display: {all_npc_characters[current_selected_npc_idx_ui].name} (Space)")
                            if DEBUG_VERBOSE : print("MAIN INFO: Game 'quicksave' loaded (F9).")
                        else: 
                            if DEBUG_VERBOSE : print("MAIN ERROR: Load 'quicksave' failed (F9).")
                    else: 
                        if DEBUG_VERBOSE : print("MAIN INFO: No 'quicksave' found to load (F9).")
        if all_npcs_sleeping_now:
            if not game_state.is_sleep_fast_forward_active and not user_manually_changed_speed_this_frame:
                # Attiva l'accelerazione solo se non è già attiva e l'utente non ha appena cambiato velocità
                game_state.previous_time_speed_index_before_sleep_ffwd = game_state.current_time_speed_index
                game_state.current_time_speed_index = 5 # O config.TIME_SPEED_SLEEP_ACCELERATED_INDEX se definito
                game_state.is_sleep_fast_forward_active = True
                if DEBUG_VERBOSE: print("MAIN INFO: All NPCs sleeping. Activating sleep fast-forward to speed 5.")
        else: # Almeno un NPC è sveglio (o non ci sono NPC)
            if game_state.is_sleep_fast_forward_active:
                # Disattiva l'accelerazione e ripristina la velocità precedente
                # (user_manually_changed_speed_this_frame avrà già disattivato is_sleep_fast_forward_active,
                # quindi questa parte si attiva solo se l'accelerazione era attiva e un NPC si è svegliato)
                game_state.current_time_speed_index = game_state.previous_time_speed_index_before_sleep_ffwd
                game_state.is_sleep_fast_forward_active = False
                if DEBUG_VERBOSE: print(f"MAIN INFO: An NPC woke up or not all are sleeping. Deactivating sleep fast-forward. Speed restored to {game_state.current_time_speed_index}.")

        for character_obj in all_npc_characters: 
            char_is_resting = character_obj.current_action == "resting_on_bed"
            if game_state.current_time_speed_index > 0: 
                food_was_eaten = ai_system.run_npc_ai_logic(
                    character_obj,                       # 1°
                    all_npc_characters,                  # 2°
                    game_hours_this_tick,                # 3°
                    main_pathfinding_grid,               # 4°
                    game_state.food_visible,             # 5°
                    config.FOOD_POS,                     # 6°
                    game_state,                          # 7° <--- Passi l'OGGETTO game_state intero
                    game_state.toilet_rect_instance,     # 8°
                    getattr(config,'FUN_OBJECT_POS_OR_RECT',None), # 9°
                    getattr(config,'SHOWER_POS_OR_RECT',None)      # 10°
                )
                if food_was_eaten: 
                    game_state.food_visible = False; game_state.food_cooldown_timer = 0.0
            if character_obj.current_action in ["phoning","interacting_intimately","romantic_interaction_action", "affectionate_interaction_action","using_toilet"]: 
                char_is_resting = False 
            character_obj.update(delta_time_seconds,config.SCREEN_WIDTH,config.SCREEN_HEIGHT,game_hours_this_tick,
                                 game_state.current_time_speed_index,char_is_resting,config.TILE_SIZE,period_name) 

        ui_manager_instance.update(delta_time_seconds)

        main_screen_surface.fill(sky_color)
        if show_debug_grid: 
            for x_line in range(0,config.SCREEN_WIDTH,config.TILE_SIZE):pygame.draw.line(main_screen_surface,config.DEBUG_GRID_COLOR,(x_line,0),(x_line,config.SCREEN_HEIGHT))
            for y_line in range(0,config.SCREEN_HEIGHT,config.TILE_SIZE):pygame.draw.line(main_screen_surface,config.DEBUG_GRID_COLOR,(0,y_line),(config.SCREEN_WIDTH,y_line))
            for gy_idx in range(config.GRID_HEIGHT):
                for gx_idx in range(config.GRID_WIDTH):
                    if main_pathfinding_grid[gy_idx][gx_idx]==0:pygame.draw.rect(main_screen_surface,config.DEBUG_OBSTACLE_COLOR,pygame.Rect(gx_idx*config.TILE_SIZE,gy_idx*config.TILE_SIZE,config.TILE_SIZE,config.TILE_SIZE))
        
        if game_state.bed_images and game_state.bed_images.get("base") and game_state.bed_rect: 
            main_screen_surface.blit(game_state.bed_images["base"], game_state.bed_rect.topleft)
        if game_state.toilet_rect_instance and hasattr(config,'TOILET_COLOR'): 
            pygame.draw.rect(main_screen_surface,config.TOILET_COLOR,game_state.toilet_rect_instance)
            pygame.draw.rect(main_screen_surface,tuple(max(0,c-50) for c in config.TOILET_COLOR),game_state.toilet_rect_instance,2)
        if game_state.food_visible: 
            pygame.draw.circle(main_screen_surface,config.FOOD_COLOR,config.FOOD_POS,config.FOOD_RADIUS)
        
        npc_on_this_bed = None
        for char_to_render in all_npc_characters:
            is_sleeping = (char_to_render.current_action == "resting_on_bed" and game_state.bed_rect and game_state.bed_rect.collidepoint(char_to_render.x, char_to_render.y))
            if is_sleeping: npc_on_this_bed = char_to_render
            char_to_render.draw(main_screen_surface, font=ui_render_font, text_color=ui_text_color)
            if show_debug_grid and char_to_render.current_path: 
                path_pts=[(char_to_render.x,char_to_render.y)];path_nodes=char_to_render.current_path
                if path_nodes and char_to_render.current_path_index < len(path_nodes):
                    for node_i in range(char_to_render.current_path_index,len(path_nodes)):path_pts.append(game_utils.grid_to_world_center(path_nodes[node_i].x,path_nodes[node_i].y))
                if len(path_pts)>=2:pygame.draw.lines(main_screen_surface,char_to_render.fallback_color,False,path_pts,2)
        
        if npc_on_this_bed and game_state.bed_images and game_state.bed_images.get("cover") and game_state.bed_rect:
            cover_y_offset_val = getattr(config, 'BED_COVER_DRAW_OFFSET_Y', 26) 
            cover_draw_y_val = game_state.bed_rect.top + cover_y_offset_val
            main_screen_surface.blit(game_state.bed_images["cover"], (game_state.bed_rect.left, cover_draw_y_val))
            if ui_render_font: 
                zzz_surf = ui_render_font.render("Zzz...", True, ui_text_color)
                zzz_rect = zzz_surf.get_rect(centerx=int(npc_on_this_bed.x), bottom=int(npc_on_this_bed.y - npc_on_this_bed.sleep_frame_height / 2 - 5 if npc_on_this_bed.sleep_frame_height > 0 else npc_on_this_bed.y - 20))
                main_screen_surface.blit(zzz_surf, zzz_rect)

        time_lbl_gui = gui_elements_dict.get('time_label')
        action_lbl = gui_elements_dict.get('action_label')
        preg_lbl = gui_elements_dict.get('pregnancy_label')
        if time_lbl_gui: 
            time_lbl_gui.set_text(
                f"Y{game_state.current_game_year}-M{game_state.current_game_month}-D{game_state.current_game_day}, "
                f"{current_int_hour:02d}:{int((game_state.current_game_hour_float%1)*60):02d} "
                f"V{game_state.current_time_speed_index}{'(P)'if game_state.current_time_speed_index==0 else''}"
            )
        sel_npc_ui_obj = all_npc_characters[current_selected_npc_idx_ui]
        if action_lbl: action_lbl.set_text(f"Action: {sel_npc_ui_obj.current_action}"); action_lbl.show()
        if preg_lbl:
            if sel_npc_ui_obj.is_pregnant:
                term = getattr(config, 'PREGNANCY_TERM_GAME_DAYS', 24); preg_text = f"Pregnant ({int(sel_npc_ui_obj.pregnancy_progress_days)}/{term}d)"; preg_lbl.set_text(preg_text); preg_lbl.show()
            else: preg_lbl.hide()
        ui_manager_instance.draw_ui(main_screen_surface) 
        
        game_utils.draw_all_manual_ui_elements(main_screen_surface, loaded_ui_icons, ui_speed_icons, 
                                game_state.current_time_speed_index, 
                                time_lbl_gui, period_name, sel_npc_ui_obj, gui_elements_dict.get('bottom_panel'), 
                                gui_elements_dict.get('needs_bar_area_x_in_panel'), gui_elements_dict.get('needs_bar_area_y_in_panel'), 
                                ui_text_color, ui_render_font, gui_elements_dict.get('time_button_rects',[]),
                                need_bar_icon_dimensions)

        if show_npc_on_screen_debug_info:
            debug_y_offset_val = 10; line_h = 18
            for char_idx_val, char_debug_obj in enumerate(all_npc_characters):
                char_debug_x_pos = config.SCREEN_WIDTH - 230 
                if char_idx_val > 0 : debug_y_offset_val += 10 
                txt_lines = [f"--- {char_debug_obj.name} ---", f"Action: {char_debug_obj.current_action}"]
                if char_debug_obj.target_destination: txt_lines.append(f"TargetXY: ({int(char_debug_obj.target_destination[0])}, {int(char_debug_obj.target_destination[1])})")
                if char_debug_obj.current_path: txt_lines.append(f"PathRem: {len(char_debug_obj.current_path) - char_debug_obj.current_path_index}")
                txt_lines.append(f"  H:{char_debug_obj.hunger.get_value():.0f} E:{char_debug_obj.energy.get_value():.0f} S:{char_debug_obj.social.get_value():.0f}")
                txt_lines.append(f"  B:{char_debug_obj.bladder.get_value():.0f} F:{char_debug_obj.fun.get_value():.0f} Hy:{char_debug_obj.hygiene.get_value():.0f}")
                txt_lines.append(f"  Int:{char_debug_obj.intimacy.get_value():.0f}")
                for i, txt_line_val in enumerate(txt_lines):
                    try:
                        debug_sfc = ui_render_font.render(txt_line_val, True, config.TEXT_COLOR_LIGHT, (0,0,0,150) if i == 0 else None)
                        main_screen_surface.blit(debug_sfc, (char_debug_x_pos, debug_y_offset_val + (i * line_h))) 
                    except Exception as e_render_debug: 
                        if DEBUG_VERBOSE: print(f"MAIN Error rendering on-screen NPC debug text: {e_render_debug}")
                debug_y_offset_val += (len(txt_lines) * line_h)
        
        pygame.display.flip()

    if game_state.db_connection: 
        game_state.db_connection.close()
        if DEBUG_VERBOSE: print("MAIN INFO: Database connection closed.")
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()