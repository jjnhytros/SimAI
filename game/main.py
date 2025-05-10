# simai/game/main.py
# Data ultimo aggiornamento: 2025-05-10 (Versione integrale con sprite NPC base)

import pygame
import sys
import math 
import os 
import random 

# Import moduli del progetto
try:
    from game.src.entities.character import Character 
    from game import config
    from game import game_utils
    from game import ai_system 
except ImportError as e:
    print(f"ERRORE CRITICO (main.py): Impossibile importare un modulo necessario: {e}")
    print("Verifica che 'game/__init__.py' esista, che i moduli siano nella cartella 'game',")
    print("e che character.py sia in 'game/src/entities/'. Esegui da 'simai/' con 'python -m game.main'.")
    sys.exit()
except Exception as e: 
    print(f"ERRORE CRITICO generico durante l'import in main.py: {e}")
    sys.exit()

# Import specifici da librerie esterne
from pathfinding.core.grid import Grid 
from pathfinding.finder.a_star import AStarFinder
from pathfinding.core.diagonal_movement import DiagonalMovement 
import pygame_gui


# --- Stato Globale del Gioco (a livello di modulo) ---
current_time_speed_index = 0 
current_game_total_sim_hours_elapsed = 0.0 
current_game_hour_float = config.INITIAL_START_HOUR 
current_game_day = 1
current_game_month = 1 
current_game_year = 1
food_visible = True 
food_cooldown_timer = 0.0 
BED_RECT = None 
TOILET_RECT = None # Definito in main() se presente in config

# --- Funzioni di Setup Helper ---

def load_all_assets_local():
    """Carica tutte le icone PNG per la UI e le immagini degli oggetti statici."""
    loaded_icons = {}
    icon_size_time_button_tuple = (30, 30)
    icon_size_period_tuple = (28, 28)
    icon_size_need_tuple = (22, 22) 
    
    placeholder_surf = pygame.Surface(icon_size_need_tuple, pygame.SRCALPHA)
    pygame.draw.circle(placeholder_surf, (100,100,100), (icon_size_need_tuple[0]//2, icon_size_need_tuple[1]//2), icon_size_need_tuple[0]//2 - 1)
    if hasattr(config, 'RED'):
        pygame.draw.line(placeholder_surf, config.RED, (3,3), (icon_size_need_tuple[0]-3, icon_size_need_tuple[1]-3), 1)
        pygame.draw.line(placeholder_surf, config.RED, (3,icon_size_need_tuple[1]-3), (icon_size_need_tuple[0]-3, 3), 1)

    icon_files_map = {
        "pause":"pause-circle.png", "speed_1":"1-circle.png", "speed_2":"2-circle.png", 
        "speed_3":"3-circle.png", "speed_4":"4-circle.png", "speed_5":"5-circle.png",
        "dawn":"brightness-alt-high.png", "noon":"sun.png", "sunset":"brightness-alt-low.png", "night":"moon.png",
        "bladder":"toilet.png", "hunger":"apple.png", "energy":"battery-charging.png",
        "fun":"joystick.png", "social":"chat-dots.png", "hygiene":"shower.png",
        "intimacy": "heart.png" 
    }
    icon_sizes_map = {name: icon_size_need_tuple for name in ["bladder", "hunger", "energy", "fun", "social", "hygiene", "intimacy"]}
    icon_sizes_map.update({name: icon_size_time_button_tuple for name in ["pause","speed_1","speed_2","speed_3","speed_4","speed_5"]})
    icon_sizes_map.update({name: icon_size_period_tuple for name in ["dawn","noon","sunset","night"]})

    for name, filename in icon_files_map.items():
        size_val = icon_sizes_map.get(name, icon_size_need_tuple)
        loaded_icons[name] = game_utils.load_image(filename, size_val, base_path=config.ICON_PATH)
        if loaded_icons[name] is None:
            loaded_icons[name] = placeholder_surf
            
    loaded_speed_icons_list = [loaded_icons.get(s) for s in ["pause","speed_1","speed_2","speed_3","speed_4","speed_5"]]

    loaded_bed_image_surf = game_utils.load_image("bed.png", 
                                               (config.DESIRED_BED_WIDTH, config.DESIRED_BED_HEIGHT), 
                                               base_path=config.OBJECT_IMAGE_PATH)
    if not loaded_bed_image_surf: 
        loaded_bed_image_surf = pygame.Surface((config.DESIRED_BED_WIDTH,config.DESIRED_BED_HEIGHT))
        loaded_bed_image_surf.fill(getattr(config, 'BED_COLOR', (100,70,30)))
    
    return loaded_icons, loaded_speed_icons_list, loaded_bed_image_surf, icon_size_need_tuple

def setup_pathfinding_grid_local(obstacle_rect_list_param):
    grid_matrix = [[1 for _ in range(config.GRID_WIDTH)] for _ in range(config.GRID_HEIGHT)]
    if obstacle_rect_list_param:
        for rect_obj in obstacle_rect_list_param:
            if rect_obj is None: continue
            start_gx, start_gy = game_utils.world_to_grid(rect_obj.left, rect_obj.top)
            end_gx, end_gy = game_utils.world_to_grid(rect_obj.right - 1, rect_obj.bottom - 1)
            for gy_o in range(start_gy, end_gy + 1):
                for gx_o in range(start_gx, end_gx + 1):
                    if 0 <= gx_o < config.GRID_WIDTH and 0 <= gy_o < config.GRID_HEIGHT: 
                        grid_matrix[gy_o][gx_o] = 0 
    return grid_matrix

def initialize_characters_local():
    char_r_fallback = min(15, config.TILE_SIZE // 2 - 2) # Usato se Character non ha dimensioni da sprite
    
    # Passa il nome del file dello spritesheet a Character
    npc_alpha = Character(name="Alpha", gender="male", 
        x=config.SCREEN_WIDTH // 3, y=config.SCREEN_HEIGHT // 2, 
        color=config.NPC_ALPHA_COLOR_MALE, radius=char_r_fallback, speed=config.NPC_SPEED,
        spritesheet_filename="male.png") # Assumendo che esista in assets/images/characters/
    
    npc_beta = Character(name="Beta", gender="female", 
        x=config.SCREEN_WIDTH - 150, y=150, 
        color=config.NPC_BETA_COLOR_FEMALE, radius=char_r_fallback - 1, speed=config.NPC_SPEED - 10,
        spritesheet_filename="female.png") # Assumendo che esista
        
    return [npc_alpha, npc_beta]

def setup_gui_elements_local(ui_manager_param, characters_list_param, initial_selected_idx_param, 
                             icon_size_time_button_tuple_param, panel_height_param, 
                             screen_width_param, screen_height_param): # <- DEVE ACCETTARE 7 ARGOMENTI
    """Crea tutti gli elementi della GUI e restituisce un dizionario di riferimenti."""
    gui_elems = {} # Dizionario per memorizzare gli elementi creati
    
    # --- Pannello Inferiore ---
    gui_elems['bottom_panel'] = pygame_gui.elements.UIPanel(
        relative_rect=pygame.Rect((0, screen_height_param - panel_height_param), 
                                  (screen_width_param, panel_height_param)), 
        manager=ui_manager_param, 
        object_id="@bottom_panel"
    )
    
    # --- Pulsanti di Controllo Tempo (manuali, posizionati SOPRA il pannello) ---
    btn_w, btn_h = icon_size_time_button_tuple_param[0], icon_size_time_button_tuple_param[1]
    btn_m = 5 # Margine per i pulsanti del tempo
    # Calcola la Y una sola volta per allineare questi elementi
    time_ctrl_y = screen_height_param - panel_height_param - btn_h - btn_m 
    
    time_btn_rects_list = []
    current_x_button = btn_m 
    for i in range(6): # 6 pulsanti velocità (0-5)
        rect = pygame.Rect(current_x_button, time_ctrl_y, btn_w, btn_h)
        time_btn_rects_list.append(rect)
        current_x_button += btn_w + btn_m
    gui_elems['time_button_rects'] = time_btn_rects_list
    
    # --- Etichetta Tempo (pygame_gui, posizionata SOPRA il pannello) ---
    time_label_x_start = current_x_button + 10 
    time_label_width = screen_width_param - time_label_x_start - btn_m 
    gui_elems['time_label'] = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((time_label_x_start, time_ctrl_y), (time_label_width, btn_h)),
        text="Caricamento...", 
        manager=ui_manager_param, 
        object_id="#time_label"
    )
    
    # --- Elementi DENTRO il Pannello Inferiore ---
    panel_margin_local = 10 # Margine interno al pannello
    char_info_width_local = screen_width_param // 3 # Larghezza per info personaggio

    # Etichetta Personaggio Selezionato
    gui_elems['char_status_label'] = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect(
            (panel_margin_local, panel_margin_local), 
            (char_info_width_local - panel_margin_local * 2, 30)
        ),
        text=f"Mostra: {characters_list_param[initial_selected_idx_param].name} (Spc)", 
        manager=ui_manager_param,
        container=gui_elems['bottom_panel'] # Usa il pannello creato sopra
    )
    # Etichetta Azione NPC
    gui_elems['action_label'] = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect(
            (panel_margin_local, gui_elems['char_status_label'].relative_rect.bottom + 5),
            (char_info_width_local - panel_margin_local * 2, 30)
        ),
        text="",
        manager=ui_manager_param,
        container=gui_elems['bottom_panel']
    )
    # Etichetta Gravidanza
    gui_elems['pregnancy_label'] = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect(
            (panel_margin_local, gui_elems['action_label'].relative_rect.bottom + 5),
            (char_info_width_local - panel_margin_local * 2, 30)
        ),
        text="", 
        manager=ui_manager_param, 
        container=gui_elems['bottom_panel'],
        visible=False # Inizia invisibile
    )
    
    # Coordinate per disegnare le barre dei bisogni (relative all'interno del pannello)
    # Queste sono le coordinate X e Y *dell'area delle barre* RELATIVE al pannello
    gui_elems['needs_bar_area_x_in_panel'] = panel_margin_local + char_info_width_local + 10 
    gui_elems['needs_bar_area_y_in_panel'] = panel_margin_local + 5 # Y di partenza per la prima barra
    
    return gui_elems

def update_game_time_state_local(dt_sec):
    global current_time_speed_index, current_game_total_sim_hours_elapsed, current_game_hour_float
    global current_game_day, current_game_month, current_game_year
    gh_advanced = 0.0
    if current_time_speed_index > 0:
        s_per_gh = config.TIME_SPEED_SETTINGS[current_time_speed_index]
        if s_per_gh > 0 : gh_advanced = dt_sec / s_per_gh # Evita divisione per zero se inf (anche se if sopra lo previene)
    if gh_advanced > 0:
        current_game_total_sim_hours_elapsed += gh_advanced
        total_gh_epoch = config.INITIAL_START_HOUR + current_game_total_sim_hours_elapsed
        current_game_hour_float = total_gh_epoch % config.GAME_HOURS_IN_DAY
        total_days_epoch = int(total_gh_epoch / config.GAME_HOURS_IN_DAY)
        current_game_year = 1 + total_days_epoch // (config.DAYS_PER_MONTH * config.MONTHS_PER_YEAR)
        days_into_year = total_days_epoch % (config.DAYS_PER_MONTH * config.MONTHS_PER_YEAR)
        current_game_month = 1 + days_into_year // config.DAYS_PER_MONTH
        current_game_day = 1 + days_into_year % config.DAYS_PER_MONTH
    return gh_advanced, int(current_game_hour_float)

def draw_manual_ui_elements_local(screen_surf, icons_d, speed_icons_l, speed_idx, 
                               time_lbl_gui, period_n_str, sel_char, bottom_panel_gui_el, 
                               needs_x_in_panel, needs_y_in_panel, 
                               ui_txt_c_ref, ui_fnt_ref, time_btn_rs_list):
    for i,r in enumerate(time_btn_rs_list):
        if i < len(speed_icons_l) and speed_icons_l[i]: screen_surf.blit(speed_icons_l[i],r.topleft)
        if i==speed_idx: pygame.draw.rect(screen_surf,(255,255,0),r,2) 
    period_icon_surf=icons_d.get({"Mattino":"dawn","Mezzogiorno":"noon","Sera":"sunset","Notte":"night"}.get(period_n_str))
    if period_icon_surf and time_lbl_gui: 
        icon_p_r=period_icon_surf.get_rect(centery=time_lbl_gui.rect.centery); icon_p_r.right=time_lbl_gui.rect.left-5
        screen_surf.blit(period_icon_surf,icon_p_r)
    
    bar_max_w=100; bar_h=15; bar_sp_y=5
    icon_s_w, icon_s_h = icons_d.get("hunger").get_size() if icons_d.get("hunger") else (22,22)
    col1_x = bottom_panel_gui_el.rect.left + needs_x_in_panel
    bar_start_y = bottom_panel_gui_el.rect.top + needs_y_in_panel
    col_spacing = icon_s_w + 5 + bar_max_w + 15
    
    needs_map_data = [
        ("vescica", icons_d.get("bladder"),sel_char.bladder), ("fame", icons_d.get("hunger"),sel_char.hunger), 
        ("energia", icons_d.get("energy"),sel_char.energy), ("divertimento", icons_d.get("fun"),sel_char.fun), 
        ("social", icons_d.get("social"),sel_char.social), ("igiene", icons_d.get("hygiene"),sel_char.hygiene),
        ("intimità", icons_d.get("intimacy"),sel_char.intimacy)]
    cols_ui_data = [needs_map_data[0:3], needs_map_data[3:6], needs_map_data[6:7]]
    current_col_x_processing = col1_x
    for col_idx, column_data_list in enumerate(cols_ui_data):
        current_need_y_processing = bar_start_y
        if col_idx == 0: current_col_x_processing = col1_x
        elif col_idx == 1: current_col_x_processing = col1_x + col_spacing
        elif col_idx == 2: current_col_x_processing = col1_x + 2 * col_spacing
        for _, icon_srf, need_obj in column_data_list:
            if not need_obj: continue
            val=need_obj.get_value(); max_v=need_obj.max_value; high_is_good=need_obj.high_value_is_good
            icon_dr=pygame.Rect(current_col_x_processing,current_need_y_processing+(bar_h-icon_s_h)//2,icon_s_w,icon_s_h)
            if icon_srf: screen_surf.blit(icon_srf,icon_dr.topleft)
            bar_curr_x=icon_dr.right+5
            perc=0 if max_v<=0 else val/max_v; perc=max(0.,min(1.,perc))
            good_f=perc if high_is_good else 1-perc
            bar_c=game_utils.interpolate_color(config.GRADIENT_COLOR_BAD,config.GRADIENT_COLOR_GOOD,good_f)
            bg_r=pygame.Rect(bar_curr_x,current_need_y_processing,bar_max_w,bar_h);pygame.draw.rect(screen_surf,config.NEED_BAR_BG_COLOR,bg_r)
            fill_w=int(bar_max_w*perc);fill_r=pygame.Rect(bar_curr_x,current_need_y_processing,fill_w,bar_h);pygame.draw.rect(screen_surf,bar_c,fill_r)
            pygame.draw.rect(screen_surf,config.NEED_BAR_BORDER_COLOR,bg_r,1);current_need_y_processing+=bar_h+bar_sp_y

# --- Funzione Principale ---
def main():
    global current_time_speed_index, current_game_total_sim_hours_elapsed, current_game_hour_float
    global current_game_day, current_game_month, current_game_year
    global food_visible, food_cooldown_timer, BED_RECT, TOILET_RECT 

    pygame.init() 
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption(config.WINDOW_TITLE)
    try: pygame.font.init()
    except Exception as e: print(f"ERRORE FATALE pygame.font.init: {e}"); pygame.quit(); sys.exit()
    
    ui_font = None
    try: ui_font = pygame.font.SysFont("arial", getattr(config, 'UI_FONT_SIZE', 26))
    except: ui_font = pygame.font.Font(None, getattr(config, 'UI_FONT_SIZE', 26) + 2)
    if not ui_font: print("ERRORE FONT UI"); pygame.quit(); sys.exit()

    theme_path = 'theme.json'
    ui_manager = pygame_gui.UIManager((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), 
                                     theme_path if os.path.exists(theme_path) else None) 
    clock = pygame.time.Clock()
    running = True

    icons, speed_icons_list, bed_image_surf, icon_size_need_tuple = load_all_assets_local()
    
    BED_RECT = bed_image_surf.get_rect(topleft=(config.DESIRED_BED_X, config.DESIRED_BED_Y))
    
    TOILET_RECT_INSTANCE = None
    if hasattr(config, 'TOILET_RECT_PARAMS'):
        params = config.TOILET_RECT_PARAMS
        TOILET_RECT_INSTANCE = pygame.Rect(params["x"], params["y"], params["w"], params["h"])
    
    obstacles_for_grid = [BED_RECT]
    if TOILET_RECT_INSTANCE: obstacles_for_grid.append(TOILET_RECT_INSTANCE)
    grid_matrix = setup_pathfinding_grid_local(obstacles_for_grid)
    
    characters = initialize_characters_local()
    ui_selected_char_index = 0 
    
    gui_panel_h_val = 150 
    icon_size_time_btn_val = icons.get("pause").get_size() if icons.get("pause") else (30,30)
    
    gui_elements = setup_gui_elements_local(ui_manager, characters, ui_selected_char_index, 
                                           icon_size_time_btn_val, gui_panel_h_val,
                                           config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
    
    prev_time_real = pygame.time.get_ticks()
    draw_grid = False 

    while running:
        time_delta = clock.tick(config.FPS)/1000.0
        
        game_hours_advanced_this_frame, current_game_hour_int_val = update_game_time_state_local(time_delta)
        current_sky_color_val, current_period_name_val, current_ui_text_color_val = game_utils.get_sky_color_and_period_info(current_game_hour_float)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            ui_manager.process_events(event) 
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: 
                    for i, rect_button in enumerate(gui_elements.get('time_button_rects',[])):
                        if rect_button.collidepoint(event.pos): current_time_speed_index = i; break 
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: running = False
                if event.key == pygame.K_g: draw_grid = not draw_grid
                if event.key == pygame.K_SPACE: 
                    ui_selected_char_index=(ui_selected_char_index+1)%len(characters)
                    if gui_elements.get('char_status_label'): gui_elements['char_status_label'].set_text(f"Mostra: {characters[ui_selected_char_index].name} (Spc)")
                if pygame.K_0 <= event.key <= pygame.K_5: current_time_speed_index = event.key - pygame.K_0
                if event.key == pygame.K_r:
                    for char_instance in characters: char_instance.randomize_needs()
        
        for character_obj in characters: 
            is_char_actually_resting = character_obj.current_action == "resting_on_bed"
            if current_time_speed_index > 0: 
                food_eaten = ai_system.run_npc_ai_logic(
                    character_obj, characters, game_hours_advanced_this_frame, grid_matrix,
                    food_visible, config.FOOD_POS, BED_RECT,
                    TOILET_RECT_INSTANCE, 
                    getattr(config, 'FUN_OBJECT_POS_OR_RECT', None),
                    getattr(config, 'SHOWER_POS_OR_RECT', None))
                if food_eaten: food_visible = False; food_cooldown_timer = 0.0
            
            if character_obj.current_action in ["phoning", "interacting_intimately", "fiki_fiki_action", "flirting_action"]: 
                is_char_actually_resting = False 
            
            character_obj.update(time_delta, config.SCREEN_WIDTH, config.SCREEN_HEIGHT, 
                             game_hours_advanced_this_frame, current_time_speed_index, 
                             is_char_actually_resting, config.TILE_SIZE, current_period_name_val) 

        ui_manager.update(time_delta)

        screen.fill(current_sky_color_val)
        if draw_grid:
            for x_g in range(0,config.SCREEN_WIDTH,config.TILE_SIZE): pygame.draw.line(screen,config.DEBUG_GRID_COLOR,(x_g,0),(x_g,config.SCREEN_HEIGHT))
            for y_g in range(0,config.SCREEN_HEIGHT,config.TILE_SIZE): pygame.draw.line(screen,config.DEBUG_GRID_COLOR,(0,y_g),(config.SCREEN_WIDTH,y_g))
            for gy_g in range(config.GRID_HEIGHT): 
                 for gx_g in range(config.GRID_WIDTH): 
                      if grid_matrix[gy_g][gx_g]==0: pygame.draw.rect(screen,config.DEBUG_OBSTACLE_COLOR,pygame.Rect(gx_g*config.TILE_SIZE,gy_g*config.TILE_SIZE,config.TILE_SIZE,config.TILE_SIZE))
        
        screen.blit(bed_image_surf, BED_RECT.topleft)
        if TOILET_RECT_INSTANCE and hasattr(config, 'TOILET_COLOR'):
            pygame.draw.rect(screen, config.TOILET_COLOR, TOILET_RECT_INSTANCE)
            pygame.draw.rect(screen, tuple(max(0,c-50) for c in config.TOILET_COLOR), TOILET_RECT_INSTANCE, 2)
        if food_visible: pygame.draw.circle(screen,config.FOOD_COLOR,config.FOOD_POS,config.FOOD_RADIUS)
        
        for character_to_draw in characters:
            character_to_draw.draw(screen, font=ui_font, text_color=current_ui_text_color_val)
            if draw_grid and character_to_draw.current_path:
                points=[(character_to_draw.x,character_to_draw.y)]
                path_n=character_to_draw.current_path
                if path_n and character_to_draw.current_path_index<len(path_n):
                    for node_idx in range(character_to_draw.current_path_index,len(path_n)): 
                        node=path_n[node_idx]
                        points.append(game_utils.grid_to_world_center(node.x,node.y))
                if len(points)>=2: pygame.draw.lines(screen,character_to_draw.color,False,points,2)

        time_label_gui = gui_elements.get('time_label')
        if time_label_gui: time_label_gui.set_text(f"A{current_game_year}-M{current_game_month}-G{current_game_day}, {current_game_hour_int_val:02d}:{int((current_game_hour_float%1)*60):02d} V{current_time_speed_index}{'(P)'if current_time_speed_index==0 else''}")
        
        selected_char_for_ui_display = characters[ui_selected_char_index]
        action_label_gui = gui_elements.get('action_label')
        if action_label_gui: 
            action_label_gui.set_text(f"Azione: {selected_char_for_ui_display.current_action}")
            action_label_gui.show()
        
        pregnancy_label_gui = gui_elements.get('pregnancy_label')
        if pregnancy_label_gui:
            if selected_char_for_ui_display.is_pregnant:
                preg_term = getattr(config, 'PREGNANCY_TERM_GAME_DAYS', 24)
                preg_text_ui = f"Incinta ({int(selected_char_for_ui_display.pregnancy_progress_days)}/{preg_term}g)"
                pregnancy_label_gui.set_text(preg_text_ui)
                pregnancy_label_gui.show()
            else:
                pregnancy_label_gui.hide()
        
        ui_manager.draw_ui(screen) 
        
        draw_manual_ui_elements_local(screen, icons, speed_icons_list, current_time_speed_index, 
                                time_label_gui, current_period_name_val, 
                                selected_char_for_ui_display, 
                                gui_elements.get('bottom_panel'), 
                                gui_elements.get('needs_bar_area_x_in_panel'), 
                                gui_elements.get('needs_bar_area_y_in_panel'), 
                                current_ui_text_color_val, ui_font,  
                                gui_elements.get('time_button_rects',[]))
        
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()