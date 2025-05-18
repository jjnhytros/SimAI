# simai/game/main.py
import pygame
import sys
import os
import logging
from typing import Optional, Tuple, List, Dict, Any

# Importa dal package 'game'
from game import config
from game.src.utils import game as game_utils
from game.src.entities.character import Character # Importato per setup_new_json_game e type hints

from game.simai_save_load_system import (
    save_game_state as save_game_state_json,
    load_game_state as load_game_state_json,
    get_save_file_path
)

# --- IMPORT MANAGER ---
from game.src.managers.asset_manager import SpriteSheetManager
from game.src.managers.time_manager import GameTimeManager
from game.src.managers.event_handler import handle_all_events
from game.src.managers.game_loop_updater import update_game_logic_for_tick
from game.src.managers.character_manager import CharacterManager
from game.src.world.world_manager import WorldManager
from game.src.utils.camera import Camera
import pygame_gui # Per il UI Manager
from game.src.modules.game_state_module import GameState # Classe per lo stato del gioco


# --- Configurazione Logging ---
log_level = logging.DEBUG if getattr(config, 'DEBUG_AI_ACTIVE', False) else logging.INFO
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(levelname)s - [%(name)s:%(funcName)s:%(lineno)d] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger_main = logging.getLogger("SimAI_Main")


def setup_new_json_game(gs_param: GameState,
                        world_obstacle_rects_param: List[pygame.Rect],
                        char_mng_instance: CharacterManager): # Modificato per accettare CharacterManager
    """Configura lo stato per una nuova partita."""
    logger_main.info("Avvio setup_new_json_game...")

    gs_param.all_npc_characters_list = char_mng_instance.create_initial_npcs()

    if not gs_param.all_npc_characters_list:
        logger_main.warning("Nessun NPC è stato inizializzato da CharacterManager.")
    else:
        logger_main.info(f"{len(gs_param.all_npc_characters_list)} NPC inizializzati da CharacterManager.")
        # Assicurati che gli NPC abbiano un household_id se usi inventari domestici
        if hasattr(config, "DEFAULT_HOUSEHOLD_ID_FOR_NEW_NPCS"):
            for npc_char_iter in gs_param.all_npc_characters_list:
                if not npc_char_iter.household_id: # Imposta solo se non già definito (es. da caricamento)
                    npc_char_iter.household_id = config.DEFAULT_HOUSEHOLD_ID_FOR_NEW_NPCS
                    logger_main.debug(f"Assegnato household_id '{npc_char_iter.household_id}' a {npc_char_iter.name}")

    gs_param.a_star_grid_instance = game_utils.setup_pathfinding_grid(world_obstacle_rects_param)
    logger_main.info("Griglia di pathfinding A* creata.")

    gs_param.current_time_speed_index = getattr(config, 'TIME_SPEED_NORMAL_INDEX', 1)
    gs_param.is_paused_by_player = (gs_param.current_time_speed_index == 0)

    if gs_param.game_time_handler:
        gs_param.game_time_handler.reset_time_to_initial(
            config.INITIAL_START_HOUR, 
            getattr(config, "INITIAL_START_DAY", 1),
            getattr(config, "INITIAL_START_MONTH", 1),
            getattr(config, "INITIAL_START_YEAR", 1)
        )
        logger_main.info("Tempo di gioco resettato ai valori iniziali.")

    # Reset stati specifici
    gs_param.bed_slot_1_occupied_by = None
    gs_param.bed_slot_2_occupied_by = None
    # ... (altri reset come food_visible, ecc. se li usi)
    gs_param.is_sleep_fast_forward_active = False
    gs_param.previous_time_speed_index_before_sleep_ffwd = gs_param.current_time_speed_index
    gs_param.last_auto_save_time = pygame.time.get_ticks() # Resetta timer autosalvataggio
    logger_main.info("Stato nuova partita configurato.")


def main():
    pygame.init()
    pygame.font.init()
    logger_main.info(f"SimAI v{config.CORE_VERSION} (Build: {config.FULL_VERSION_INTERNAL}) avviato.")

    if hasattr(game_utils, 'load_object_blueprints'):
        game_utils.load_object_blueprints()
    else:
        logger_main.critical("Funzione 'load_object_blueprints' non trovata in game_utils. Uscita.")
        pygame.quit(); sys.exit()

    game_state = GameState()

    try:
        game_state.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption(config.WINDOW_TITLE)
    except pygame.error as e:
        logger_main.critical(f"Impossibile inizializzare lo schermo Pygame: {e}. Uscita.")
        pygame.quit(); sys.exit()

    # Caricamento Font Principali
    try:
        font_path = config.FONT_NAME if hasattr(config, 'FONT_NAME') and config.FONT_NAME and os.path.exists(config.FONT_NAME) else None
        game_state.main_font = pygame.font.Font(font_path, getattr(config, 'UI_FONT_SIZE', 18))
        game_state.debug_font = pygame.font.Font(font_path, 15)
    except Exception: # Gestione fallback font
        logger_main.warning(f"Font '{getattr(config, 'FONT_NAME', 'N/A')}' non trovato. Tentativo con SysFont.")
        try:
            game_state.main_font = pygame.font.SysFont("arial", getattr(config, 'UI_FONT_SIZE', 18))
            game_state.debug_font = pygame.font.SysFont("monospace", 15)
        except Exception as e_font_sys:
             logger_main.critical(f"Errore critico anche con SysFont: {e_font_sys}. Uscita.")
             pygame.quit(); sys.exit()

    # >>> Caricamento Font per Icone Unicode <<<
    ui_icon_font_instance: Optional[pygame.font.Font] = None 
    try:
        icon_font_path = getattr(config, 'UI_UNICODE_ICON_FONT_PATH', None)
        icon_font_size = getattr(config, 'UI_UNICODE_ICON_FONT_SIZE', 24)
        if icon_font_path and os.path.exists(icon_font_path):
            ui_icon_font_instance = pygame.font.Font(icon_font_path, icon_font_size)
            logger_main.info(f"Font per icone Unicode '{icon_font_path}' caricato (size: {icon_font_size}).")
        else:
            if icon_font_path:
                 logger_main.warning(f"Font per icone Unicode '{icon_font_path}' non trovato.")
            else:
                 logger_main.info("Nessun UI_UNICODE_ICON_FONT_PATH specificato in config.")
            logger_main.info(f"Uso font di default di Pygame (size: {icon_font_size}) per le icone Unicode come fallback.")
            ui_icon_font_instance = pygame.font.Font(None, icon_font_size)
    except Exception as e_icon_font:
        logger_main.error(f"Errore durante il caricamento del font per icone Unicode: {e_icon_font}. Uso font di default.")
        ui_icon_font_instance = pygame.font.Font(None, getattr(config, 'UI_UNICODE_ICON_FONT_SIZE', 24))
    
    game_state.ui_icon_font = ui_icon_font_instance
    
    game_state.sprite_sheet_manager = SpriteSheetManager()
    try:
        game_state.sprite_sheet_manager.load_sheet("male_char", os.path.join("characters", "male.png"), config.SPRITE_FRAME_WIDTH, config.SPRITE_FRAME_HEIGHT)
        game_state.sprite_sheet_manager.load_sheet("female_char", os.path.join("characters", "female.png"), config.SPRITE_FRAME_WIDTH, config.SPRITE_FRAME_HEIGHT)
        game_state.sprite_sheet_manager.load_sheet("male_sleep", os.path.join("characters", config.SLEEP_SPRITESHEET_MALE_FILENAME), config.SLEEP_SPRITE_FRAME_WIDTH, config.SLEEP_SPRITE_FRAME_HEIGHT)
        game_state.sprite_sheet_manager.load_sheet("female_sleep", os.path.join("characters", config.SLEEP_SPRITESHEET_FEMALE_FILENAME), config.SLEEP_SPRITE_FRAME_WIDTH, config.SLEEP_SPRITE_FRAME_HEIGHT)
        game_state.sprite_sheet_manager.load_sheet("baby_bundle", os.path.join("characters", "bundles.png"), config.BUNDLE_FRAME_WIDTH, config.BUNDLE_FRAME_HEIGHT)
        # Carica spritesheet mobili se necessario
        # furniture_ss_path = getattr(config, 'FURNITURE_SPRITESHEET_PATH', "furnitures/generic_furniture.png")
        # game_state.sprite_sheet_manager.load_sheet("furniture_sprites", furniture_ss_path, 32, 32)
        logger_main.info("Sprite sheets principali caricati.")
    except Exception as e_sprites:
        logger_main.critical(f"Errore critico nel caricamento degli sprite sheet: {e_sprites}. Uscita.")
        pygame.quit(); sys.exit()

    game_state.game_time_handler = GameTimeManager(
        initial_hour=config.INITIAL_START_HOUR,
        default_speed_index=getattr(config, 'TIME_SPEED_NORMAL_INDEX', 1)
    )
    
    # Istanzia CharacterManager DOPO che game_state e i suoi attributi base sono pronti
    character_manager = CharacterManager(game_state, game_state.sprite_sheet_manager, game_state.main_font)
    game_state.character_manager_instance = character_manager # Rendi accessibile tramite game_state

    world_manager_instance = WorldManager()
    camera_instance = Camera(config.SCREEN_WIDTH, config.SCREEN_HEIGHT,
                             world_manager_instance.world_pixel_width,
                             world_manager_instance.world_pixel_height)
    
    gui_theme_path = os.path.join(config.GAME_DIR_PATH, 'theme.json')
    game_state.ui_manager_instance = pygame_gui.UIManager(
        (config.SCREEN_WIDTH, config.SCREEN_HEIGHT),
        theme_path=gui_theme_path if os.path.exists(gui_theme_path) else None
    )
    if not os.path.exists(gui_theme_path) and game_state.DEBUG_AI_ACTIVE:
            logger_main.warning(f"File tema UI '{gui_theme_path}' non trovato.")

    world_obstacle_rects: List[pygame.Rect] = []
    # Configurazione Oggetti Mondo (Letto, Bagno, ecc.)
    # Letto
    bed_blueprint = game_utils.get_object_blueprint(getattr(config, "MAIN_BED_BLUEPRINT_KEY", "double_bed_blue"))
    if bed_blueprint:
        rect_info = bed_blueprint.get("sprite_rect_in_sheet", [0,0,64,96])
        game_state.bed_rect = pygame.Rect(config.DESIRED_BED_X, config.DESIRED_BED_Y, rect_info[2], rect_info[3])
        obs_rel = bed_blueprint.get("obstacle_rect_relative")
        if obs_rel: world_obstacle_rects.append(pygame.Rect(game_state.bed_rect.left + obs_rel[0], game_state.bed_rect.top + obs_rel[1], obs_rel[2], obs_rel[3]))
        else: world_obstacle_rects.append(game_state.bed_rect)
        # Imposta punti interazione/sonno da blueprint in game_state
        game_utils.setup_object_interaction_points(game_state, "bed", bed_blueprint, game_state.bed_rect) # Funzione helper
        logger_main.debug(f"Letto '{getattr(config, 'MAIN_BED_BLUEPRINT_KEY', 'double_bed_blue')}' configurato.")
    else: logger_main.warning("Blueprint letto principale non trovato.")
    # Bagno
    toilet_blueprint = game_utils.get_object_blueprint(getattr(config, "MAIN_TOILET_BLUEPRINT_KEY", "toilet_standard"))
    if toilet_blueprint:
        rect_info_toilet = toilet_blueprint.get("sprite_rect_in_sheet", [0,0,32,48])
        toilet_cfg_params = getattr(config, 'TOILET_RECT_PARAMS', {'x': 700, 'y': 300}) # Posizione da config
        game_state.toilet_rect_instance = pygame.Rect(toilet_cfg_params['x'], toilet_cfg_params['y'], rect_info_toilet[2], rect_info_toilet[3])
        obs_rel_toilet = toilet_blueprint.get("obstacle_rect_relative")
        if obs_rel_toilet: world_obstacle_rects.append(pygame.Rect(game_state.toilet_rect_instance.left + obs_rel_toilet[0], game_state.toilet_rect_instance.top + obs_rel_toilet[1], obs_rel_toilet[2], obs_rel_toilet[3]))
        else: world_obstacle_rects.append(game_state.toilet_rect_instance)
        game_utils.setup_object_interaction_points(game_state, "toilet", toilet_blueprint, game_state.toilet_rect_instance) # Funzione helper
        logger_main.debug(f"Bagno '{getattr(config, 'MAIN_TOILET_BLUEPRINT_KEY', 'toilet_standard')}' configurato.")
    else: logger_main.warning("Blueprint bagno principale non trovato.")
    
    current_selected_npc_idx_ui = 0
    gui_elements_dict: Dict[str, pygame_gui.core.UIElement] = {}
    
    save_file_json = get_save_file_path(config.DEFAULT_SAVE_FILENAME)
    load_on_startup = getattr(config, 'LOAD_GAME_ON_STARTUP', True)
    if load_on_startup and os.path.exists(save_file_json):
        logger_main.info(f"Trovato file di salvataggio: {save_file_json}. Tentativo di caricamento.")
        loaded_ok = load_game_state_json(game_state, game_state.sprite_sheet_manager, game_state.main_font, character_manager) # Passa CharacterManager
        if not loaded_ok:
            logger_main.warning("Caricamento fallito, inizio nuova partita.")
            setup_new_json_game(game_state, world_obstacle_rects, character_manager)
        else:
            logger_main.info("Partita caricata con successo.")
            # Risolvi riferimenti UUID dopo caricamento (es. target_partner)
            if hasattr(character_manager, 'resolve_uuid_references_after_load'):
                 character_manager.resolve_uuid_references_after_load(game_state.all_npc_characters_list)
            if not game_state.all_npc_characters_list or not (0 <= current_selected_npc_idx_ui < len(game_state.all_npc_characters_list)):
                current_selected_npc_idx_ui = 0 if game_state.all_npc_characters_list else -1
    else:
        if not os.path.exists(save_file_json): logger_main.info(f"Nessun file JSON '{save_file_json}' trovato.")
        else: logger_main.info("Caricamento partita saltato (LOAD_GAME_ON_STARTUP=False).")
        logger_main.info("Inizio nuova partita.")
        setup_new_json_game(game_state, world_obstacle_rects, character_manager)

    if not game_state.all_npc_characters_list: logger_main.warning("Lista NPC vuota dopo setup/load.")
    
    loaded_ui_icons, ui_speed_icons, bed_images_loaded, need_bar_icon_dimensions = \
        game_utils.load_all_game_assets(ui_icon_font_instance) # <-- MODIFICA QUI
    if bed_images_loaded: game_state.bed_images = bed_images_loaded

    if game_state.all_npc_characters_list and game_state.ui_manager_instance and current_selected_npc_idx_ui != -1:
        gui_elements_dict = game_utils.setup_gui_elements(
            game_state.ui_manager_instance, game_state.all_npc_characters_list,
            current_selected_npc_idx_ui, 
            loaded_ui_icons.get("pause").get_size() if loaded_ui_icons.get("pause") else (30,30), # time_button_dimensions
            getattr(config, 'PANEL_UI_HEIGHT', 150),
            config.SCREEN_WIDTH, config.SCREEN_HEIGHT
        )
        # Aggiorna testi UI iniziali in setup_gui_elements o qui
        if gui_elements_dict.get('char_status_label') and 0 <= current_selected_npc_idx_ui < len(game_state.all_npc_characters_list):
            sel_npc_for_init_label = game_state.all_npc_characters_list[current_selected_npc_idx_ui]
            gui_elements_dict['char_status_label'].set_text(f"NPC: {sel_npc_for_init_label.name} ({sel_npc_for_init_label.get_formatted_age_string()})")
    elif game_state.DEBUG_AI_ACTIVE:
        logger_main.debug("Nessun NPC o UI Manager, o indice NPC non valido. UI completa non inizializzata.")

    game_clock = pygame.time.Clock()
    is_game_running = True
    show_debug_grid = False
    show_npc_on_screen_debug_info = game_state.DEBUG_AI_ACTIVE
    
    tile_images_dict: Dict[int, pygame.Surface] = {}
    # Popola tile_images_dict con le immagini dei tile della mappa qui
    if hasattr(config, "TILE_IMAGE_MAPPING"):
        tile_base_path = os.path.join(config.IMAGE_PATH, "tiles")
        for tile_id, image_filename in config.TILE_IMAGE_MAPPING.items():
            img = game_utils.load_image(image_filename, (config.TILE_SIZE, config.TILE_SIZE), base_path=tile_base_path)
            if img: tile_images_dict[tile_id] = img
            else: logger_main.warning(f"Immagine tile '{image_filename}' per ID {tile_id} non caricata.")


    logger_main.info("Inizio loop principale del gioco.")
    while is_game_running:
        time_delta_real_seconds = game_clock.tick(config.FPS) / 1000.0
        if time_delta_real_seconds == 0: continue

        for event in pygame.event.get():
            current_selected_npc_idx_ui, show_debug_grid, show_npc_on_screen_debug_info, is_game_running = \
                handle_all_events(event, game_state, current_selected_npc_idx_ui, 
                                  show_debug_grid, show_npc_on_screen_debug_info)
            if not is_game_running: break
        if not is_game_running: break

        update_game_logic_for_tick(game_state, time_delta_real_seconds)
        
        if camera_instance:
            if game_state.all_npc_characters_list and \
               0 <= current_selected_npc_idx_ui < len(game_state.all_npc_characters_list) and \
               current_selected_npc_idx_ui != -1:
                camera_instance.set_target(game_state.all_npc_characters_list[current_selected_npc_idx_ui])
            else: camera_instance.set_target(None)
            camera_instance.update()

        # Aggiornamento testi UI dinamici
        if game_state.ui_manager_instance and gui_elements_dict:
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
                if gui_elements_dict.get('mood_label') and selected_npc_for_ui_update.emotions: gui_elements_dict['mood_label'].set_text(config.UI_LABEL_MOOD + selected_npc_for_ui_update.emotions.get_dominant_emotion())
                if gui_elements_dict.get('pregnancy_label') and selected_npc_for_ui_update.status:
                    if selected_npc_for_ui_update.status.is_pregnant:
                        preg_term = getattr(config, 'PREGNANCY_TERM_GAME_DAYS', 24)
                        gui_elements_dict['pregnancy_label'].set_text(f"Incinta: {int(selected_npc_for_ui_update.status.pregnancy_progress_days)}/{preg_term}gg"); gui_elements_dict['pregnancy_label'].visible = True
                    else: gui_elements_dict['pregnancy_label'].visible = False
            else: # Resetta testi se nessun NPC è selezionato
                if gui_elements_dict.get('char_status_label'): gui_elements_dict['char_status_label'].set_text("NPC: -")
                if gui_elements_dict.get('action_label'): gui_elements_dict['action_label'].set_text(config.UI_LABEL_ACTION + "-")
                if gui_elements_dict.get('finance_label'): gui_elements_dict['finance_label'].set_text(config.UI_LABEL_FINANCE + "-")
                if gui_elements_dict.get('mood_label'): gui_elements_dict['mood_label'].set_text(config.UI_LABEL_MOOD + "-")
                if gui_elements_dict.get('pregnancy_label'): gui_elements_dict['pregnancy_label'].visible = False
        
        # Disegno
        if game_state.screen:
            current_sky_col = game_state.game_time_handler.current_sky_color if game_state.game_time_handler else (135, 206, 235)
            game_state.screen.fill(current_sky_col)

            if world_manager_instance and camera_instance:
                 world_manager_instance.draw_map_portion(game_state.screen, camera_instance.camera_rect, tile_images_dict)
                 if show_debug_grid: world_manager_instance.draw_world_grid_on_surface(game_state.screen, camera_instance.camera_rect)
            
            if game_state.bed_rect and game_state.bed_images.get("base") and camera_instance:
                game_state.screen.blit(game_state.bed_images["base"], camera_instance.apply_to_rect(game_state.bed_rect).topleft)
            if game_state.toilet_rect_instance and camera_instance:
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
            
            sel_npc_for_manual_ui = None
            if game_state.all_npc_characters_list and 0 <= current_selected_npc_idx_ui < len(game_state.all_npc_characters_list) and current_selected_npc_idx_ui != -1:
                sel_npc_for_manual_ui = game_state.all_npc_characters_list[current_selected_npc_idx_ui]

            if sel_npc_for_manual_ui : # Disegna solo se c'è un NPC selezionato
                game_utils.draw_all_manual_ui_elements(
                    screen_surface=game_state.screen, loaded_icons_map=loaded_ui_icons, 
                    speed_button_icons=ui_speed_icons, current_selected_speed_idx=game_state.current_time_speed_index,
                    time_label_gui_obj=gui_elements_dict.get('time_label'), # Usato per posizionamento relativo se necessario
                    current_day_period_name=game_state.game_time_handler.current_period_name if game_state.game_time_handler else "",
                    selected_character_to_display=sel_npc_for_manual_ui,
                    bottom_panel_gui_obj=gui_elements_dict.get('bottom_panel'),
                    needs_bars_start_x_in_panel=gui_elements_dict.get('needs_bar_area_x_in_panel', 0),
                    needs_bars_start_y_in_panel=gui_elements_dict.get('needs_bar_area_y_in_panel', 0),
                    ui_current_text_color=game_state.game_time_handler.ui_text_color if game_state.game_time_handler else config.TEXT_COLOR_DARK,
                    default_ui_font=game_state.main_font,
                    time_control_buttons_rect_list=gui_elements_dict.get('time_button_rects', []),
                    need_icon_dimensions=need_bar_icon_dimensions,
                    gui_elements_ref = gui_elements_dict # Passa il dizionario per riferimenti a pulsanti/label della UI destra
                )

            if game_state.ui_manager_instance:
                game_state.ui_manager_instance.draw_ui(game_state.screen)

            pygame.display.flip()
        else:
            logger_main.error("game_state.screen non definito. Impossibile disegnare.")
            is_game_running = False


    logger_main.info("Uscita dal loop principale del gioco.")
    if getattr(config, 'SAVE_GAME_ON_EXIT', False):
        logger_main.info("Salvataggio partita all'uscita...")
        save_game_state_json(game_state)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()