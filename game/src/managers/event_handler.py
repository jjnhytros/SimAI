# game/src/managers/event_handler.py
import pygame
import sys
import logging # Importa logging

# Importa dal package 'game'
from game import config
from game.src.modules.game_state_module import GameState
# Potrebbe essere necessario importare Character se la randomizzazione dei bisogni è gestita qui
# from game.src.entities.character import Character

logger = logging.getLogger(__name__)

def handle_all_events(event: pygame.event.Event, 
                      game_state: GameState, 
                      # Passa anche altri elementi se necessario per le azioni dei tasti
                      current_selected_npc_idx_param: int, 
                      show_debug_grid_param: bool,
                      show_npc_debug_info_param: bool
                      ) -> tuple[int, bool, bool, bool]: # Restituisce i valori aggiornati
    """
    Gestisce tutti gli eventi di Pygame (input da tastiera, mouse, chiusura finestra).
    Modifica game_state e restituisce stati che potrebbero essere locali a main.py.
    """
    new_selected_npc_idx = current_selected_npc_idx_param
    new_show_debug_grid = show_debug_grid_param
    new_show_npc_debug_info = show_npc_debug_info_param
    should_game_run = True # Flag per controllare se il gioco deve continuare

    if event.type == pygame.QUIT:
        should_game_run = False

    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            should_game_run = False
        elif event.key == pygame.K_p: # Pausa / Riprendi
            game_state.is_paused_by_player = not game_state.is_paused_by_player
            if game_state.is_paused_by_player:
                # Se mettiamo in pausa, potremmo voler impostare la velocità a 0
                # e salvare la velocità precedente se non è già gestito da time_speed_index = 0
                # game_state.current_time_speed_index = 0 # O gestito tramite il sistema di velocità
                logging.info("Gioco in PAUSA (manuale).")
            else:
                # Al resume, potremmo ripristinare la velocità precedente o quella normale
                # game_state.current_time_speed_index = game_state.game_time_handler.default_speed_index
                logging.info("Gioco RIPRESO (manuale).")
            # Nota: la logica di TIME_SPEED_SETTINGS con indice 0 per la pausa è più robusta.
            # Qui gestiamo solo un flag aggiuntivo per la pausa utente.

        elif event.key == pygame.K_0: game_state.current_time_speed_index = 0
        elif event.key == pygame.K_1: game_state.current_time_speed_index = 1
        elif event.key == pygame.K_2: game_state.current_time_speed_index = 2
        elif event.key == pygame.K_3: game_state.current_time_speed_index = 3
        elif event.key == pygame.K_4: game_state.current_time_speed_index = 4
        elif event.key == pygame.K_5: game_state.current_time_speed_index = 5
        
        if event.key in [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]:
            game_state.is_paused_by_player = (game_state.current_time_speed_index == 0) # Pausa se velocità è 0
            if game_state.game_time_handler and game_state.current_time_speed_index in game_state.game_time_handler.time_speeds:
                 speed_name = game_state.game_time_handler.time_speeds[game_state.current_time_speed_index].get("name", "Sconosciuta")
                 logging.info(f"Velocità di gioco cambiata a: {game_state.current_time_speed_index} ({speed_name})")
            game_state.is_sleep_fast_forward_active = False # Interrompe l'accelerazione del sonno se l'utente cambia velocità

        elif event.key == pygame.K_SPACE:
            if game_state.all_npc_characters_list:
                new_selected_npc_idx = (current_selected_npc_idx_param + 1) % len(game_state.all_npc_characters_list)
                selected_npc_name = game_state.all_npc_characters_list[new_selected_npc_idx].name
                logging.debug(f"Cambiato NPC selezionato per UI a: {selected_npc_name}")
        
        elif event.key == pygame.K_g:
            new_show_debug_grid = not show_debug_grid_param
            logging.debug(f"Toggle griglia di debug: {'ON' if new_show_debug_grid else 'OFF'}")

        elif event.key == pygame.K_i:
            new_show_npc_debug_info = not show_npc_debug_info_param
            logging.debug(f"Toggle info debug NPC: {'ON' if new_show_npc_debug_info else 'OFF'}")

        elif event.key == pygame.K_r:
            if game_state.all_npc_characters_list and 0 <= new_selected_npc_idx < len(game_state.all_npc_characters_list):
                selected_npc = game_state.all_npc_characters_list[new_selected_npc_idx]
                selected_npc.randomize_needs()
                logging.info(f"Bisogni randomizzati per {selected_npc.name}")

        # Aggiungi qui la gestione per F5 (Salva) e F9 (Carica) se vuoi
        # elif event.key == pygame.K_F5:
        #     save_game_state_json(game_state) # Assumendo che save_game_state_json sia accessibile
        # elif event.key == pygame.K_F9:
        #     loaded_gs = load_game_state_json(game_state, sprite_sheet_manager=game_state.sprite_sheet_manager, font=game_state.main_font)
        #     if loaded_gs:
        #         game_state = loaded_gs # Potrebbe essere necessario aggiornare più variabili in main

    # Passa l'evento al gestore UI di Pygame GUI (se esiste)
    if game_state.ui_manager_instance:
        game_state.ui_manager_instance.process_events(event)
        
    return new_selected_npc_idx, new_show_debug_grid, new_show_npc_debug_info, should_game_run