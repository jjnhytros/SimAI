# simai_save_load_system.py
import json
import os
import sys
import pygame 
import logging
import datetime
from collections import deque
from typing import TYPE_CHECKING, Optional, List, Dict, Any, Tuple # <-- AGGIUNGI/COMPLETA QUESTO

# Importa dal package 'game'
# Importa 'config' a livello di modulo così è accessibile ovunque in questo file
try:
    from game import config # Python cercherà simai/game/config.py
except ImportError as e_cfg:
    print(f"ERRORE CRITICO (simai_save_load_system.py): Impossibile importare 'game.config': {e_cfg}")
    sys.exit() # È una dipendenza fondamentale

# Ora importa le altre dipendenze, usando 'config' se necessario per fallback o valori
try:
    from game.src.entities.character import Character 
    # Le costanti specifiche verranno accedute tramite 'config.NOME_COSTANTE'
    # Non è necessario importarle individualmente qui se importi 'config'
except ImportError as e_char:
    print(f"ERRORE CRITICO (simai_save_load_system.py): Impossibile importare 'game.src.entities.character': {e_char}")
    sys.exit()
# Non importare GameState qui, verrà passata come oggetto

DEBUG_SAVE_LOAD = getattr(config, 'DEBUG_AI_ACTIVE', False) # Usa il flag di config

def ensure_save_directory_exists():
    """Assicura che la cartella dei salvataggi (definita in config.py) esista."""
    # Usa config.SAVE_GAME_DIR
    if not os.path.exists(config.SAVE_GAME_DIR):
        try:
            os.makedirs(config.SAVE_GAME_DIR)
            if DEBUG_SAVE_LOAD: print(f"SAVE_LOAD: Cartella '{config.SAVE_GAME_DIR}' creata.")
        except OSError as e:
            print(f"ERRORE SAVE_LOAD: Impossibile creare '{config.SAVE_GAME_DIR}': {e}")
            raise 
    else:
        if DEBUG_SAVE_LOAD:
            print(f"Cartella di salvataggio '{config.SAVE_GAME_DIR}' già esistente.")


def get_save_file_path(filename_to_load: str) -> str: # Assicurati che il parametro sia usato
    if not isinstance(filename_to_load, str): # Aggiungi un controllo per debug
        logging.error(f"GET_SAVE_FILE_PATH: filename_to_load NON è una stringa! Ricevuto: {type(filename_to_load)} - {filename_to_load}")
        # Fallback o solleva un errore più specifico
        filename_to_load = config.DEFAULT_SAVE_FILENAME 

    save_dir = getattr(config, 'SAVE_GAME_DIR', 'saves') # Usa getattr per un fallback
    if not os.path.exists(save_dir): # Assicurati che la directory base esista, anche se ensure_save_directory_exists lo fa per il salvataggio
        try:
            os.makedirs(save_dir)
            logging.info(f"SAVE_LOAD: Creata directory di salvataggio: {save_dir}")
        except OSError as e:
            logging.error(f"SAVE_LOAD: Impossibile creare directory di salvataggio {save_dir}: {e}")
            # Potrebbe essere meglio sollevare l'errore o avere un percorso di fallback
    return os.path.join(save_dir, filename_to_load)


def save_game_state(game_state: 'GameState', filename: str = config.DEFAULT_SAVE_FILENAME):
    """Salva lo stato corrente del gioco su un file JSON."""
    if not game_state:
        logging.error("SAVE_LOAD: Tentativo di salvare un game_state nullo.")
        return

    logging.info(f"SAVE_LOAD: Inizio salvataggio partita su '{filename}'...")
    ensure_save_directory_exists() # Assicura che la cartella 'saves' esista

    # Dati dal GameTimeManager (se esiste)
    time_data_to_save = {}
    if game_state.game_time_handler and hasattr(game_state.game_time_handler, 'to_dict'):
        time_data_to_save = game_state.game_time_handler.to_dict()

    # Dati degli NPC
    npcs_data_to_save = []
    if game_state.all_npc_characters_list:
        for npc_obj in game_state.all_npc_characters_list:
            if hasattr(npc_obj, 'to_dict'):
                npcs_data_to_save.append(npc_obj.to_dict())
            else:
                logging.warning(f"SAVE_LOAD: NPC '{npc_obj.name if hasattr(npc_obj, 'name') else 'Sconosciuto'}' non ha metodo to_dict().")

    # Dati principali del GameState
    game_data_to_save = {
        "anthalys_core_version": config.CORE_VERSION,
        "anthalys_full_version": config.FULL_VERSION_INTERNAL,
        "save_timestamp_utc": datetime.datetime.utcnow().isoformat(),

        # Attributi diretti di GameState (quelli che hai definito in GameState.__init__)
        "current_game_total_sim_hours_elapsed": game_state.current_game_total_sim_hours_elapsed,
        "is_paused_by_player": game_state.is_paused_by_player,

        # Usa il nome attributo corretto per l'indice di velocità
        "current_time_speed_index": game_state.current_time_speed_index, # <-- CORRETTO

        "previous_time_speed_index_before_sleep_ffwd": game_state.previous_time_speed_index_before_sleep_ffwd,
        "is_sleep_fast_forward_active": game_state.is_sleep_fast_forward_active,
        "last_auto_save_time_ticks": game_state.last_auto_save_time, # Salva i ticks

        # Dati oggetti del mondo (letto, bagno, ecc. - lo stato, non la definizione)
        "bed_slot_1_occupied_by_uuid": game_state.bed_slot_1_occupied_by,
        "bed_slot_2_occupied_by_uuid": game_state.bed_slot_2_occupied_by,
        # Aggiungi qui altri stati di oggetti del mondo che devono essere salvati
        # es. "food_visible": game_state.food_visible, "food_cooldown_timer": game_state.food_cooldown_timer

        # Dati aggregati
        "time_manager_data": time_data_to_save,
        "all_npcs_character_data": npcs_data_to_save,
        # Potresti voler salvare anche gli inventari domestici
        # "household_inventories_data": {hid: inv.to_dict() for hid, inv in game_state.household_inventories.items()}
    }

    save_file_path = get_save_file_path(filename)
    try:
        with open(save_file_path, 'w') as f:
            json.dump(game_data_to_save, f, indent=4)
        logging.info(f"SAVE_LOAD: Partita salvata con successo in '{save_file_path}'.")
    except IOError as e:
        logging.error(f"SAVE_LOAD: Errore di I/O durante il salvataggio in '{save_file_path}': {e}")
    except TypeError as e:
        logging.error(f"SAVE_LOAD: Errore di tipo durante la serializzazione JSON per '{save_file_path}': {e}. Controlla che tutti i dati siano serializzabili.")
    except Exception as e:
        logging.exception(f"SAVE_LOAD: Errore imprevisto durante il salvataggio in '{save_file_path}': {e}")


def load_game_state(game_state_to_populate: 'GameState',
                    sprite_sheet_manager_param: Optional['SpriteSheetManager'],
                    font_param: Optional[pygame.font.Font],
                    character_manager_param: Optional['CharacterManager'],
                    filename: str = config.DEFAULT_SAVE_FILENAME) -> bool: # 'filename' è il parametro corretto

    logging.info(f"SAVE_LOAD: Tentativo di caricamento partita da '{filename}'...")

    # >>> USA IL PARAMETRO 'filename' QUI <<<
    load_file_path = get_save_file_path(filename) # Passa il parametro 'filename'

    if not os.path.exists(load_file_path):
        logging.info(f"SAVE_LOAD: File di salvataggio '{load_file_path}' non trovato. Nessuna partita caricata.")
        return False # Indica che nessun file è stato caricato (per main.py per avviare una nuova partita)

    try:
        with open(load_file_path, 'r') as f:
            loaded_data = json.load(f)
        logging.info(f"SAVE_LOAD: Dati caricati con successo da '{load_file_path}'.")
    except FileNotFoundError: # Dovrebbe essere già gestito da os.path.exists, ma per sicurezza
        logging.info(f"SAVE_LOAD: File di salvataggio '{load_file_path}' non trovato (FileNotFoundError).")
        return False
    except json.JSONDecodeError as e:
        logging.error(f"SAVE_LOAD: Errore nel decodificare JSON da '{load_file_path}': {e}")
        return False
    except Exception as e:
        logging.error(f"SAVE_LOAD: Errore imprevisto durante il caricamento di '{load_file_path}': {e}", exc_info=True)
        return False
    
    try:
        # Popola l'istanza di GameState (game_state_to_populate)
        # (La logica di popolamento di GameState che avevamo definito, 
        #  assicurandoti che usi 'config.' per i valori di default dalle costanti
        #  e 'Character' per Character.from_dict)
        
        # Esempio per game_time_details
        time_details = loaded_data.get("game_time_details", {})
        if game_state_to_populate.game_time_handler: # Assicurati che esista
            gt_handler = game_state_to_populate.game_time_handler
            gt_handler.day = time_details.get("day", 1)
            gt_handler.month = time_details.get("month", 1)
            # ... etc ...
            gt_handler.current_sky_color_index = time_details.get("current_sky_color_index", 0)
            gt_handler.update_time(0) 
        else: # Fallback se game_time_handler non è impostato su game_state_to_populate
            game_state_to_populate.current_game_day = time_details.get("day", loaded_data.get("current_game_day", 1))
            game_state_to_populate.current_game_month = time_details.get("month", loaded_data.get("current_game_month", 1))
            game_state_to_populate.current_game_year = time_details.get("year", loaded_data.get("current_game_year", 1))
            game_state_to_populate.current_game_hour_float = time_details.get("hour", loaded_data.get("current_game_hour_float", config.INITIAL_START_HOUR))
            game_state_to_populate.current_game_total_sim_hours_elapsed = time_details.get("total_sim_hours", loaded_data.get("current_game_total_sim_hours_elapsed", 0.0))


        game_state_to_populate.time_speed_index = loaded_data.get("time_speed_index", 
                                                                  game_state_to_populate.game_time_handler.default_speed_index if game_state_to_populate.game_time_handler else 0)
        if game_state_to_populate.game_time_handler:
            game_state_to_populate.time_speed_multiplier = game_state_to_populate.game_time_handler.time_speeds[game_state_to_populate.time_speed_index]['multiplier']
        
        game_state_to_populate.is_paused_by_player = loaded_data.get("is_paused_by_player", False)
        game_state_to_populate.is_sleep_fast_forward_active = loaded_data.get("is_sleep_fast_forward_active", False)
        game_state_to_populate.previous_time_speed_index_before_sleep_ffwd = loaded_data.get( # Corretto nome variabile
            "previous_time_speed_index_before_sleep_ffwd", 
            game_state_to_populate.time_speed_index
        )
        game_state_to_populate.last_auto_save_time = loaded_data.get("last_auto_save_time", pygame.time.get_ticks())
        game_state_to_populate.food_visible = loaded_data.get("food_visible", True)
        game_state_to_populate.food_cooldown_timer = loaded_data.get("food_cooldown_timer", 0.0)

        bed_rect_data = loaded_data.get("bed_rect_data")
        if bed_rect_data:
            game_state_to_populate.bed_rect = pygame.Rect(bed_rect_data)
            # Ricalcola posizioni slot come facevi in main.py o in GameState.populate_from_dict
            if hasattr(config, 'BED_SLOT_1_INTERACTION_OFFSET'):
                s1io,s2io = config.BED_SLOT_1_INTERACTION_OFFSET, config.BED_SLOT_2_INTERACTION_OFFSET
                s1so,s2so = config.BED_SLOT_1_SLEEP_POS_OFFSET, config.BED_SLOT_2_SLEEP_POS_OFFSET
                game_state_to_populate.bed_slot_1_interaction_pos_world = (game_state_to_populate.bed_rect.left + s1io[0], game_state_to_populate.bed_rect.top + s1io[1])
                game_state_to_populate.bed_slot_2_interaction_pos_world = (game_state_to_populate.bed_rect.left + s2io[0], game_state_to_populate.bed_rect.top + s2io[1])
                game_state_to_populate.bed_slot_1_sleep_pos_world = (game_state_to_populate.bed_rect.left + s1so[0], game_state_to_populate.bed_rect.top + s1so[1])
                game_state_to_populate.bed_slot_2_sleep_pos_world = (game_state_to_populate.bed_rect.left + s2so[0], game_state_to_populate.bed_rect.top + s2so[1])
        
        game_state_to_populate.bed_slot_1_occupied_by = loaded_data.get("bed_slot_1_occupied_by")
        game_state_to_populate.bed_slot_2_occupied_by = loaded_data.get("bed_slot_2_occupied_by")

        toilet_rect_data = loaded_data.get("toilet_rect_data")
        if toilet_rect_data:
            game_state_to_populate.toilet_rect_instance = pygame.Rect(toilet_rect_data)
        elif hasattr(config, 'TOILET_RECT_PARAMS'):
             params = config.TOILET_RECT_PARAMS
             game_state_to_populate.toilet_rect_instance = pygame.Rect(params["x"], params["y"], params["w"], params["h"])


        # Ricrea NPC
        # Assicurati che sprite_sheet_manager e font siano passati e validi.
        # E che game_state_to_populate (che è l'istanza di GameState) sia passato a Character.from_dict.
        loaded_npcs_data = loaded_data.get("npcs", []) # Chiave corretta da save_game_state
        if hasattr(game_state_to_populate, 'all_npc_characters_list'):
            game_state_to_populate.all_npc_characters_list = [] 
            if sprite_sheet_manager and font:
                for i, npc_data in enumerate(loaded_npcs_data):
                    try:
                        character = Character.from_dict(npc_data, sprite_sheet_manager, font, game_state_to_populate)
                        game_state_to_populate.all_npc_characters_list.append(character)
                    except Exception as e:
                        if DEBUG_SAVE_LOAD: print(f"ERRORE SAVE_LOAD: creazione NPC #{i} ('{npc_data.get('name')}'): {e}")
            elif DEBUG_SAVE_LOAD:
                print("WARN SAVE_LOAD: sprite_sheet_manager o font mancanti per caricare NPC.")
        
        if DEBUG_SAVE_LOAD:
            npc_count = len(game_state_to_populate.all_npc_characters_list) if hasattr(game_state_to_populate, 'all_npc_characters_list') else "N/A (lista NPC non in game_state)"
            print(f"SAVE_LOAD: Partita caricata. NPC: {npc_count}")
        
        return game_state_to_populate

    except KeyError as e:
        print(f"ERRORE SAVE_LOAD: Chiave mancante nel file di salvataggio: '{e}'. "
              "Il file potrebbe essere corrotto, di una vecchia versione, o un errore nel metodo to_dict/from_dict.")
        return None
    except Exception as e:
        print(f"ERRORE SAVE_LOAD: Errore imprevisto durante il caricamento dei dati: {e}")
        # import traceback
        # traceback.print_exc()
        return None
