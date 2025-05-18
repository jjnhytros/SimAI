# game/src/managers/game_loop_updater.py
import pygame # Potrebbe non essere necessario direttamente qui, ma le funzioni chiamate potrebbero usarlo
import logging

# Importa dal package 'game'
from game import config
from game.src.modules.game_state_module import GameState
from game.src.ai.npc_behavior import run_npc_ai_logic # Importa la logica AI
# from game.src.utils import game as game_utils # Se chiami funzioni da lì

logger = logging.getLogger(__name__)

def update_game_logic_for_tick(
    game_state: GameState,
    time_delta_real_seconds: float,
    # Passa altri manager se sono necessari per gli aggiornamenti e non sono in game_state
    # world_manager: Optional['WorldManager'] = None, # Esempio
    # camera: Optional['Camera'] = None, # Esempio
):
    """
    Esegue tutta la logica di aggiornamento per un singolo tick di gioco.
    Modifica game_state.
    """

    # --- 1. Calcolo del tempo di gioco avanzato ---
    game_hours_advanced_this_frame = 0.0
    effective_time_speed_index = game_state.current_time_speed_index
    
    # Logica per l'accelerazione del sonno
    # (Questa logica potrebbe essere più complessa e meriterebbe una sua funzione/modulo)
    all_resting = False
    if game_state.all_npc_characters_list: # Solo se ci sono NPC
        all_resting = all(npc.current_action == "resting_on_bed" for npc in game_state.all_npc_characters_list)
        
    if all_resting and not game_state.is_sleep_fast_forward_active and game_state.current_time_speed_index != 0:
        game_state.previous_time_speed_index_before_sleep_ffwd = game_state.current_time_speed_index
        effective_time_speed_index = getattr(config, 'TIME_SPEED_SLEEP_ACCELERATED_INDEX', 5) # Usa la velocità di config
        game_state.is_sleep_fast_forward_active = True
        logging.info(f"Tutti gli NPC dormono. Accelerazione sonno ATTIVATA alla velocità: {effective_time_speed_index}")
    elif not all_resting and game_state.is_sleep_fast_forward_active:
        effective_time_speed_index = game_state.previous_time_speed_index_before_sleep_ffwd
        game_state.is_sleep_fast_forward_active = False
        logging.info(f"Un NPC si è svegliato. Accelerazione sonno DISATTIVATA. Ripristino velocità a: {effective_time_speed_index}")
    
    if game_state.is_paused_by_player: # La pausa manuale ha la priorità
        effective_time_speed_index = 0
    
    # Aggiorna l'indice di velocità effettivo in game_state se è diverso da quello base
    # (potrebbe non essere necessario se la logica AI e update NPC usano effective_time_speed_index)
    # game_state.current_time_speed_index = effective_time_speed_index # Attenzione: questo potrebbe sovrascrivere la selezione utente

    if effective_time_speed_index > 0: # Se non è in pausa (indice 0)
        seconds_per_game_hour = config.TIME_SPEED_SETTINGS.get(effective_time_speed_index, float('inf'))
        if seconds_per_game_hour > 0 and seconds_per_game_hour != float('inf'):
            game_hours_advanced_this_frame = time_delta_real_seconds / seconds_per_game_hour
    
    game_state.current_game_total_sim_hours_elapsed += game_hours_advanced_this_frame

    # --- 2. Aggiornamento Time Manager e stato temporale in GameState ---
    if game_state.game_time_handler:
        # update_time fa avanzare il tempo di gioco (ore, giorni, ecc.)
        # e internamente chiama update_time_display_elements, 
        # che a sua volta chiama _update_sky_and_ui_text_color.
        game_state.game_time_handler.update_time(game_hours_advanced_this_frame * 3600) 
        
        # Aggiorna gli attributi di GameState dal TimeManager (se necessario tenerli sincronizzati)
        game_state.current_game_hour_float = game_state.game_time_handler.get_hour_float()
        game_state.current_game_day = game_state.game_time_handler.day
        game_state.current_game_month = game_state.game_time_handler.month
        game_state.current_game_year = game_state.game_time_handler.year
        
        # game_state.game_time_handler.update_sky_color(time_delta_real_seconds) # Passa dt REALE per transizioni fluide
    else:
        logging.warning("GameTimeManager non trovato in game_state durante l'aggiornamento.")

    # --- 3. Aggiornamento NPC (Logica e IA) ---
    # La logica NPC viene eseguita solo se il gioco non è in pausa (dall'utente o velocità 0)
    # e se ci sono NPC. effective_time_speed_index tiene conto della pausa.
    if effective_time_speed_index > 0 and game_state.all_npc_characters_list:
        current_period = game_state.game_time_handler.current_period_name if game_state.game_time_handler else "Mattina"
        for npc_char in game_state.all_npc_characters_list:
            is_resting_for_update = (npc_char.current_action == "resting_on_bed")
            npc_char.update(
                dt_real=time_delta_real_seconds,
                world_width_pixels=config.WORLD_TILE_WIDTH * config.TILE_SIZE,  # Modificato da screen_width
                world_height_pixels=config.WORLD_TILE_HEIGHT * config.TILE_SIZE, # Modificato da screen_height
                game_hours_advanced=game_hours_advanced_this_frame,
                current_time_speed_index=effective_time_speed_index,
                # is_char_externally_resting=is_resting_for_need_update, # Rimosso per ora
                tile_size=config.TILE_SIZE,
                period_name=current_period
            )
            # Passa la griglia di pathfinding corretta (da game_state)
            if game_state.a_star_grid_instance:
                run_npc_ai_logic(
                    npc_char,
                    game_state.all_npc_characters_list,
                    game_hours_advanced_this_frame,
                    game_state.a_star_grid_instance,
                    game_state
                )
            else:
                logging.warning(f"Griglia A* non disponibile per NPC {npc_char.name}, AI non eseguita.")
    
    # --- 4. Aggiornamento UI Manager (Pygame GUI) ---
    if game_state.ui_manager_instance:
        game_state.ui_manager_instance.update(time_delta_real_seconds)

    # --- 5. Aggiornamento Altri Sistemi di Gioco ---
    # Esempio: cooldown cibo (se la logica del cibo viene reintrodotta)
    # if not game_state.food_visible:
    #    game_state.food_cooldown_timer -= time_delta_real_seconds
    #    if game_state.food_cooldown_timer <= 0:
    #        game_state.food_visible = True
    #        logging.debug("Cibo riapparso.")

    # Auto-salvataggio
    if config.AUTO_SAVE_INTERVAL_SECONDS > 0:
        current_ticks = pygame.time.get_ticks()
        if current_ticks - game_state.last_auto_save_time > config.AUTO_SAVE_INTERVAL_SECONDS * 1000:
            logging.info("Autosalvataggio in corso...")
            # save_game_state_json(game_state) # Assicurati che sia importata e usata correttamente
            game_state.last_auto_save_time = current_ticks