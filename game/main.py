# simai/game/main.py
# MODIFIED: Extended conditional debug prints using config.DEBUG_AI_ACTIVE.
# MODIFIED: Corrected NameError from main_screen to main_screen_surface in NPC debug rendering.
# MODIFIED: Unified NPC debug flag to 'show_npc_on_screen_debug_info'
# MODIFIED: Encapsulated global game state variables into a GameState class

# main.py

import pygame
import sys
import os
import asyncio # Se usi asyncio per qualche parte (non evidente nel tuo snippet main)
import random
from collections import deque # Per i path degli NPC, se li salvi

# Le tue importazioni esistenti
import game.config as config # Importa il tuo modulo config
import game.game_utils as game_utils
from game.src.ai.npc_behavior import run_npc_ai_logic
from game.src.modules.game_state_module import GameState

# from src.entities.character import Character # La tua classe Character
# Dovrai importare la tua classe Character dal percorso corretto
# Assumendo che sia in src.entities.character
try:
    from game.src.entities.character import Character
except ImportError:
    # Fallback se la struttura delle cartelle è diversa o per debug locale
    import game.src.entities.character # Assicurati che character.py sia accessibile

import pygame_gui # Usi pygame_gui

# NUOVE IMPORTAZIONI PER SALVATAGGIO/CARICAMENTO JSON
# Rinominiamo le funzioni per evitare conflitti con il tuo 'sl_system' esistente se vuoi tenerlo per ora
from simai_save_load_system import (
    save_game_state as save_game_state_json, 
    load_game_state as load_game_state_json,
    get_save_file_path
)
# Commenta o rimuovi l'import del tuo sistema SQLite se lo sostituisci completamente
# import simai_save_load_system as sl_system # Il tuo sistema attuale (presumibilmente per SQLite)

# --- Main Game Function ---
def main(): # Rimuovi async se non usi asyncio direttamente nel loop principale
    game_state = GameState()

    pygame.init() 
    pygame.font.init()
    main_screen_surface = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption(config.WINDOW_TITLE) # Usa WINDOW_TITLE da config
    
    DEBUG_VERBOSE = getattr(config, 'DEBUG_AI_ACTIVE', False) # Usa il tuo flag di debug

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
    if not ui_render_font:
        print("CRITICAL UI FONT ERROR: No font could be loaded. Exiting."); pygame.quit(); sys.exit()

    # Imposta i font in game_state per l'uso in load_game_state_json
    game_state.main_font = ui_render_font # O un font specifico per Character
    # game_state.debug_font = pygame.font.Font(config.FONT_NAME, 16) # Se hai un debug_font specifico

    gui_theme_file_path = 'theme.json' 
    if not os.path.exists(gui_theme_file_path) and DEBUG_VERBOSE:
        print(f"MAIN INFO: Pygame GUI theme file '{gui_theme_file_path}' not found. Using default theme.")
        
    ui_manager_instance = pygame_gui.UIManager((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), 
                                     gui_theme_file_path if os.path.exists(gui_theme_file_path) else None) 
    game_clock = pygame.time.Clock()
    is_game_running = True

    # --- Gestione Database SQLite (COMMENTATA O DA RIMUOVERE SE SI USA JSON) ---
    # game_state.db_connection = sl_system.connect_db(sl_system.DB_FILENAME) 
    # if game_state.db_connection:
    #     sl_system.create_tables_if_not_exist(game_state.db_connection) 
    # else:
    #     print("CRITICAL DB ERROR: Could not connect to database. Exiting.")
    #     pygame.quit(); sys.exit()
    # --- Fine Gestione Database SQLite ---

    # Caricamento asset (il tuo codice esistente)
    # Assicurati che sprite_sheet_manager sia creato e popolato qui
    # Esempio:
    game_state.sprite_sheet_manager = game_utils.SpriteSheetManager() # O come lo inizializzi tu
    try:
        # Carica i tuoi sprite sheet qui, come facevi prima
        # Esempio: game_state.sprite_sheet_manager.load_sheet("male", "assets/images/characters/male.png", ...)
        # game_state.sprite_sheet_manager.load_sheet("female", "assets/images/characters/female.png", ...)
        # Carica gli sprite per gli oggetti se necessario per il loro stato salvato/caricato
        # Questo è un ESEMPIO, devi adattarlo ai tuoi nomi di file e chiavi
        game_state.sprite_sheet_manager.load_sheet("male_char", "assets/images/characters/male.png", config.SPRITE_FRAME_WIDTH, config.SPRITE_FRAME_HEIGHT)
        game_state.sprite_sheet_manager.load_sheet("female_char", "assets/images/characters/female.png", config.SPRITE_FRAME_WIDTH, config.SPRITE_FRAME_HEIGHT)
        game_state.sprite_sheet_manager.load_sheet("male_sleep", os.path.join(config.CHARACTER_SPRITE_PATH, config.SLEEP_SPRITESHEET_MALE_FILENAME), config.SLEEP_SPRITE_FRAME_WIDTH, config.SLEEP_SPRITE_FRAME_HEIGHT)
        game_state.sprite_sheet_manager.load_sheet("female_sleep", os.path.join(config.CHARACTER_SPRITE_PATH, config.SLEEP_SPRITESHEET_FEMALE_FILENAME), config.SLEEP_SPRITE_FRAME_WIDTH, config.SLEEP_SPRITE_FRAME_HEIGHT)
        game_state.sprite_sheet_manager.load_sheet("baby_bundle", os.path.join(config.CHARACTER_SPRITE_PATH, "bundles.png"), config.BUNDLE_FRAME_WIDTH, config.BUNDLE_FRAME_HEIGHT)

    except Exception as e_sprites:
        print(f"ERRORE CRITICO nel caricamento degli sprite sheet: {e_sprites}")
        pygame.quit(); sys.exit()


    loaded_ui_icons, ui_speed_icons, game_state.bed_images, need_bar_icon_dimensions = \
        game_utils.load_all_game_assets() # Il tuo caricamento asset esistente
    
    # Setup oggetti del mondo (letto, bagno - il tuo codice esistente)
    # ... (il tuo codice per bed_rect, toilet_rect_instance, ecc.) ...
    if game_state.bed_images and game_state.bed_images.get("base"):
        base_bed_width = game_state.bed_images["base"].get_width()
        base_bed_height = game_state.bed_images["base"].get_height()
    else: 
        base_bed_width = config.DESIRED_BED_WIDTH
        base_bed_height = config.DESIRED_BED_HEIGHT
        if DEBUG_VERBOSE: print("MAIN WARNING: Bed base image not loaded, using fallback dimensions from config.")
        
    game_state.bed_rect = pygame.Rect(config.DESIRED_BED_X, config.DESIRED_BED_Y, base_bed_width, base_bed_height)
    # ... (calcolo posizioni slot letto come nel tuo codice) ...
    if game_state.bed_rect:
        s1_inter_offset = getattr(config, 'BED_SLOT_1_INTERACTION_OFFSET', (config.TILE_SIZE * 0.5, config.TILE_SIZE * 2.2))
        s2_inter_offset = getattr(config, 'BED_SLOT_2_INTERACTION_OFFSET', (config.TILE_SIZE * 1.5, config.TILE_SIZE * 2.2))
        s1_sleep_offset = getattr(config, 'BED_SLOT_1_SLEEP_POS_OFFSET', (config.TILE_SIZE * 0.5, config.TILE_SIZE * 0.8))
        s2_sleep_offset = getattr(config, 'BED_SLOT_2_SLEEP_POS_OFFSET', (config.TILE_SIZE * 1.5, config.TILE_SIZE * 0.8))

        game_state.bed_slot_1_interaction_pos_world = (
            game_state.bed_rect.left + s1_inter_offset[0], game_state.bed_rect.top + s1_inter_offset[1]
        )
        game_state.bed_slot_2_interaction_pos_world = (
            game_state.bed_rect.left + s2_inter_offset[0], game_state.bed_rect.top + s2_inter_offset[1]
        )
        game_state.bed_slot_1_sleep_pos_world = (
            game_state.bed_rect.left + s1_sleep_offset[0], game_state.bed_rect.top + s1_sleep_offset[1]
        )
        game_state.bed_slot_2_sleep_pos_world = (
            game_state.bed_rect.left + s2_sleep_offset[0], game_state.bed_rect.top + s2_sleep_offset[1]
        )

    if hasattr(config, 'TOILET_RECT_PARAMS'):
        params = config.TOILET_RECT_PARAMS
        game_state.toilet_rect_instance = pygame.Rect(params["x"], params["y"], params["w"], params["h"])
    
    # Aggiungi gli oggetti principali alla lista world_objects_list di game_state se vuoi salvarne lo stato
    # Esempio:
    # if game_state.bed_rect: game_state.world_objects_list.append(BedObject(game_state.bed_rect, ...)) # Se hai classi per oggetti
    # Per ora, il sistema JSON si concentrerà su GameState e NPC.

    world_obstacle_rects = []
    if game_state.bed_rect: world_obstacle_rects.append(game_state.bed_rect)
    if game_state.toilet_rect_instance: world_obstacle_rects.append(game_state.toilet_rect_instance)
    main_pathfinding_grid = game_utils.setup_pathfinding_grid(world_obstacle_rects)
    
    show_debug_grid = False 
    show_npc_on_screen_debug_info = False

    # --- Funzione di Setup per Nuova Partita (adattata) ---
    def setup_new_json_game(current_game_state):
        if DEBUG_VERBOSE: print("MAIN: Impostazione nuova partita (JSON)...")
        # Resetta gli attributi di GameState ai valori iniziali
        current_game_state.current_time_speed_index = 0 # O il tuo default da config
        current_game_state.previous_time_speed_index_before_sleep_ffwd = 0
        current_game_state.is_sleep_fast_forward_active = False
        current_game_state.current_game_total_sim_hours_elapsed = 0.0
        current_game_state.current_game_hour_float = config.INITIAL_START_HOUR
        current_game_state.current_game_day = 1
        current_game_state.current_game_month = 1
        current_game_state.current_game_year = 1
        current_game_state.food_visible = True
        current_game_state.food_cooldown_timer = 0.0
        current_game_state.bed_slot_1_occupied_by = None
        current_game_state.bed_slot_2_occupied_by = None
        # ... (altri reset se necessario) ...

        # Inizializza NPC (la tua funzione esistente, ma popola game_state.all_npc_characters_list)
        current_game_state.all_npc_characters_list = _initialize_npcs_local(current_game_state) # Passa game_state
        
        # Aggiorna la griglia di pathfinding
        nonlocal main_pathfinding_grid # Riferimento alla griglia esterna
        main_pathfinding_grid = game_utils.setup_pathfinding_grid(world_obstacle_rects, current_game_state.all_npc_characters_list)

    def _initialize_npcs_local(current_game_state_param): # Rinominato parametro per evitare shadowing
        # Questa funzione ora popolerà current_game_state_param.all_npc_characters_list
        # e userà current_game_state_param.sprite_sheet_manager, ecc.
        npcs_temp_list = []
        char_fb_radius = min(15, config.TILE_SIZE // 2 - 2)
        
        # Esempio di creazione NPC, dovrai adattarlo per usare SpriteSheetManager
        # e passare game_state all'init di Character
        alpha_npc = Character(
            name="Alpha", gender="male", 
            x=config.SCREEN_WIDTH // 3, y=config.SCREEN_HEIGHT // 2, 
            # color=config.NPC_ALPHA_COLOR_MALE, radius=char_fb_radius, # Rimosso radius, colore se gestito da sprite
            speed=config.CHARACTER_SPEED, # Usa CHARACTER_SPEED
            sprite_sheet_manager=current_game_state_param.sprite_sheet_manager,
            font=current_game_state_param.main_font,
            game_state=current_game_state_param,
            sprite_key_override="male_char" # Chiave per lo sprite sheet
        )
        # alpha_npc.sleep_spritesheet_filename = getattr(config, "SLEEP_SPRITESHEET_MALE_FILENAME", None) # Gestito da Character
        npcs_temp_list.append(alpha_npc)

        beta_npc = Character(
            name="Beta", gender="female", 
            x=config.SCREEN_WIDTH - 150, y=150,
            # color=config.NPC_BETA_COLOR_FEMALE, radius=char_fb_radius - 1,
            speed=config.CHARACTER_SPEED - 10, # Usa CHARACTER_SPEED
            sprite_sheet_manager=current_game_state_param.sprite_sheet_manager,
            font=current_game_state_param.main_font,
            game_state=current_game_state_param,
            sprite_key_override="female_char" # Chiave per lo sprite sheet
        )
        # beta_npc.sleep_spritesheet_filename = getattr(config, "SLEEP_SPRITESHEET_FEMALE_FILENAME", None) # Gestito da Character
        npcs_temp_list.append(beta_npc)
        
        return npcs_temp_list

    # --- Logica di Caricamento JSON all'Avvio ---
    save_file_json = get_save_file_path(config.DEFAULT_SAVE_FILENAME) # Usa costante da config
    if os.path.exists(save_file_json):
        if DEBUG_VERBOSE: print(f"MAIN: Trovato file JSON '{save_file_json}'. Tentativo di caricamento...")
        
        # Chiamiamo load_game_state_json passando game_state per popolarlo,
        # e gli asset manager necessari.
        if load_game_state_json(game_state, config.DEFAULT_SAVE_FILENAME, game_state.sprite_sheet_manager, game_state.main_font):
            if DEBUG_VERBOSE: print("MAIN: Partita caricata con successo da JSON all'avvio.")
            # game_state.all_npc_characters_list è già stato popolato da load_game_state_json
            # Aggiorna la griglia di pathfinding con gli NPC caricati
            main_pathfinding_grid = game_utils.setup_pathfinding_grid(world_obstacle_rects, game_state.all_npc_characters_list)

            # Aggiorna UI Manager (se necessario, es. per selezionare l'NPC corretto)
            # current_selected_npc_idx_ui potrebbe dover essere ricalcolato o caricato
            # ... (la tua logica per aggiornare l'indice dell'NPC selezionato) ...
            # if gui_elements_dict.get('char_status_label'): 
            #     gui_elements_dict['char_status_label'].set_text(f"Display: {game_state.all_npc_characters_list[current_selected_npc_idx_ui].name} (Space)")
        else:
            if DEBUG_VERBOSE: print("MAIN: Caricamento da JSON fallito. Inizio nuova partita.")
            setup_new_json_game(game_state) # Chiama la nuova funzione di setup
    else:
        if DEBUG_VERBOSE: print(f"MAIN: Nessun file JSON '{save_file_json}' trovato. Inizio nuova partita.")
        setup_new_json_game(game_state) # Chiama la nuova funzione di setup

    # Inizializza all_npc_characters qui, dopo il setup o il caricamento
    all_npc_characters = game_state.all_npc_characters_list # Ora è popolata
    current_selected_npc_idx_ui = 0 # Resetta o carica l'indice salvato

    # Setup GUI (il tuo codice esistente, ma assicurati che usi all_npc_characters aggiornato)
    ui_panel_height_val = getattr(config, 'PANEL_UI_HEIGHT', 150) # Usa valore da config con fallback
    time_btn_dims = loaded_ui_icons.get("pause").get_size() if loaded_ui_icons.get("pause") else (30,30)
    gui_elements_dict = game_utils.setup_gui_elements(
        ui_manager_instance, all_npc_characters, current_selected_npc_idx_ui, 
        time_btn_dims, ui_panel_height_val, config.SCREEN_WIDTH, config.SCREEN_HEIGHT
    )
    # Assicurati che l'etichetta del personaggio selezionato sia aggiornata
    if all_npc_characters and gui_elements_dict.get('char_status_label'):
        gui_elements_dict['char_status_label'].set_text(f"Display: {all_npc_characters[current_selected_npc_idx_ui].name} (Space)")


    # --- Loop Principale del Gioco ---
    while is_game_running:
        delta_time_seconds = game_clock.tick(config.FPS) / 1000.0
        
        # Gestione Tempo (il tuo codice esistente)
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
        
        # Gestione accelerazione sonno (il tuo codice esistente)
        all_npcs_sleeping_now = False 
        if all_npc_characters:
            all_npcs_sleeping_now = all(npc.current_action == "resting_on_bed" for npc in all_npc_characters)
        
        user_manually_changed_speed_this_frame = False

        # Loop Eventi
        for event in pygame.event.get():
            if event.type == pygame.QUIT: is_game_running = False
            ui_manager_instance.process_events(event) 

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # Logica per i bottoni velocità
                for i, rect_btn in enumerate(gui_elements_dict.get('time_button_rects',[])):
                    if rect_btn.collidepoint(event.pos): 
                        if game_state.current_time_speed_index != i:
                            game_state.current_time_speed_index = i
                            user_manually_changed_speed_this_frame = True
                            if game_state.is_sleep_fast_forward_active: 
                                game_state.is_sleep_fast_forward_active = False 
                                if DEBUG_VERBOSE: print("MAIN INFO: User changed speed during sleep fast-forward. Deactivating auto FF.")
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: is_game_running = False
                if event.key == pygame.K_g: show_debug_grid = not show_debug_grid
                if event.key == pygame.K_d: show_npc_on_screen_debug_info = not show_npc_on_screen_debug_info
                if event.key == pygame.K_SPACE: 
                    if all_npc_characters: # Solo se ci sono NPC
                        current_selected_npc_idx_ui = (current_selected_npc_idx_ui + 1) % len(all_npc_characters)
                        if gui_elements_dict.get('char_status_label'): 
                            gui_elements_dict['char_status_label'].set_text(f"Display: {all_npc_characters[current_selected_npc_idx_ui].name} (Space)")
                if pygame.K_0 <= event.key <= pygame.K_5: # Selezione velocità da tastiera
                    new_speed_idx = event.key - pygame.K_0
                    if game_state.current_time_speed_index != new_speed_idx:
                        game_state.current_time_speed_index = new_speed_idx
                        user_manually_changed_speed_this_frame = True
                        if game_state.is_sleep_fast_forward_active: 
                            game_state.is_sleep_fast_forward_active = False
                            if DEBUG_VERBOSE: print("MAIN INFO: User changed speed during sleep fast-forward. Deactivating auto FF.")
                if event.key == pygame.K_r and getattr(config, 'DEBUG_MODE_ACTIVE', False):
                    for char_obj in all_npc_characters: char_obj.randomize_needs()
                
                # --- MODIFICA PER SALVATAGGIO/CARICAMENTO JSON ---
                if event.key == pygame.K_F5: 
                    if DEBUG_VERBOSE: print("MAIN: Tasto F5 premuto - Salvataggio partita (JSON)...")
                    # Passa game_state che ora dovrebbe contenere all_npc_characters_list
                    # e gli asset manager (se necessari a save_game_state_json, anche se di solito servono a load)
                    save_game_state_json(game_state, config.DEFAULT_SAVE_FILENAME)

                if event.key == pygame.K_F9: 
                    if DEBUG_VERBOSE: print("MAIN: Tasto F9 premuto - Caricamento partita (JSON)...")
                    if load_game_state_json(game_state, config.DEFAULT_SAVE_FILENAME, 
                                           game_state.sprite_sheet_manager, game_state.main_font):
                        # game_state è stato popolato. Aggiorna le variabili locali e la UI.
                        all_npc_characters = game_state.all_npc_characters_list # Aggiorna riferimento locale
                        # Ricalcola l'indice dell'NPC selezionato se necessario o caricalo
                        # Per ora, lo resettiamo a 0 o cerchiamo di trovare l'UUID se lo salvassimo
                        current_selected_npc_idx_ui = 0 
                        if all_npc_characters and gui_elements_dict.get('char_status_label'):
                            gui_elements_dict['char_status_label'].set_text(f"Display: {all_npc_characters[current_selected_npc_idx_ui].name} (Space)")
                        
                        # Aggiorna la griglia di pathfinding
                        main_pathfinding_grid = game_utils.setup_pathfinding_grid(world_obstacle_rects, all_npc_characters)

                        if DEBUG_VERBOSE: print("MAIN: Partita caricata da JSON e stato aggiornato (F9).")
                    else: 
                        if DEBUG_VERBOSE: print("MAIN ERROR: Caricamento da JSON fallito (F9).")
                # --- FINE MODIFICA PER SALVATAGGIO/CARICAMENTO JSON ---

        # Logica accelerazione sonno (il tuo codice esistente)
        if all_npcs_sleeping_now:
            if not game_state.is_sleep_fast_forward_active and not user_manually_changed_speed_this_frame:
                game_state.previous_time_speed_index_before_sleep_ffwd = game_state.current_time_speed_index
                game_state.current_time_speed_index = getattr(config, 'TIME_SPEED_SLEEP_ACCELERATED_INDEX', 5)
                game_state.is_sleep_fast_forward_active = True
                if DEBUG_VERBOSE: print(f"MAIN INFO: All NPCs sleeping. Activating sleep fast-forward to speed {game_state.current_time_speed_index}.")
        else: 
            if game_state.is_sleep_fast_forward_active:
                game_state.current_time_speed_index = game_state.previous_time_speed_index_before_sleep_ffwd
                game_state.is_sleep_fast_forward_active = False
                if DEBUG_VERBOSE: print(f"MAIN INFO: An NPC woke up. Deactivating sleep FF. Speed restored to {game_state.current_time_speed_index}.")


        # Logica AI e Update NPC (il tuo codice esistente)
        # Assicurati che all_npc_characters sia la lista corretta (da game_state)
        for character_obj in all_npc_characters: 
            # ... (la tua logica di update e AI per ogni NPC) ...
            char_is_resting = character_obj.current_action == "resting_on_bed" # Dovrebbe essere gestito da Character.update
            
            # Chiamata a run_npc_ai_logic (assicurati che i parametri siano corretti)
            # Questa parte dipende molto da come è strutturata la tua IA.
            # Il tuo snippet originale aveva una chiamata a ai_system.run_npc_ai_logic
            if game_state.current_time_speed_index > 0 and main_pathfinding_grid: # Solo se il tempo scorre e la griglia esiste
                food_was_eaten = run_npc_ai_logic(
                    character_obj,
                    all_npc_characters,
                    game_hours_this_tick,
                    main_pathfinding_grid,
                    game_state.food_visible,
                    config.FOOD_POS,
                    game_state,
                    game_state.toilet_rect_instance,
                    getattr(config,'FUN_OBJECT_POS_OR_RECT',None),
                    getattr(config,'SHOWER_POS_OR_RECT',None)
                )
                if food_was_eaten: 
                    game_state.food_visible = False; game_state.food_cooldown_timer = 0.0
            
            # Update del Character (il tuo metodo esistente)
            character_obj.update(delta_time_seconds, config.SCREEN_WIDTH, config.SCREEN_HEIGHT, game_hours_this_tick,
                                 game_state.current_time_speed_index, char_is_resting, config.TILE_SIZE, period_name)


        ui_manager_instance.update(delta_time_seconds)

        # Rendering (il tuo codice esistente)
        main_screen_surface.fill(sky_color)
        if show_debug_grid: 
            # ... (tuo codice per disegnare la griglia) ...
            for x_line in range(0,config.SCREEN_WIDTH,config.TILE_SIZE):pygame.draw.line(main_screen_surface,config.DEBUG_GRID_COLOR,(x_line,0),(x_line,config.SCREEN_HEIGHT))
            for y_line in range(0,config.SCREEN_HEIGHT,config.TILE_SIZE):pygame.draw.line(main_screen_surface,config.DEBUG_GRID_COLOR,(0,y_line),(config.SCREEN_WIDTH,y_line))
            if main_pathfinding_grid: # Controlla se la griglia esiste
                for gy_idx in range(len(main_pathfinding_grid)): # Usa len per la dimensione corretta
                    for gx_idx in range(len(main_pathfinding_grid[0])):
                        if main_pathfinding_grid[gy_idx][gx_idx]==0:
                            pygame.draw.rect(main_screen_surface,config.DEBUG_OBSTACLE_COLOR,pygame.Rect(gx_idx*config.TILE_SIZE,gy_idx*config.TILE_SIZE,config.TILE_SIZE,config.TILE_SIZE))
        
        # Disegna oggetti (letto, bagno, cibo)
        if game_state.bed_images and game_state.bed_images.get("base") and game_state.bed_rect: 
            main_screen_surface.blit(game_state.bed_images["base"], game_state.bed_rect.topleft)
        if game_state.toilet_rect_instance and hasattr(config,'TOILET_COLOR'): 
            pygame.draw.rect(main_screen_surface,config.TOILET_COLOR,game_state.toilet_rect_instance)
            pygame.draw.rect(main_screen_surface,tuple(max(0,c-50) for c in config.TOILET_COLOR),game_state.toilet_rect_instance,2)
        if game_state.food_visible: 
            pygame.draw.circle(main_screen_surface,config.FOOD_COLOR,config.FOOD_POS,config.FOOD_RADIUS)
        
        # Disegna NPC e coperta del letto
        npc_on_this_bed_instance = None # Rinominato per chiarezza
        for char_to_render in all_npc_characters:
            char_to_render.draw(main_screen_surface, font=ui_render_font, text_color=ui_text_color) # Passa il font corretto
            # Controlla se l'NPC è a letto e DEVE essere l'NPC specifico nel suo slot per la coperta
            if char_to_render.current_action == "resting_on_bed":
                if (game_state.bed_slot_1_occupied_by == char_to_render.uuid and game_state.bed_slot_1_sleep_pos_world) or \
                   (game_state.bed_slot_2_occupied_by == char_to_render.uuid and game_state.bed_slot_2_sleep_pos_world):
                    npc_on_this_bed_instance = char_to_render # Potrebbe essere sovrascritto se entrambi dormono, gestisci meglio se necessario

            if show_debug_grid and char_to_render.current_path: # Il tuo debug del path
                # ... (tuo codice) ...
                path_pts=[(char_to_render.x,char_to_render.y)];path_nodes=char_to_render.current_path
                if path_nodes and char_to_render.current_path_index < len(path_nodes):
                    for node_i in range(char_to_render.current_path_index,len(path_nodes)):path_pts.append(game_utils.grid_to_world_center(path_nodes[node_i].x,path_nodes[node_i].y))
                if len(path_pts)>=2:pygame.draw.lines(main_screen_surface,char_to_render.fallback_color,False,path_pts,2)

        if npc_on_this_bed_instance and game_state.bed_images and game_state.bed_images.get("cover") and game_state.bed_rect:
            cover_y_offset_val = getattr(config, 'BED_COVER_DRAW_OFFSET_Y', 26) 
            cover_draw_y_val = game_state.bed_rect.top + cover_y_offset_val
            main_screen_surface.blit(game_state.bed_images["cover"], (game_state.bed_rect.left, cover_draw_y_val))
            if ui_render_font: 
                # ... (tuo codice per Zzz...) ...
                zzz_surf = ui_render_font.render("Zzz...", True, ui_text_color)
                # Determina la corretta posizione y per Zzz
                sleep_frame_h = npc_on_this_bed_instance.sleep_frame_height if npc_on_this_bed_instance.sleep_frame_height > 0 else npc_on_this_bed_instance.radius * 2
                zzz_rect = zzz_surf.get_rect(centerx=int(npc_on_this_bed_instance.x), bottom=int(npc_on_this_bed_instance.y - sleep_frame_h / 2 - 5 ))
                main_screen_surface.blit(zzz_surf, zzz_rect)

        # UI Rendering (pygame_gui e manuale)
        time_lbl_gui = gui_elements_dict.get('time_label')
        action_lbl = gui_elements_dict.get('action_label')
        preg_lbl = gui_elements_dict.get('pregnancy_label')
        if time_lbl_gui: 
            time_lbl_gui.set_text(
                f"Y{game_state.current_game_year}-M{game_state.current_game_month}-D{game_state.current_game_day}, "
                f"{current_int_hour:02d}:{int((game_state.current_game_hour_float%1)*60):02d} "
                f"V{game_state.current_time_speed_index}{'(P)'if game_state.current_time_speed_index==0 else''}"
            )
        
        if all_npc_characters: # Assicurati che ci siano NPC prima di accedere all'indice
            sel_npc_ui_obj = all_npc_characters[current_selected_npc_idx_ui]
            if action_lbl: action_lbl.set_text(f"Action: {sel_npc_ui_obj.current_action}"); action_lbl.show()
            if preg_lbl:
                if sel_npc_ui_obj.is_pregnant:
                    term = getattr(config, 'PREGNANCY_TERM_GAME_DAYS', 24)
                    preg_text = f"Pregnant ({int(sel_npc_ui_obj.days_into_pregnancy)}/{term}d)" # Usa days_into_pregnancy
                    preg_lbl.set_text(preg_text); preg_lbl.show()
                else: preg_lbl.hide()
        
        ui_manager_instance.draw_ui(main_screen_surface) 
        
        if all_npc_characters: # Passa l'NPC selezionato solo se la lista non è vuota
            game_utils.draw_all_manual_ui_elements(main_screen_surface, loaded_ui_icons, ui_speed_icons, 
                                    game_state.current_time_speed_index, 
                                    time_lbl_gui, period_name, all_npc_characters[current_selected_npc_idx_ui], 
                                    gui_elements_dict.get('bottom_panel'), 
                                    gui_elements_dict.get('needs_bar_area_x_in_panel'), 
                                    gui_elements_dict.get('needs_bar_area_y_in_panel'), 
                                    ui_text_color, ui_render_font, gui_elements_dict.get('time_button_rects',[]),
                                    need_bar_icon_dimensions)

        if show_npc_on_screen_debug_info: # Il tuo debug info
            # ... (tuo codice) ...
            debug_y_offset_val = 10; line_h = 18
            for char_idx_val, char_debug_obj in enumerate(all_npc_characters):
                char_debug_x_pos = config.SCREEN_WIDTH - 230 
                if char_idx_val > 0 : debug_y_offset_val += 10 
                txt_lines = [f"--- {char_debug_obj.name} ---", f"Action: {char_debug_obj.current_action}"]
                if char_debug_obj.target_destination: txt_lines.append(f"TargetXY: ({int(char_debug_obj.target_destination[0])}, {int(char_debug_obj.target_destination[1])})")
                if char_debug_obj.current_path: txt_lines.append(f"PathRem: {len(char_debug_obj.current_path) - char_debug_obj.current_path_index}")
                # Bisogni: assicurati che i nomi dei bisogni siano corretti
                txt_lines.append(f"  H:{char_debug_obj.needs['hunger'].get_value():.0f} E:{char_debug_obj.needs['energy'].get_value():.0f} S:{char_debug_obj.needs['social'].get_value():.0f}")
                txt_lines.append(f"  B:{char_debug_obj.needs['bladder'].get_value():.0f} F:{char_debug_obj.needs['fun'].get_value():.0f} Hy:{char_debug_obj.needs['hygiene'].get_value():.0f}")
                txt_lines.append(f"  Int:{char_debug_obj.needs['intimacy'].get_value():.0f}")
                for i, txt_line_val in enumerate(txt_lines):
                    try:
                        debug_sfc = ui_render_font.render(txt_line_val, True, config.TEXT_COLOR_LIGHT, (0,0,0,150) if i == 0 else None)
                        main_screen_surface.blit(debug_sfc, (char_debug_x_pos, debug_y_offset_val + (i * line_h))) 
                    except Exception as e_render_debug: 
                        if DEBUG_VERBOSE: print(f"MAIN Error rendering on-screen NPC debug text: {e_render_debug}")
                debug_y_offset_val += (len(txt_lines) * line_h)

        pygame.display.flip()

    # --- Chiusura (commenta la chiusura DB se non usi più SQLite) ---
    # if game_state.db_connection: 
    #     game_state.db_connection.close()
    #     if DEBUG_VERBOSE: print("MAIN INFO: Database connection closed.")
    # --- Fine Chiusura ---
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    # Se non usi asyncio direttamente in main(), puoi chiamare main() normalmente.
    # Se run_npc_ai_logic o altre parti usano async, allora asyncio.run(main()) è corretto.
    # Dal tuo snippet, main() non sembra essere una coroutine, quindi:
    main()
    # Se invece run_npc_ai_logic è asincrono e vuoi eseguirlo con asyncio.gather,
    # allora main() deve essere async e chiamato con asyncio.run(main()).
    # Ho lasciato la struttura con `async def main()` e `asyncio.run(main())`
    # nel caso tu stia usando `asyncio.gather` per le task AI come nella mia precedente proposta.
    # Se `run_npc_ai_logic` non è async, puoi semplificare.
    # Basandomi sulla chiamata a `ai_system.run_npc_ai_logic` senza `await` nel tuo snippet,
    # è probabile che `main` non necessiti di essere `async` e `ai_tasks` non siano usate.
    # Ho adattato la chiamata a `run_npc_ai_logic` nel loop per riflettere questo.
    # Se invece `run_npc_ai_logic` è effettivamente una coroutine, la gestione con `ai_tasks`
    # e `await asyncio.gather(*ai_tasks)` è corretta. Ho mantenuto la struttura `async` per ora.
