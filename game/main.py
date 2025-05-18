# simai/game/main.py
# MODIFIED: Extended conditional debug prints using config.DEBUG_AI_ACTIVE.
# MODIFIED: Corrected NameError from main_screen to main_screen_surface in NPC debug rendering.
# MODIFIED: Unified NPC debug flag to 'show_npc_on_screen_debug_info'
# MODIFIED: Encapsulated global game state variables into a GameState class

# main.py

import pygame
import sys
import os
# import asyncio # Rimuovi se non lo usi attivamente
import random
from collections import deque
from typing import Optional, Tuple, List, Dict # Aggiungi per type hints

# Importa dal package 'game'
from game import config 
from game.src.utils import game as game_utils


# Importa Character e run_npc_ai_logic
from game.src.entities.character import Character
from game.src.ai.npc_behavior import run_npc_ai_logic 

# Importa le funzioni JSON per salvare/caricare
from game.simai_save_load_system import (
    save_game_state as save_game_state_json, 
    load_game_state as load_game_state_json,
    get_save_file_path
)

# --- IMPORT CORRETTO PER I MANAGER ---
from game.src.managers.asset_manager import SpriteSheetManager
from game.src.managers.time_manager import GameTimeManager
# from game.src.ui_manager import UIManager # Se hai una tua classe UIManager dedicata
import pygame_gui 

# Importa la classe GameState
from game.src.modules.game_state_module import GameState

# --- Main Game Function ---
def main():
    pygame.init()
    pygame.font.init()

    # PRIMA COSA: Carica i blueprint degli oggetti!
    # Questo popolerà game_utils.OBJECT_BLUEPRINTS_DATA (o una variabile simile)
    # Assicurati che il file object_blueprints.json esista in game/assets/data/
    # e che la funzione load_object_blueprints in game_utils sia corretta.
    if hasattr(game_utils, 'load_object_blueprints'):
        game_utils.load_object_blueprints()
    else:
        print("ERRORE CRITICO: Funzione 'load_object_blueprints' non trovata in game_utils.")
        pygame.quit()
        sys.exit()


    game_state = GameState()

    game_state.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption(config.WINDOW_TITLE)

    DEBUG_VERBOSE = game_state.DEBUG_AI_ACTIVE

    try:
        game_state.main_font = pygame.font.SysFont("arial", getattr(config, 'UI_FONT_SIZE', 26))
    except Exception:
        try:
            game_state.main_font = pygame.font.Font(None, getattr(config, 'UI_FONT_SIZE', 26) + 2)
        except Exception as e_font_final:
             print(f"ERRORE CRITICO FONT: {e_font_final}. Uscita.")
             pygame.quit(); sys.exit()

    game_state.sprite_sheet_manager = SpriteSheetManager()
    try:
        game_state.sprite_sheet_manager.load_sheet(
            "male_char", "characters/male.png", config.SPRITE_FRAME_WIDTH, config.SPRITE_FRAME_HEIGHT
        )
        game_state.sprite_sheet_manager.load_sheet(
            "female_char", "characters/female.png", config.SPRITE_FRAME_WIDTH, config.SPRITE_FRAME_HEIGHT
        )
        game_state.sprite_sheet_manager.load_sheet(
            "male_sleep", os.path.join("characters", config.SLEEP_SPRITESHEET_MALE_FILENAME),
            config.SLEEP_SPRITE_FRAME_WIDTH, config.SLEEP_SPRITE_FRAME_HEIGHT
        )
        game_state.sprite_sheet_manager.load_sheet(
            "female_sleep", os.path.join("characters", config.SLEEP_SPRITESHEET_FEMALE_FILENAME),
            config.SLEEP_SPRITE_FRAME_WIDTH, config.SLEEP_SPRITE_FRAME_HEIGHT
        )
        game_state.sprite_sheet_manager.load_sheet(
            "baby_bundle", os.path.join("characters", "bundles.png"),
            config.BUNDLE_FRAME_WIDTH, config.BUNDLE_FRAME_HEIGHT
        )
        # Carica anche lo spritesheet per i mobili se lo usi
        # Ad esempio, se OBJECT_BLUEPRINTS["double_bed_blue"]["sprite_sheet_key"] è "furniture_sprites"
        # e il file è "furnitures.png" (un singolo sheet per più mobili)
        # game_state.sprite_sheet_manager.load_sheet(
        # "furniture_sprites",
        # "furnitures/furnitures.png", # Adatta il nome del file e le dimensioni dei frame
        # config.FURNITURE_FRAME_WIDTH, # Dovresti definire queste costanti
        # config.FURNITURE_FRAME_HEIGHT
        # )

    except Exception as e_sprites:
        print(f"ERRORE CRITICO nel caricamento degli sprite sheet: {e_sprites}")
        pygame.quit(); sys.exit()

    expected_time_manager_path = os.path.join(config.GAME_DIR_PATH, "src", "managers", "time_manager.py")
    if DEBUG_VERBOSE:
        print(f"DEBUG MAIN: Percorso GAME_DIR_PATH in config: {config.GAME_DIR_PATH}")
        print(f"DEBUG MAIN: Controllo esistenza per time_manager.py a: {expected_time_manager_path}")

    if os.path.exists(expected_time_manager_path):
        game_state.game_time_handler = GameTimeManager(
            game_hours_in_day=config.GAME_HOURS_IN_DAY,
            sky_keyframes=config.SKY_KEYFRAMES,
            time_speeds=config.TIME_SPEED_SETTINGS,
            initial_hour=config.INITIAL_START_HOUR,
            default_speed_index = getattr(config, 'TIME_SPEED_NORMAL_INDEX', 1)
        )
    else:
        print(f"ERRORE CRITICO: {expected_time_manager_path} non trovato. Impossibile avviare il gestore del tempo.")
        pygame.quit(); sys.exit()

    gui_theme_path = os.path.join(config.GAME_DIR_PATH, 'theme.json')
    game_state.ui_manager_instance = pygame_gui.UIManager(
        (config.SCREEN_WIDTH, config.SCREEN_HEIGHT),
        gui_theme_path if os.path.exists(gui_theme_path) else None
    )

    loaded_ui_icons, ui_speed_icons, game_state.bed_images, need_bar_icon_dimensions = \
        game_utils.load_all_game_assets() # Questa funzione carica le icone UI e le immagini del letto dallo spritesheet

    # --- Setup oggetti del mondo (letto, bagno) ---
    # Ora, la posizione del letto è da config, ma i suoi dettagli (offset interazione)
    # dovrebbero idealmente venire da OBJECT_BLUEPRINTS_DATA caricato da game_utils.
    # Per ora, manteniamo la logica degli offset da config.py, ma con l'idea di passare ai blueprint.

    # Prendi il blueprint per il letto che useremo (es. il "double_bed_blue")
    main_bed_blueprint_key = "double_bed_blue" # Dovresti avere questo tipo definito nel tuo JSON
    bed_blueprint = game_utils.get_object_blueprint(main_bed_blueprint_key)

    if bed_blueprint and bed_blueprint.get("sprite_rect_in_sheet"):
        # Usa le dimensioni dal blueprint se possibile, altrimenti config
        # Nota: game_state.bed_images["base"] è già stato caricato da load_all_game_assets
        # usando i rect da config.BED_SPRITESHEET_BASE_RECT_COORDS.
        # Ci potrebbe essere una ridondanza qui se non allinei le due cose.
        # Per ora, assumiamo che le dimensioni di base del letto siano quelle dello sprite caricato.
        if game_state.bed_images and game_state.bed_images.get("base"):
            base_bed_width = game_state.bed_images["base"].get_width()
            base_bed_height = game_state.bed_images["base"].get_height()
        else: # Fallback se l'immagine del letto non è stata caricata
            base_bed_width = bed_blueprint["sprite_rect_in_sheet"][2]
            base_bed_height = bed_blueprint["sprite_rect_in_sheet"][3]
            if DEBUG_VERBOSE: print("MAIN WARNING: game_state.bed_images['base'] non trovata. Uso dimensioni da blueprint per bed_rect.")
    else:
        base_bed_width = config.DESIRED_BED_WIDTH
        base_bed_height = config.DESIRED_BED_HEIGHT
        if DEBUG_VERBOSE: print(f"MAIN WARNING: Blueprint per '{main_bed_blueprint_key}' non trovato o 'sprite_rect_in_sheet' mancante. Uso DESIRED_BED_WIDTH/HEIGHT da config.")


    game_state.bed_rect = pygame.Rect(config.DESIRED_BED_X, config.DESIRED_BED_Y, base_bed_width, base_bed_height)

    if game_state.bed_rect and bed_blueprint:
        # Calcola i punti di interazione e sonno usando gli offset DAL BLUEPRINT
        # e la posizione del game_state.bed_rect
        interaction_points_def = bed_blueprint.get("interaction_points", [])
        slot_positions_def = bed_blueprint.get("slots", [])

        if len(interaction_points_def) > 0:
            offset_slot0_inter = interaction_points_def[0].get("offset", (0,0))
            game_state.bed_slot_1_interaction_pos_world = (
                game_state.bed_rect.left + offset_slot0_inter[0],
                game_state.bed_rect.top + offset_slot0_inter[1]
            )
        if len(interaction_points_def) > 1:
            offset_slot1_inter = interaction_points_def[1].get("offset", (0,0))
            game_state.bed_slot_2_interaction_pos_world = (
                game_state.bed_rect.left + offset_slot1_inter[0],
                game_state.bed_rect.top + offset_slot1_inter[1]
            )

        if len(slot_positions_def) > 0:
            offset_slot0_sleep = slot_positions_def[0].get("offset", (0,0))
            game_state.bed_slot_1_sleep_pos_world = (
                game_state.bed_rect.left + offset_slot0_sleep[0],
                game_state.bed_rect.top + offset_slot0_sleep[1]
            )
        if len(slot_positions_def) > 1:
            offset_slot1_sleep = slot_positions_def[1].get("offset", (0,0))
            game_state.bed_slot_2_sleep_pos_world = (
                game_state.bed_rect.left + offset_slot1_sleep[0],
                game_state.bed_rect.top + offset_slot1_sleep[1]
            )

        if DEBUG_VERBOSE:
            print(f"DEBUG MAIN: Letto (config pos): X={config.DESIRED_BED_X}, Y={config.DESIRED_BED_Y}")
            print(f"DEBUG MAIN: Letto Rect (calcolato): {game_state.bed_rect.topleft}")
            if game_state.bed_slot_1_interaction_pos_world:
                 print(f"DEBUG MAIN: Slot 0 Interaction Mondo (da blueprint): {game_state.bed_slot_1_interaction_pos_world} -> Griglia: {game_utils.world_to_grid(game_state.bed_slot_1_interaction_pos_world[0], game_state.bed_slot_1_interaction_pos_world[1])}")
            if game_state.bed_slot_2_interaction_pos_world:
                 print(f"DEBUG MAIN: Slot 1 Interaction Mondo (da blueprint): {game_state.bed_slot_2_interaction_pos_world} -> Griglia: {game_utils.world_to_grid(game_state.bed_slot_2_interaction_pos_world[0], game_state.bed_slot_2_interaction_pos_world[1])}")
    elif DEBUG_VERBOSE:
        print("MAIN WARNING: game_state.bed_rect o bed_blueprint non disponibili per calcolare posizioni slot letto.")


    if hasattr(config, 'TOILET_RECT_PARAMS'): # Manteniamo il bagno da config per ora
        params = config.TOILET_RECT_PARAMS
        game_state.toilet_rect_instance = pygame.Rect(params["x"], params["y"], params["w"], params["h"])
    else:
        game_state.toilet_rect_instance = None
        if DEBUG_VERBOSE: print("MAIN WARNING: TOILET_RECT_PARAMS non definito in config. Bagno non creato.")

    world_obstacle_rects = []
    if game_state.bed_rect:
        # Qui dovresti usare l'obstacle_rect_relative dal blueprint del letto,
        # sommato alla posizione del letto nel mondo.
        # Per ora, usiamo l'intero game_state.bed_rect come ostacolo.
        world_obstacle_rects.append(game_state.bed_rect)

    if game_state.toilet_rect_instance:
        world_obstacle_rects.append(game_state.toilet_rect_instance)

    main_pathfinding_grid = None
    all_npc_characters = []
    current_selected_npc_idx_ui = 0
    gui_elements_dict = {}

    def _initialize_npcs_local(current_game_state_param):
        # ... (come prima) ...
        return [] # Placeholder

    def setup_new_json_game(current_game_state):
        # ... (come prima, assicurati che usi world_obstacle_rects definito sopra) ...
        nonlocal main_pathfinding_grid, all_npc_characters, current_selected_npc_idx_ui
        # ...
        current_game_state.all_npc_characters_list = _initialize_npcs_local(current_game_state)
        all_npc_characters = current_game_state.all_npc_characters_list
        main_pathfinding_grid = game_utils.setup_pathfinding_grid(world_obstacle_rects)
        current_game_state.a_star_grid_instance = main_pathfinding_grid
        current_selected_npc_idx_ui = 0


    save_file_json = get_save_file_path(config.DEFAULT_SAVE_FILENAME)
    if os.path.exists(save_file_json):
        # ... (logica di caricamento, assicurati che aggiorni main_pathfinding_grid e all_npc_characters) ...
        pass # Placeholder
    else:
        if DEBUG_VERBOSE: print(f"MAIN: Nessun file JSON '{save_file_json}' trovato. Inizio nuova partita.")
        setup_new_json_game(game_state)
        # all_npc_characters è già aggiornato da setup_new_json_game

    if DEBUG_VERBOSE and main_pathfinding_grid and all_npc_characters:
        # ... (stampa griglia di debug come prima, usando le coordinate corrette degli slot letto) ...
        pass # Placeholder


    # Setup GUI
    ui_panel_height_val = getattr(config, 'PANEL_UI_HEIGHT', 150)
    time_btn_dims = loaded_ui_icons.get("pause").get_size() if loaded_ui_icons.get("pause") else (30,30)
    if all_npc_characters: # Assicurati che ci sia almeno un NPC per l'UI iniziale
        gui_elements_dict = game_utils.setup_gui_elements(
            game_state.ui_manager_instance,
            all_npc_characters,
            current_selected_npc_idx_ui,
            time_btn_dims,
            ui_panel_height_val,
            config.SCREEN_WIDTH,
            config.SCREEN_HEIGHT
        )
        if gui_elements_dict.get('char_status_label'):
            gui_elements_dict['char_status_label'].set_text(f"Display: {all_npc_characters[current_selected_npc_idx_ui].name} (Space)")
    elif DEBUG_VERBOSE:
        print("MAIN WARNING: Nessun NPC inizializzato. Alcuni elementi UI potrebbero non essere creati o aggiornati.")


    main_screen_surface = game_state.screen
    game_clock = pygame.time.Clock()
    is_game_running = True
    show_debug_grid = False
    show_npc_on_screen_debug_info = False

    # --- Loop Principale del Gioco ---
    while is_game_running:
        # ... (loop di gioco come prima) ...
        # Assicurati che tutte le variabili usate nel loop siano state definite prima
        pass # Placeholder per il resto del loop

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
