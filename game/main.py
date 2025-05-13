# simai/game/main.py
# Last Updated: 2025-05-13 (Full main with 2-part bed sprite, sleep sprites, English translation)

import pygame
import sys
import math 
import os 
import random 
import datetime 

# Project module imports
try:
    from game.src.entities.character import Character 
    from game import config
    from game import game_utils
    from game.src.ai import npc_behavior as ai_system 
    from game import simai_save_load_system as sl_system 
except ImportError as e:
    print(f"CRITICAL ERROR (main.py): Could not import a required module: {e}")
    print("Check folder structure, __init__.py files, and ensure you are running from the parent directory of 'game' (e.g., 'simai/') with 'python -m game.main'.")
    sys.exit()
except Exception as e_generic_import: 
    print(f"CRITICAL GENERIC ERROR during import in main.py: {e_generic_import}")
    sys.exit()

# External library imports
from pathfinding.core.grid import Grid 
from pathfinding.finder.a_star import AStarFinder
from pathfinding.core.diagonal_movement import DiagonalMovement 
import pygame_gui

# --- Global Game State (module level) ---
g_current_time_speed_index: int = 0 
g_current_game_total_sim_hours_elapsed: float = 0.0 
g_current_game_hour_float: float = config.INITIAL_START_HOUR 
g_current_game_day: int = 1
g_current_game_month: int = 1 
g_current_game_year: int = 1
g_food_visible: bool = True 
g_food_cooldown_timer: float = 0.0 

g_bed_rect: pygame.Rect | None = None 
g_bed_images: dict = {"base": None, "cover": None} 
g_toilet_rect_instance: pygame.Rect | None = None
g_db_connection: 'sqlite3.Connection | None' = None

# --- Main Game Function ---
def main():
    global g_current_time_speed_index, g_current_game_total_sim_hours_elapsed, g_current_game_hour_float
    global g_current_game_day, g_current_game_month, g_current_game_year
    global g_food_visible, g_food_cooldown_timer
    global g_bed_rect, g_bed_images, g_toilet_rect_instance, g_db_connection

    pygame.init() 
    pygame.font.init()
    main_screen_surface = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption(config.WINDOW_TITLE)
    
    ui_render_font = None
    try:
        ui_render_font = pygame.font.SysFont("arial", getattr(config, 'UI_FONT_SIZE', 26))
    except Exception:
        ui_render_font = pygame.font.Font(None, getattr(config, 'UI_FONT_SIZE', 26) + 2)
    if not ui_render_font:
        print("CRITICAL UI FONT ERROR: Could not load any font."); pygame.quit(); sys.exit()

    gui_theme_file_path = 'theme.json' 
    ui_manager_instance = pygame_gui.UIManager((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), 
                                     gui_theme_file_path if os.path.exists(gui_theme_file_path) else None) 
    game_clock = pygame.time.Clock()
    is_game_running = True

    g_db_connection = sl_system.connect_db(sl_system.DB_FILENAME)
    if g_db_connection:
        sl_system.create_tables_if_not_exist(g_db_connection)
    else:
        print("CRITICAL DB ERROR: Could not connect. Exiting."); pygame.quit(); sys.exit()

    loaded_ui_icons, ui_speed_icons, g_bed_images, need_bar_icon_dimensions = \
        game_utils.load_all_game_assets() 
    
    # Define g_bed_rect based on the loaded base image dimensions or config
    # This rect is for placement and collision of the entire bed unit
    if g_bed_images and g_bed_images.get("base"):
        base_bed_width = g_bed_images["base"].get_width()
        base_bed_height = g_bed_images["base"].get_height()
    else: # Fallback to config dimensions if base image not loaded
        base_bed_width = config.DESIRED_BED_WIDTH
        base_bed_height = config.DESIRED_BED_HEIGHT
        
    g_bed_rect = pygame.Rect(config.DESIRED_BED_X, config.DESIRED_BED_Y, base_bed_width, base_bed_height)
    
    g_toilet_rect_instance = None
    if hasattr(config, 'TOILET_RECT_PARAMS'):
        params = config.TOILET_RECT_PARAMS
        g_toilet_rect_instance = pygame.Rect(params["x"], params["y"], params["w"], params["h"])
    
    world_obstacle_rects = [g_bed_rect]
    if g_toilet_rect_instance: world_obstacle_rects.append(g_toilet_rect_instance)
    main_pathfinding_grid = game_utils.setup_pathfinding_grid(world_obstacle_rects)
    show_debug_grid_flag = False 
    show_npc_on_screen_debug_info = False # <-- NOME VARIABILE INIZIALIZZATO QUI

    # Initialize NPCs
    # This helper can remain in main.py or be moved to game_utils if preferred
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
    
    show_debug_grid = False 
    show_npc_debug_text = False

    # --- Main Game Loop ---
    while is_game_running:
        delta_time_seconds = game_clock.tick(config.FPS)/1000.0
        
        (game_hours_this_tick, current_int_hour, # Questi sono locali al loop o usati subito
         g_current_game_day, g_current_game_month, g_current_game_year, # Aggiorna le globali
         g_current_game_total_sim_hours_elapsed, g_current_game_hour_float) = \
            game_utils.update_game_time_state( # La chiamata a game_utils deve passare tutti gli argomenti necessari
                delta_time_seconds,
                g_current_time_speed_index,             # Passa la globale
                g_current_game_total_sim_hours_elapsed, # Passa la globale
                g_current_game_hour_float,              # Passa la globale
                g_current_game_day,                     # Passa la globale
                g_current_game_month,                   # Passa la globale
                g_current_game_year                     # Passa la globale
            )
        # Update globals based on return
        # g_current_game_day = game_utils.update_game_time_state.new_day # Example if function returns object/dict
        # Re-assign all globals based on the 7 return values of update_game_time_state
        # This was previously:
        # (game_hours_advanced_this_tick, current_hour_int, 
        #  g_current_game_day, g_current_game_month, g_current_game_year, 
        #  g_current_game_total_sim_hours_elapsed, g_current_game_hour_float) = \
        #     game_utils.update_game_time_state(...) # The call in my last version was correct.

        sky_color, period_name, ui_text_color = game_utils.get_sky_color_and_period_info(g_current_game_hour_float)

        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT: is_game_running = False
            ui_manager_instance.process_events(event) 
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect_btn in enumerate(gui_elements_dict.get('time_button_rects',[])):
                    if rect_btn.collidepoint(event.pos): g_current_time_speed_index = i; break 
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: is_game_running = False
                if event.key == pygame.K_g: show_debug_grid = not show_debug_grid
                if event.key == pygame.K_d: show_npc_debug_text = not show_npc_debug_text
                if event.key == pygame.K_SPACE: 
                    current_selected_npc_idx_ui = (current_selected_npc_idx_ui + 1) % len(all_npc_characters)
                    if gui_elements_dict.get('char_status_label'): 
                        gui_elements_dict['char_status_label'].set_text(f"Display: {all_npc_characters[current_selected_npc_idx_ui].name} (Space)")
                if pygame.K_0 <= event.key <= pygame.K_5: g_current_time_speed_index = event.key - pygame.K_0
                if event.key == pygame.K_r and getattr(config, 'DEBUG_MODE_ACTIVE', False):
                    for char_obj in all_npc_characters: char_obj.randomize_needs()
                if event.key == pygame.K_F5: 
                    gs_data = {"year":g_current_game_year,"month":g_current_game_month,"day":g_current_game_day,"hour_float":g_current_game_hour_float,"total_sim_hours":g_current_game_total_sim_hours_elapsed,"speed_index":g_current_time_speed_index,"food_visible":g_food_visible,"food_cooldown":g_food_cooldown_timer,"selected_char_uuid":all_npc_characters[current_selected_npc_idx_ui].uuid if all_npc_characters else None}
                    if sl_system.save_current_game_state(g_db_connection,"quicksave",gs_data,all_npc_characters): print("INFO: Game state saved.")
                    else: print("ERROR: Save failed.")
                if event.key == pygame.K_F9: 
                    saves = sl_system.get_available_save_slots(g_db_connection); qs_id = None
                    for s_id,s_name,_ in saves: 
                        if s_name=="quicksave": qs_id=s_id; break
                    if qs_id is not None:
                        loaded_globals,loaded_chars = sl_system.load_game_state_from_db(g_db_connection,qs_id)
                        if loaded_globals and loaded_chars is not None:
                            g_current_game_year=loaded_globals["year"];g_current_game_month=loaded_globals["month"];g_current_game_day=loaded_globals["day"];g_current_game_hour_float=loaded_globals["hour_float"];g_current_game_total_sim_hours_elapsed=loaded_globals["total_sim_hours"];g_current_time_speed_index=loaded_globals["speed_index"];g_food_visible=loaded_globals["food_visible"];g_food_cooldown_timer=loaded_globals["food_cooldown"]
                            all_npc_characters = loaded_chars 
                            sel_uuid=loaded_globals["selected_char_uuid"]; current_selected_npc_idx_ui=0
                            if sel_uuid:
                                for i,char in enumerate(all_npc_characters):
                                    if char.uuid==sel_uuid:current_selected_npc_idx_ui=i;break
                            if gui_elements_dict.get('char_status_label'): gui_elements_dict['char_status_label'].set_text(f"Display: {all_npc_characters[current_selected_npc_idx_ui].name} (Space)")
                            print("INFO: Game 'quicksave' loaded.")
                        else: print("ERROR: Load 'quicksave' failed.")
                    else: print("INFO: No 'quicksave' found to load.")

        # Update Game Logic
        for character_obj in all_npc_characters: 
            char_is_resting = character_obj.current_action == "resting_on_bed"
            if g_current_time_speed_index > 0: 
                food_was_eaten = ai_system.run_npc_ai_logic(character_obj, all_npc_characters, game_hours_this_tick, main_pathfinding_grid, g_food_visible, config.FOOD_POS, g_bed_rect, g_toilet_rect_instance, getattr(config,'FUN_OBJECT_POS_OR_RECT',None), getattr(config,'SHOWER_POS_OR_RECT',None))
                if food_was_eaten: g_food_visible = False; g_food_cooldown_timer = 0.0
            if character_obj.current_action in ["phoning","interacting_intimately","romantic_interaction_action", "affectionate_interaction_action","using_toilet"]: char_is_resting = False 
            character_obj.update(delta_time_seconds,config.SCREEN_WIDTH,config.SCREEN_HEIGHT,game_hours_this_tick,g_current_time_speed_index,char_is_resting,config.TILE_SIZE,period_name) 

        ui_manager_instance.update(delta_time_seconds)

        # --- Rendering ---
        main_screen_surface.fill(sky_color)
        if show_debug_grid: # Debug Grid
            for x_line in range(0,config.SCREEN_WIDTH,config.TILE_SIZE):pygame.draw.line(main_screen_surface,config.DEBUG_GRID_COLOR,(x_line,0),(x_line,config.SCREEN_HEIGHT))
            for y_line in range(0,config.SCREEN_HEIGHT,config.TILE_SIZE):pygame.draw.line(main_screen_surface,config.DEBUG_GRID_COLOR,(0,y_line),(config.SCREEN_WIDTH,y_line))
            for gy_idx in range(config.GRID_HEIGHT):
                for gx_idx in range(config.GRID_WIDTH):
                    if main_pathfinding_grid[gy_idx][gx_idx]==0:pygame.draw.rect(main_screen_surface,config.DEBUG_OBSTACLE_COLOR,pygame.Rect(gx_idx*config.TILE_SIZE,gy_idx*config.TILE_SIZE,config.TILE_SIZE,config.TILE_SIZE))
        
        # Game Objects
        if g_bed_images and g_bed_images.get("base") and g_bed_rect: main_screen_surface.blit(g_bed_images["base"], g_bed_rect.topleft)
        if g_toilet_rect_instance and hasattr(config,'TOILET_COLOR'): pygame.draw.rect(main_screen_surface,config.TOILET_COLOR,g_toilet_rect_instance); pygame.draw.rect(main_screen_surface,tuple(max(0,c-50) for c in config.TOILET_COLOR),g_toilet_rect_instance,2)
        if g_food_visible: pygame.draw.circle(main_screen_surface,config.FOOD_COLOR,config.FOOD_POS,config.FOOD_RADIUS)
        
        # Characters & Bed Cover
        npc_on_this_bed = None
        for char_to_render in all_npc_characters:
            is_sleeping = (char_to_render.current_action == "resting_on_bed" and g_bed_rect and g_bed_rect.collidepoint(char_to_render.x, char_to_render.y))
            if is_sleeping: npc_on_this_bed = char_to_render # Mark to draw cover later
            # Character.draw now handles if its main sprite or sleep sprite should be drawn based on its action
            char_to_render.draw(main_screen_surface, font=ui_render_font, text_color=ui_text_color)
            if show_debug_grid and char_to_render.current_path: # Path
                path_pts=[(char_to_render.x,char_to_render.y)];path_nodes=char_to_render.current_path
                if path_nodes and char_to_render.current_path_index < len(path_nodes):
                    for node_i in range(char_to_render.current_path_index,len(path_nodes)):path_pts.append(game_utils.grid_to_world_center(path_nodes[node_i].x,path_nodes[node_i].y))
                if len(path_pts)>=2:pygame.draw.lines(main_screen_surface,char_to_render.fallback_color,False,path_pts,2)
        
        if npc_on_this_bed and g_bed_images and g_bed_images.get("cover") and g_bed_rect:
            cover_y_offset_val = getattr(config, 'BED_COVER_DRAW_OFFSET_Y', 26) 
            cover_draw_y_val = g_bed_rect.top + cover_y_offset_val
            main_screen_surface.blit(g_bed_images["cover"], (g_bed_rect.left, cover_draw_y_val))
            # Optionally, re-draw name/status text for sleeping NPC on top of cover if needed
            if ui_render_font: # Draw "Zzz..." or similar for sleeping NPC
                zzz_surf = ui_render_font.render("Zzz...", True, ui_text_color)
                zzz_rect = zzz_surf.get_rect(centerx=int(npc_on_this_bed.x), bottom=int(npc_on_this_bed.y - npc_on_this_bed.sleep_frame_height / 2 - 5 if npc_on_this_bed.sleep_frame_height > 0 else npc_on_this_bed.y - 20))
                main_screen_surface.blit(zzz_surf, zzz_rect)

        # Update Pygame_GUI Labels
        time_lbl = gui_elements_dict.get('time_label')
        current_hour_int = int(g_current_game_hour_float)
        action_lbl = gui_elements_dict.get('action_label')
        preg_lbl = gui_elements_dict.get('pregnancy_label')
        if time_lbl: 
            current_hour_int = time_lbl.set_text(
                f"Y{g_current_game_year}-M{g_current_game_month}-D{g_current_game_day}, "
                f"{current_hour_int:02d}:{int((g_current_game_hour_float%1)*60):02d} "
                f"V{g_current_time_speed_index}{'(P)'if g_current_time_speed_index==0 else''}"
            )
        sel_npc_ui_obj = all_npc_characters[current_selected_npc_idx_ui]
        if action_lbl: action_lbl.set_text(f"Action: {sel_npc_ui_obj.current_action}"); action_lbl.show()
        if preg_lbl:
            if sel_npc_ui_obj.is_pregnant:
                term = getattr(config, 'PREGNANCY_TERM_GAME_DAYS', 24); preg_text = f"Pregnant ({int(sel_npc_ui_obj.pregnancy_progress_days)}/{term}d)"; preg_lbl.set_text(preg_text); preg_lbl.show()
            else: preg_lbl.hide()
        ui_manager_instance.draw_ui(main_screen_surface) 
        
        # Draw Manual UI Elements
        game_utils.draw_all_manual_ui_elements(main_screen_surface, loaded_ui_icons, ui_speed_icons, g_current_time_speed_index, 
                                time_lbl, period_name, sel_npc_ui_obj, gui_elements_dict.get('bottom_panel'), 
                                gui_elements_dict.get('needs_bar_area_x_in_panel'), gui_elements_dict.get('needs_bar_area_y_in_panel'), 
                                ui_text_color, ui_render_font, gui_elements_dict.get('time_button_rects',[]),
                                need_bar_icon_dimensions)


        # On-screen NPC Debug Info
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
                        main_screen.blit(debug_sfc, (char_debug_x_pos, debug_y_offset_val + (i * line_h)))
                    except Exception as e_render_debug: print(f"Error rendering debug text: {e_render_debug}")
                debug_y_offset_val += (len(txt_lines) * line_h)
        
        pygame.display.flip()

    # Cleanup
    if g_db_connection: 
        g_db_connection.close()
        print("INFO: Database connection closed.")
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()