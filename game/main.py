# simai/game/main.py
import pygame
import sys
import os
import logging
import random # Aggiunto per la generazione casuale di nomi/ecc.
from typing import Optional, Tuple, List, Dict, Any

# Importa dal package 'game'
from game import config
from game.src.utils import game as game_utils
from game.src.entities.character import Character 

from game.simai_save_load_system import (
    save_game_state as save_game_state_json,
    load_game_state as load_game_state_json,
    get_save_file_path
)

# --- IMPORT MANAGER ---
from game.src.managers.asset_manager import SpriteSheetManager # Già presente e corretto
from game.src.managers.time_manager import GameTimeManager
from game.src.managers.event_handler import handle_all_events
from game.src.managers.game_loop_updater import update_game_logic_for_tick
from game.src.managers.character_manager import CharacterManager
from game.src.world.world_manager import WorldManager
from game.src.utils.camera import Camera
import pygame_gui 
from game.src.modules.game_state_module import GameState

# --- IMPORT NUOVE SCHERMATE UI ---
# Assicurati che questi file esistano nel percorso corretto (es. game/src/ui/)
# e che le classi siano definite come discusso.
from game.src.ui.main_menu_screen import MainMenuScreen 
from game.src.ui.character_creation_screen import CharacterCreationScreen

# --- STATI DI FLUSSO DEL GIOCO ---
GAME_FLOW_STATE_MAIN_MENU = "main_menu"
GAME_FLOW_STATE_CHARACTER_CREATION = "character_creation"
GAME_FLOW_STATE_GAMEPLAY = "gameplay"
GAME_FLOW_STATE_QUIT = "quit"


# --- Configurazione Logging ---
log_level = logging.DEBUG if getattr(config, 'DEBUG_AI_ACTIVE', False) else logging.INFO
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(levelname)s - [%(name)s:%(funcName)s:%(lineno)d] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("SimAI_Main")


def setup_new_json_game(gs_param: GameState,
                        world_obstacle_rects_param: List[pygame.Rect],
                        char_mng_instance: CharacterManager,
                        player_character_instance: Optional[Character] = None, # PG creato dall'utente
                        debug_npc_data_list: Optional[List[Dict[str, Any]]] = None): # Dati per NPC di debug
    """Configura lo stato per una nuova partita, considerando un PG o NPC di debug."""
    logger.info("Avvio setup_new_json_game...")

    # Se c'è un PG, assicurati che sia il primo nella lista (o gestiscilo separatamente)
    if player_character_instance:
        if player_character_instance not in char_mng_instance.characters: # Usa la lista interna di CM
            char_mng_instance.add_character(player_character_instance) # Assicurati che CM lo gestisca
        # La lista in GameState verrà popolata da CharacterManager
        logger.info(f"Personaggio Giocatore '{player_character_instance.full_name}' pre-esistente e aggiunto a CharacterManager.")
        # gs_param.all_npc_characters_list = [player_character_instance] # Inizia con il PG
        # gs_param.all_npc_characters_list.extend(char_mng_instance.create_initial_npcs(exclude_characters=[player_character_instance]))
    
    if debug_npc_data_list:
        logger.info(f"Creazione {len(debug_npc_data_list)} NPC di debug...")
        # gs_param.all_npc_characters_list = [] # Inizia una lista pulita per i debug NPC
        for i, npc_data in enumerate(debug_npc_data_list):
            # Usa CharacterManager per creare questi NPC
            # Assicurati che spawn_random_npc o una funzione simile possa usare questi dati
            new_debug_npc = char_mng_instance.spawn_random_npc(
                gender=npc_data.get("gender", "Male"),
                position=(config.TILE_SIZE * (5 + i*2), config.TILE_SIZE * 5), # Posizione di esempio
                first_name_override=npc_data.get("first_name"),
                last_name_override=npc_data.get("last_name")
            )
            if new_debug_npc:
                # char_mng_instance.add_character(new_debug_npc) # spawn_random_npc dovrebbe già farlo
                logger.info(f"Creato NPC di debug: {new_debug_npc.full_name}")
            else:
                logger.warning(f"Fallita creazione NPC di debug per dati: {npc_data}")
    
    if not player_character_instance and not debug_npc_data_list:
        # Nessun PG o debug NPC, crea gli NPC iniziali standard
        # char_mng_instance.create_initial_npcs() gestisce l'aggiunta a gs_param.all_npc_characters_list
        # tramite il game_state reference nel CharacterManager
        logger.info("Nessun PG o Debug NPC specificato, creazione NPC iniziali standard.")
        initial_npcs = char_mng_instance.create_initial_npcs() # Questo dovrebbe popolare gs_param.all_npc_characters_list
        if not initial_npcs: # Se create_initial_npcs non restituisce nulla ma modifica game_state direttamente
             if not gs_param.all_npc_characters_list:
                logger.warning("Nessun NPC è stato inizializzato da CharacterManager (setup standard).")
        elif not gs_param.all_npc_characters_list: # Se create_initial_npcs ritorna ma non popola gs_param
            gs_param.all_npc_characters_list = initial_npcs


    # Assicurati che gs_param.all_npc_characters_list sia corretto dopo le operazioni sopra
    # CharacterManager dovrebbe essere la fonte di verità per la lista dei personaggi in GameState
    gs_param.all_npc_characters_list = char_mng_instance.get_all_characters() # Sincronizza con CM

    if not gs_param.all_npc_characters_list:
        logger.warning("Lista NPC ancora vuota dopo tutti i tentativi di creazione.")
    else:
        logger.info(f"{len(gs_param.all_npc_characters_list)} NPC totali in GameState pronti per il setup.")
        if hasattr(config, "DEFAULT_HOUSEHOLD_ID_FOR_NEW_NPCS"):
            for npc_char_iter in gs_param.all_npc_characters_list:
                if not npc_char_iter.household_id:
                    npc_char_iter.household_id = config.DEFAULT_HOUSEHOLD_ID_FOR_NEW_NPCS


    gs_param.a_star_grid_instance = game_utils.setup_pathfinding_grid(world_obstacle_rects_param)
    logger.info("Griglia di pathfinding A* creata.")

    gs_param.current_time_speed_index = getattr(config, 'TIME_SPEED_NORMAL_INDEX', 1)
    gs_param.is_paused_by_player = (gs_param.current_time_speed_index == 0)

    if gs_param.game_time_handler:
        gs_param.game_time_handler.reset_time_to_initial(
            config.INITIAL_START_HOUR, 
            getattr(config, "INITIAL_START_DAY", 1),
            getattr(config, "INITIAL_START_MONTH", 1),
            getattr(config, "INITIAL_START_YEAR", 1)
        )
        logger.info("Tempo di gioco resettato ai valori iniziali.")

    gs_param.bed_slot_1_occupied_by = None
    gs_param.bed_slot_2_occupied_by = None
    gs_param.is_sleep_fast_forward_active = False
    gs_param.previous_time_speed_index_before_sleep_ffwd = gs_param.current_time_speed_index
    gs_param.last_auto_save_time = pygame.time.get_ticks()
    logger.info("Stato nuova partita configurato.")


def main():
    pygame.init()
    pygame.font.init()
    logger.info(f"SimAI v{config.CORE_VERSION} (Build: {config.FULL_VERSION_INTERNAL}) avviato.")

    # --- Inizializzazione Pygame Screen e UIManager (una sola volta) ---
    try:
        screen_surface = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption(config.WINDOW_TITLE)
    except pygame.error as e:
        logger.critical(f"Impossibile inizializzare lo schermo Pygame: {e}. Uscita.")
        pygame.quit(); sys.exit()

    gui_theme_path = os.path.join(config.GAME_DIR_PATH, 'theme.json')
    try:
        ui_manager = pygame_gui.UIManager(
            (config.SCREEN_WIDTH, config.SCREEN_HEIGHT),
            theme_path=gui_theme_path if os.path.exists(gui_theme_path) else None
        )
        if not os.path.exists(gui_theme_path):
            logger.warning(f"File tema UI '{gui_theme_path}' non trovato. Uso tema di default.")
    except Exception as e_ui_manager: # Gestione più generica per errori imprevisti con UIManager
        logger.error(f"Errore durante l'inizializzazione di UIManager con tema '{gui_theme_path}': {e_ui_manager}. Tentativo senza tema.")
        try:
            ui_manager = pygame_gui.UIManager((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        except Exception as e_ui_manager_fallback:
            logger.critical(f"Errore critico inizializzazione UIManager (anche fallback): {e_ui_manager_fallback}. Uscita.")
            pygame.quit(); sys.exit()


    # --- SpriteSheetManager Globale (per anteprime e gioco) ---
    # La tua classe si chiama SpriteSheetManager, non AssetManager
    sprite_sheet_manager_global = SpriteSheetManager()
    try:
        # Carica solo gli sheet necessari per le anteprime qui, o tutti se preferisci
        sprite_sheet_manager_global.load_sheet("male_char", os.path.join("characters", "male.png"), config.SPRITE_FRAME_WIDTH, config.SPRITE_FRAME_HEIGHT)
        sprite_sheet_manager_global.load_sheet("female_char", os.path.join("characters", "female.png"), config.SPRITE_FRAME_WIDTH, config.SPRITE_FRAME_HEIGHT)
        
        # --- AGGIUNGI QUI IL CARICAMENTO DELLO SPRITESHEET DEI MOBILI ---
        # Assicurati che il percorso e il nome del file siano corretti
        # e che le dimensioni del frame siano appropriate se questo sheet è basato su frame,
        # altrimenti, se estrai solo rettangoli pixel, frame_width/height potrebbero essere meno critici qui
        # ma sono comunque richiesti da load_sheet. Usa dimensioni generiche se non applicabile (es. 1,1).
        # Tuttavia, è meglio se SpriteSheetManager.load_sheet non richiedesse frame_width/height
        # se lo sheet è solo per get_sprite_by_pixel_rect. Per ora, forniamoli.
        furniture_sheet_path = getattr(config, 'FURNITURE_SPRITESHEET_PATH', "furnitures/generic_furniture.png") # Prendi da config se definito
        furniture_frame_w = getattr(config, 'FURNITURE_DEFAULT_FRAME_WIDTH', 32) # Valore di default
        furniture_frame_h = getattr(config, 'FURNITURE_DEFAULT_FRAME_HEIGHT', 32) # Valore di default

        # La chiave qui DEVE corrispondere a quella usata in object_blueprints.json ("sprite_sheet_key")
        key_for_furniture_sheet = "furniture_sprites" # O la chiave che usi nei blueprint

        sprite_sheet_manager_global.load_sheet(
            key_for_furniture_sheet, 
            furniture_sheet_path, # Es: "furnitures/generic_furniture.png"
            furniture_frame_w,    # Larghezza frame di default per questo sheet (anche se estrai rect)
            furniture_frame_h     # Altezza frame di default
        )
        logger.info(f"Sprite sheet '{key_for_furniture_sheet}' caricato da '{furniture_sheet_path}'.")
        # ------------------------------------------------------------------

        logger.info("Sprite sheets per anteprima/base caricate in SpriteSheetManager globale.")
    except Exception as e_sprites_global:
        logger.error(f"Errore caricamento sprite sheet globali: {e_sprites_global}", exc_info=True)
        # Decidi se uscire o continuare con fallback


    if hasattr(game_utils, 'load_object_blueprints'):
        game_utils.load_object_blueprints() # Chiamato una volta all'inizio
    else:
        logger.critical("Funzione 'load_object_blueprints' non trovata in game_utils. Uscita.")
        pygame.quit(); sys.exit()

    # --- Variabili di Flusso e Dati tra Stati ---
    current_flow_state = GAME_FLOW_STATE_MAIN_MENU
    active_screen_module = None # Modulo UI attivo (MainMenu, CharacterCreation)
    player_character_creation_data: Optional[Dict[str, Any]] = None
    debug_npc_creation_data_list: Optional[List[Dict[str, Any]]] = None
    
    game_loop_running = True
    game_clock = pygame.time.Clock() # Clock principale per tutto

    while game_loop_running:
        time_delta_real_seconds = game_clock.tick(config.FPS) / 1000.0
        # Evita time_delta == 0 se possibile, specialmente per pygame_gui
        if time_delta_real_seconds <= 0: time_delta_real_seconds = 1/config.FPS 


        # --- Gestione Stati di Flusso (Menu, Creazione) ---
        if current_flow_state == GAME_FLOW_STATE_MAIN_MENU:
            if not active_screen_module or not isinstance(active_screen_module, MainMenuScreen):
                # MainMenuScreen NON ha bisogno di CharacterManager per creare NPC, passerà solo i dati.
                active_screen_module = MainMenuScreen(ui_manager, screen_surface, None, sprite_sheet_manager_global)
            
            # Il metodo .run() di MainMenuScreen gestirà il suo loop e gli eventi
            # Restituisce: next_flow_state_signal, (None per player_data), debug_npc_data (lista di dict)
            next_flow_state_signal, _, temp_debug_npc_data = active_screen_module.run()
            
            if next_flow_state_signal == GAME_FLOW_STATE_QUIT:
                game_loop_running = False
            elif next_flow_state_signal == GAME_FLOW_STATE_CHARACTER_CREATION:
                current_flow_state = GAME_FLOW_STATE_CHARACTER_CREATION
                player_character_creation_data = None # Resetta
                debug_npc_creation_data_list = None
                active_screen_module = None # Forza reinizializzazione prossimo stato
            elif next_flow_state_signal == GAME_FLOW_STATE_GAMEPLAY and temp_debug_npc_data: # Avvio Debug
                current_flow_state = GAME_FLOW_STATE_GAMEPLAY
                debug_npc_creation_data_list = temp_debug_npc_data
                player_character_creation_data = None
                active_screen_module = None
            # Altrimenti, rimane nel menu (gestito dal loop interno di MainMenuScreen.run())

        elif current_flow_state == GAME_FLOW_STATE_CHARACTER_CREATION:
            if not active_screen_module or not isinstance(active_screen_module, CharacterCreationScreen):
                # CharacterCreationScreen non ha bisogno di CharacterManager, restituisce solo dati.
                active_screen_module = CharacterCreationScreen(ui_manager, screen_surface, None, sprite_sheet_manager_global)

            # .run() restituisce i dati del personaggio (dict) o None se annullato/uscito
            returned_player_data = active_screen_module.run()

            if active_screen_module.is_running is False: # Schermata terminata
                if returned_player_data:
                    player_character_creation_data = returned_player_data
                    debug_npc_creation_data_list = None
                    current_flow_state = GAME_FLOW_STATE_GAMEPLAY
                else: # Annullato o uscito dalla creazione
                    current_flow_state = GAME_FLOW_STATE_MAIN_MENU
                active_screen_module = None # Forza reinizializzazione
        
        elif current_flow_state == GAME_FLOW_STATE_GAMEPLAY:
            # --- QUI INIZIA IL TUO SETUP E LOOP DI GIOCO ESISTENTE ---
            # Questo blocco viene eseguito una volta per configurare e avviare il gioco.
            
            logger.info("Entrata in GAME_FLOW_STATE_GAMEPLAY.")
            
            # 1. Inizializzazione GameState (come nel tuo main originale)
            game_state = GameState()
            game_state.screen = screen_surface # Riusa la superficie
            game_state.ui_manager_instance = ui_manager # Riusa l'UIManager globale

            # Caricamento Font (come nel tuo main originale)
            try:
                font_path = config.FONT_NAME if hasattr(config, 'FONT_NAME') and config.FONT_NAME and os.path.exists(config.FONT_NAME) else None
                game_state.main_font = pygame.font.Font(font_path, getattr(config, 'UI_FONT_SIZE', 18))
                game_state.debug_font = pygame.font.Font(font_path, 15)
            except Exception:
                logger.warning(f"Font '{getattr(config, 'FONT_NAME', 'N/A')}' non trovato. Tentativo con SysFont.")
                game_state.main_font = pygame.font.SysFont("arial", getattr(config, 'UI_FONT_SIZE', 18))
                game_state.debug_font = pygame.font.SysFont("monospace", 15)
            
            # Font Icone (come nel tuo main originale)
            ui_icon_font_instance: Optional[pygame.font.Font] = None 
            try:
                icon_font_path = getattr(config, 'UI_UNICODE_ICON_FONT_PATH', None)
                icon_font_size = getattr(config, 'UI_UNICODE_ICON_FONT_SIZE', 22) # Era 24, usa config
                if icon_font_path and os.path.exists(icon_font_path):
                    ui_icon_font_instance = pygame.font.Font(icon_font_path, icon_font_size)
                else:
                    ui_icon_font_instance = pygame.font.Font(None, icon_font_size) # Fallback
            except Exception as e_icon_font:
                logger.error(f"Errore caricamento font icone: {e_icon_font}.")
                ui_icon_font_instance = pygame.font.Font(None, getattr(config, 'UI_UNICODE_ICON_FONT_SIZE', 22))
            game_state.ui_icon_font = ui_icon_font_instance

            # SpriteSheetManager per GameState (usa l'istanza globale)
            game_state.sprite_sheet_manager = sprite_sheet_manager_global
            # Carica gli altri sprite sheet specifici per il gameplay se non già caricati globalmente
            try:
                game_state.sprite_sheet_manager.load_sheet("male_sleep", os.path.join("characters", config.SLEEP_SPRITESHEET_MALE_FILENAME), config.SLEEP_SPRITE_FRAME_WIDTH, config.SLEEP_SPRITE_FRAME_HEIGHT)
                game_state.sprite_sheet_manager.load_sheet("female_sleep", os.path.join("characters", config.SLEEP_SPRITESHEET_FEMALE_FILENAME), config.SLEEP_SPRITE_FRAME_WIDTH, config.SLEEP_SPRITE_FRAME_HEIGHT)
                game_state.sprite_sheet_manager.load_sheet("baby_bundle", os.path.join("characters", "bundles.png"), config.BUNDLE_FRAME_WIDTH, config.BUNDLE_FRAME_HEIGHT)
                logger.info("Sprite sheets specifici per gameplay caricati.")
            except Exception as e_sprites_game:
                logger.critical(f"Errore caricamento sprite sheet gameplay: {e_sprites_game}. Uscita.")
                game_loop_running = False; break # Esce dal loop while principale


            game_state.game_time_handler = GameTimeManager(
                initial_hour=config.INITIAL_START_HOUR,
                default_speed_index=getattr(config, 'TIME_SPEED_NORMAL_INDEX', 1)
            )
            
            # Ora CharacterManager può essere inizializzato con un GameState valido
            character_manager_ingame = CharacterManager(game_state, game_state.sprite_sheet_manager, game_state.main_font)
            game_state.character_manager_instance = character_manager_ingame

            world_manager_instance = WorldManager()
            camera_instance = Camera(config.SCREEN_WIDTH, config.SCREEN_HEIGHT,
                                     world_manager_instance.world_pixel_width,
                                     world_manager_instance.world_pixel_height)
            
            world_obstacle_rects: List[pygame.Rect] = []
            # Configurazione Oggetti Mondo (Letto, Bagno, ecc. - il tuo codice originale)
            bed_blueprint = game_utils.get_object_blueprint(getattr(config, "MAIN_BED_BLUEPRINT_KEY", "double_bed_blue"))
            if bed_blueprint:
                rect_info = bed_blueprint.get("sprite_rect_in_sheet", [0,0,64,96])
                game_state.bed_rect = pygame.Rect(config.DESIRED_BED_X, config.DESIRED_BED_Y, rect_info[2], rect_info[3])
                obs_rel = bed_blueprint.get("obstacle_rect_relative")
                if obs_rel: world_obstacle_rects.append(pygame.Rect(game_state.bed_rect.left + obs_rel[0], game_state.bed_rect.top + obs_rel[1], obs_rel[2], obs_rel[3]))
                else: world_obstacle_rects.append(game_state.bed_rect)
                game_utils.setup_object_interaction_points(game_state, "bed", bed_blueprint, game_state.bed_rect)
            else: logger.warning("Blueprint letto principale non trovato.")
            
            toilet_blueprint = game_utils.get_object_blueprint(getattr(config, "MAIN_TOILET_BLUEPRINT_KEY", "toilet_standard"))
            if toilet_blueprint:
                rect_info_toilet = toilet_blueprint.get("sprite_rect_in_sheet", [0,0,32,48])
                toilet_cfg_params = getattr(config, 'TOILET_RECT_PARAMS', {'x': 700, 'y': 300})
                game_state.toilet_rect_instance = pygame.Rect(toilet_cfg_params['x'], toilet_cfg_params['y'], rect_info_toilet[2], rect_info_toilet[3])
                obs_rel_toilet = toilet_blueprint.get("obstacle_rect_relative")
                if obs_rel_toilet: world_obstacle_rects.append(pygame.Rect(game_state.toilet_rect_instance.left + obs_rel_toilet[0], game_state.toilet_rect_instance.top + obs_rel_toilet[1], obs_rel_toilet[2], obs_rel_toilet[3]))
                else: world_obstacle_rects.append(game_state.toilet_rect_instance)
                game_utils.setup_object_interaction_points(game_state, "toilet", toilet_blueprint, game_state.toilet_rect_instance)
            else: logger.warning("Blueprint bagno principale non trovato.")

            current_selected_npc_idx_ui = 0 # Indice per la UI di gioco
            created_player_char_instance: Optional[Character] = None

            if player_character_creation_data:
                logger.info(f"Creazione PG dai dati UI: {player_character_creation_data}")
                # Assumi una nuova funzione in CharacterManager o usa spawn_random_npc con overrides
                # Esempio:
                created_player_char_instance = character_manager_ingame.create_character_from_data(
                    player_character_creation_data,
                    is_player=True # Potrebbe essere un flag utile
                )
                if created_player_char_instance:
                     logger.info(f"Personaggio Giocatore '{created_player_char_instance.full_name}' creato e aggiunto.")
                     # Non serve fare add_character esplicitamente se create_character_from_data lo fa
                else:
                     logger.error("Fallita creazione del Personaggio Giocatore dai dati UI.")
                     # Fallback a personaggio di default o esci? Per ora continua.

            # Gestione caricamento/nuova partita (considerando PG e Debug NPC)
            save_file_json = get_save_file_path(config.DEFAULT_SAVE_FILENAME)
            load_on_startup = getattr(config, 'LOAD_GAME_ON_STARTUP', True)
            
            # Se abbiamo creato un PG o NPC di debug, generalmente iniziamo una NUOVA partita,
            # a meno che non si voglia un sistema "aggiungi a partita esistente".
            # Per ora, la creazione di PG o NPC di debug forza una nuova partita (non carica da file).
            start_fresh_game_after_menu = bool(player_character_creation_data or debug_npc_creation_data_list)

            if not start_fresh_game_after_menu and load_on_startup and os.path.exists(save_file_json):
                logger.info(f"Trovato file di salvataggio: {save_file_json}. Tentativo di caricamento.")
                loaded_ok = load_game_state_json(game_state, game_state.sprite_sheet_manager, game_state.main_font, character_manager_ingame)
                if not loaded_ok:
                    logger.warning("Caricamento fallito, inizio nuova partita standard.")
                    # Nessun PG o Debug NPC qui, quindi setup_new_json_game creerà NPC di default
                    setup_new_json_game(game_state, world_obstacle_rects, character_manager_ingame)
                else:
                    logger.info("Partita caricata con successo.")
                    if hasattr(character_manager_ingame, 'resolve_uuid_references_after_load'):
                         character_manager_ingame.resolve_uuid_references_after_load(character_manager_ingame.get_all_characters())
            else:
                if start_fresh_game_after_menu:
                    logger.info("Inizio nuova partita dopo Menu/Creazione.")
                elif not os.path.exists(save_file_json): 
                    logger.info(f"Nessun file JSON '{save_file_json}' trovato (nuova partita).")
                else: 
                    logger.info("Caricamento partita saltato (LOAD_GAME_ON_STARTUP=False, nuova partita).")
                
                setup_new_json_game(game_state, world_obstacle_rects, character_manager_ingame, 
                                    player_character_instance=created_player_char_instance,
                                    debug_npc_data_list=debug_npc_creation_data_list)

            if not game_state.all_npc_characters_list: # game_state.all_npc_characters_list è ora popolato da CharacterManager
                game_state.all_npc_characters_list = character_manager_ingame.get_all_characters()

            if not game_state.all_npc_characters_list: 
                logger.critical("Lista NPC vuota dopo setup/load gameplay. Uscita.")
                game_loop_running = False; break 
            else:
                logger.info(f"Gameplay avviato con {len(game_state.all_npc_characters_list)} personaggi.")
                # Se è stato creato un PG, selezionalo nella UI
                if created_player_char_instance:
                    try:
                        current_selected_npc_idx_ui = game_state.all_npc_characters_list.index(created_player_char_instance)
                    except ValueError:
                        logger.warning("PG creato non trovato nella lista per selezione UI, default a 0.")
                        current_selected_npc_idx_ui = 0
                elif not game_state.all_npc_characters_list: # Check aggiuntivo
                    current_selected_npc_idx_ui = -1 # Nessun NPC da selezionare
                else:
                    current_selected_npc_idx_ui = 0 # Default al primo NPC


            # Setup GUI Elementi di gioco (il tuo codice originale)
            gui_elements_dict: Dict[str, pygame_gui.core.UIElement] = {}
            loaded_ui_icons, ui_speed_icons, bed_images_loaded, need_bar_icon_dimensions = \
                 game_utils.load_all_game_assets(game_state.ui_icon_font)
            if bed_images_loaded: game_state.bed_images = bed_images_loaded
            
            if game_state.all_npc_characters_list and game_state.ui_manager_instance and current_selected_npc_idx_ui != -1:
                gui_elements_dict = game_utils.setup_gui_elements(
                    game_state.ui_manager_instance, game_state.all_npc_characters_list,
                    current_selected_npc_idx_ui, 
                    loaded_ui_icons.get("pause").get_size() if loaded_ui_icons.get("pause") else (30,30),
                    getattr(config, 'PANEL_UI_HEIGHT', 160), # Era 150
                    config.SCREEN_WIDTH, config.SCREEN_HEIGHT
                )
                if gui_elements_dict.get('char_status_label') and 0 <= current_selected_npc_idx_ui < len(game_state.all_npc_characters_list):
                    sel_npc_for_init_label = game_state.all_npc_characters_list[current_selected_npc_idx_ui]
                    gui_elements_dict['char_status_label'].set_text(f"NPC: {sel_npc_for_init_label.name} ({sel_npc_for_init_label.get_formatted_age_string()})")

            # Variabili per il loop di gioco interno (dal tuo codice originale)
            is_game_running_internal_loop = True # Rinominata per chiarezza
            show_debug_grid = False
            show_npc_on_screen_debug_info = game_state.DEBUG_AI_ACTIVE
            tile_images_dict: Dict[int, pygame.Surface] = {}
            if hasattr(config, "TILE_IMAGE_MAPPING"):
                tile_base_path = os.path.join(config.IMAGE_PATH, "tiles")
                for tile_id, image_filename in config.TILE_IMAGE_MAPPING.items():
                    img = game_utils.load_image(image_filename, (config.TILE_SIZE, config.TILE_SIZE), base_path=tile_base_path)
                    if img: tile_images_dict[tile_id] = img

            logger.info("Inizio loop di gioco effettivo.")
            # --- INIZIO LOOP DI GIOCO ESISTENTE ---
            while is_game_running_internal_loop:
                time_delta_ingame = game_clock.tick(config.FPS) / 1000.0
                if time_delta_ingame <= 0: time_delta_ingame = 1/config.FPS

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        is_game_running_internal_loop = False
                        game_loop_running = False # Esce dal loop esterno
                        break
                    
                    game_state.ui_manager_instance.process_events(event) # Passa eventi all'UIManager di gioco
                    
                    # handle_all_events (tuo codice)
                    current_selected_npc_idx_ui, show_debug_grid, show_npc_on_screen_debug_info, game_should_continue = \
                        handle_all_events(event, game_state, current_selected_npc_idx_ui, 
                                          show_debug_grid, show_npc_on_screen_debug_info)
                    if not game_should_continue:
                        is_game_running_internal_loop = False
                        # Decidi se tornare al menu o chiudere
                        # current_flow_state = GAME_FLOW_STATE_MAIN_MENU 
                        game_loop_running = False # Per ora esce
                        break
                if not is_game_running_internal_loop or not game_loop_running: break

                update_game_logic_for_tick(game_state, time_delta_ingame)
                
                if camera_instance: # Il tuo codice camera
                    target_for_cam = None
                    if game_state.all_npc_characters_list and \
                       0 <= current_selected_npc_idx_ui < len(game_state.all_npc_characters_list) and \
                       current_selected_npc_idx_ui != -1:
                        target_for_cam = game_state.all_npc_characters_list[current_selected_npc_idx_ui]
                    camera_instance.set_target(target_for_cam)
                    camera_instance.update()

                # Aggiornamento testi UI dinamici (tuo codice)
                if game_state.ui_manager_instance and gui_elements_dict:
                    # ... (il tuo codice per aggiornare time_label, char_status_label, ecc.)
                    if gui_elements_dict.get('time_label') and game_state.game_time_handler:
                        gui_elements_dict['time_label'].set_text(game_state.game_time_handler.get_time_display_text())
                    
                    selected_npc_for_ui_update = None
                    if game_state.all_npc_characters_list and \
                       0 <= current_selected_npc_idx_ui < len(game_state.all_npc_characters_list) and \
                       current_selected_npc_idx_ui != -1:
                        selected_npc_for_ui_update = game_state.all_npc_characters_list[current_selected_npc_idx_ui]

                    if selected_npc_for_ui_update:
                        if gui_elements_dict.get('char_status_label'): gui_elements_dict['char_status_label'].set_text(f"NPC: {selected_npc_for_ui_update.name} ({selected_npc_for_ui_update.get_formatted_age_string()})")
                        if gui_elements_dict.get('action_label'): gui_elements_dict['action_label'].set_text(config.UI_LABEL_ACTION + selected_npc_for_ui_update.current_action)
                        if gui_elements_dict.get('finance_label') and selected_npc_for_ui_update.finances: gui_elements_dict['finance_label'].set_text(config.UI_LABEL_FINANCE + f"${selected_npc_for_ui_update.finances.get_balance():.0f}")
                        if gui_elements_dict.get('mood_label'): # Prima controlla se la label esiste
                            if hasattr(selected_npc_for_ui_update, 'mood') and selected_npc_for_ui_update.mood: # Poi controlla se l'NPC ha il componente 'mood'
                                gui_elements_dict['mood_label'].set_text(config.UI_LABEL_MOOD + selected_npc_for_ui_update.mood.get_dominant_emotion())
                            else: # Fallback se l'NPC non ha il componente mood per qualche motivo
                                gui_elements_dict['mood_label'].set_text(config.UI_LABEL_MOOD + "N/D")
                        if gui_elements_dict.get('pregnancy_label') and selected_npc_for_ui_update.status:
                            if selected_npc_for_ui_update.status.is_pregnant:
                                preg_term = getattr(config, 'PREGNANCY_TERM_GAME_DAYS', 24)
                                gui_elements_dict['pregnancy_label'].set_text(f"Incinta: {int(selected_npc_for_ui_update.status.pregnancy_progress_days)}/{preg_term}gg"); gui_elements_dict['pregnancy_label'].visible = True
                            else: gui_elements_dict['pregnancy_label'].visible = False
                    else: 
                        if gui_elements_dict.get('char_status_label'): gui_elements_dict['char_status_label'].set_text("NPC: -")
                        if gui_elements_dict.get('action_label'): gui_elements_dict['action_label'].set_text(config.UI_LABEL_ACTION + "-")
                        if gui_elements_dict.get('finance_label'): gui_elements_dict['finance_label'].set_text(config.UI_LABEL_FINANCE + "-")
                        if gui_elements_dict.get('mood_label'): gui_elements_dict['mood_label'].set_text(config.UI_LABEL_MOOD + "-")
                        if gui_elements_dict.get('pregnancy_label'): gui_elements_dict['pregnancy_label'].visible = False
                
                # Disegno (tuo codice)
                current_sky_col = game_state.game_time_handler.current_sky_color if game_state.game_time_handler else (135, 206, 235)
                game_state.screen.fill(current_sky_col)

                if world_manager_instance and camera_instance:
                     world_manager_instance.draw_map_portion(game_state.screen, camera_instance.camera_rect, tile_images_dict)
                     if show_debug_grid: world_manager_instance.draw_world_grid_on_surface(game_state.screen, camera_instance.camera_rect)
                
                if game_state.bed_rect and game_state.bed_images.get("base") and camera_instance:
                    game_state.screen.blit(game_state.bed_images["base"], camera_instance.apply_to_rect(game_state.bed_rect).topleft)
                if game_state.toilet_rect_instance and camera_instance: # Disegno toilette
                    # Idealmente, caricheresti uno sprite anche per la toilette
                    toilet_sprite_blueprint = game_utils.get_object_blueprint(getattr(config, "MAIN_TOILET_BLUEPRINT_KEY", "toilet_standard"))
                    if toilet_sprite_blueprint and game_state.sprite_sheet_manager:
                        toilet_sprite = game_utils.get_sprite_from_blueprint(toilet_sprite_blueprint, game_state.sprite_sheet_manager)
                        if toilet_sprite:
                             game_state.screen.blit(toilet_sprite, camera_instance.apply_to_rect(game_state.toilet_rect_instance).topleft)
                        else: # Fallback a rettangolo colorato se lo sprite non può essere caricato
                            pygame.draw.rect(game_state.screen, getattr(config, 'TOILET_COLOR', (200,200,200)), camera_instance.apply_to_rect(game_state.toilet_rect_instance))
                    else: # Fallback se non c'è blueprint o sprite sheet manager
                        pygame.draw.rect(game_state.screen, getattr(config, 'TOILET_COLOR', (200,200,200)), camera_instance.apply_to_rect(game_state.toilet_rect_instance))


                for npc_char_iter in game_state.all_npc_characters_list:
                    font_debug = game_state.debug_font if show_npc_on_screen_debug_info else None
                    text_col = game_state.game_time_handler.ui_text_color if game_state.game_time_handler else config.TEXT_COLOR_LIGHT
                    npc_char_iter.draw(screen=game_state.screen, camera=camera_instance, font=font_debug, text_color=text_col)
                
                if game_state.bed_rect and game_state.bed_images.get("cover") and camera_instance:
                    if any(npc.is_on_bed and npc.bed_object_id == "main_bed" for npc in game_state.all_npc_characters_list):
                        bed_rect_on_screen = camera_instance.apply_to_rect(game_state.bed_rect)
                        cover_offset_y = getattr(config, 'BED_COVER_DRAW_OFFSET_Y', 26)
                        game_state.screen.blit(game_state.bed_images["cover"], (bed_rect_on_screen.left, bed_rect_on_screen.top + cover_offset_y))
                
                sel_npc_for_manual_ui = None # Rinominato per evitare conflitto
                if game_state.all_npc_characters_list and 0 <= current_selected_npc_idx_ui < len(game_state.all_npc_characters_list) and current_selected_npc_idx_ui != -1:
                    sel_npc_for_manual_ui = game_state.all_npc_characters_list[current_selected_npc_idx_ui]

                if sel_npc_for_manual_ui : 
                    game_utils.draw_all_manual_ui_elements(
                        screen_surface=game_state.screen, loaded_icons_map=loaded_ui_icons, 
                        speed_button_icons=ui_speed_icons, current_selected_speed_idx=game_state.current_time_speed_index,
                        # time_label_gui_obj rimosso
                        current_day_period_name=game_state.game_time_handler.current_period_name if game_state.game_time_handler else "",
                        selected_character_to_display=sel_npc_for_manual_ui,
                        bottom_panel_gui_obj=gui_elements_dict.get('bottom_panel'),
                        needs_bars_start_x_in_panel=gui_elements_dict.get('needs_bar_area_x_in_panel', 0),
                        needs_bars_start_y_in_panel=gui_elements_dict.get('needs_bar_area_y_in_panel', 0),
                        ui_current_text_color=game_state.game_time_handler.ui_text_color if game_state.game_time_handler else config.TEXT_COLOR_DARK,
                        default_ui_font=game_state.main_font,
                        time_control_buttons_rect_list=gui_elements_dict.get('time_button_rects', []),
                        need_icon_dimensions=need_bar_icon_dimensions,
                        gui_elements_ref = gui_elements_dict
                    )

                game_state.ui_manager_instance.draw_ui(game_state.screen)
                pygame.display.flip()
            # --- FINE LOOP DI GIOCO ESISTENTE ---
            
            logger.info("Uscita dal loop di GAMEPLAY.")
            if getattr(config, 'SAVE_GAME_ON_EXIT', False) and game_loop_running: # Salva solo se non stiamo uscendo del tutto
                logger.info("Salvataggio partita all'uscita dal gameplay...")
                save_game_state_json(game_state)
            
            # Dopo che il loop di gameplay termina, decidiamo cosa fare:
            if game_loop_running: # Se non è un quit generale, torna al menu
                current_flow_state = GAME_FLOW_STATE_MAIN_MENU
                active_screen_module = None # Forza reinizializzazione menu
                player_character_creation_data = None
                debug_npc_creation_data_list = None
            # Altrimenti, game_loop_running è False e il while esterno terminerà.

        elif current_flow_state == GAME_FLOW_STATE_QUIT: # Aggiunto per gestire l'uscita esplicita
            game_loop_running = False

        # L'update dell'ui_manager e il flip del display sono gestiti
        # all'interno dei loop .run() delle schermate UI o nel loop di gameplay.

    logger.info("SimAI sta terminando.")
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()