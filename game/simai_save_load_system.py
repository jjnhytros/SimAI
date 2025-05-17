# simai_save_load_system.py
import json
import os
import sys
import pygame 
from collections import deque

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
            print(f"Cartella di salvataggio '{config.SAVE_GAME_SAVE_DIR}' già esistente.")


def get_save_file_path(filename=None): # filename può essere None per usare il default
    """Restituisce il percorso completo del file di salvataggio."""
    # Usa config.DEFAULT_SAVE_FILENAME se filename non è fornito
    actual_filename = filename if filename is not None else config.DEFAULT_SAVE_FILENAME
    return os.path.join(config.SAVE_GAME_DIR, actual_filename)


def save_game_state(game_state, filename=None): # filename può essere None
    """Salva lo stato completo del gioco in un file JSON."""
    ensure_save_directory_exists() 
    actual_filename = filename if filename is not None else config.DEFAULT_SAVE_FILENAME
    file_path = get_save_file_path(actual_filename) # Usa actual_filename
    
    if DEBUG_SAVE_LOAD: # Usa la variabile definita a livello di modulo
        print(f"SAVE_LOAD: Tentativo di salvataggio partita in {file_path}...")

    # ... (il resto della funzione save_game_state rimane come prima, 
    #      ma assicurati che usi 'config.NOME_COSTANTE' quando accedi alle costanti,
    #      e 'Character' come nome importato) ...
    # Esempio:
    save_data = {
        "game_time_details": {
            "day": game_state.game_time_handler.day,
            "month": game_state.game_time_handler.month,
            # ... etc.
            "current_sky_color_index": game_state.game_time_handler.current_sky_color_index,
        },
        "time_speed_index": game_state.time_speed_index,
        "is_paused_by_player": game_state.is_paused_by_player,
        "is_sleep_fast_forward_active": game_state.is_sleep_fast_forward_active,
        "previous_time_speed_index_before_sleep_ff": game_state.previous_time_speed_index_before_sleep_ff,
        "npcs": [npc.to_dict() for npc in game_state.all_npc_characters_list], # Assumendo che la lista sia in game_state
        "last_auto_save_time": game_state.last_auto_save_time,
        # Aggiungi qui il salvataggio degli attributi diretti di GameState che erano nel tuo JSON originale
        "current_game_hour_float": game_state.current_game_hour_float, # Se non coperto da game_time_details
        "current_game_day": game_state.current_game_day,
        "current_game_month": game_state.current_game_month,
        "current_game_year": game_state.current_game_year,
        "current_game_total_sim_hours_elapsed": game_state.current_game_total_sim_hours_elapsed,
        "food_visible": game_state.food_visible,
        "food_cooldown_timer": game_state.food_cooldown_timer,
        "bed_rect_data": [game_state.bed_rect.x, game_state.bed_rect.y, game_state.bed_rect.width, game_state.bed_rect.height] if game_state.bed_rect else None,
        "bed_slot_1_occupied_by": game_state.bed_slot_1_occupied_by,
        "bed_slot_2_occupied_by": game_state.bed_slot_2_occupied_by,
        # Non salvare bed_slot_X_interaction_pos_world e bed_slot_X_sleep_pos_world perché sono derivati
        "toilet_rect_data": [game_state.toilet_rect_instance.x, game_state.toilet_rect_instance.y, game_state.toilet_rect_instance.width, game_state.toilet_rect_instance.height] if game_state.toilet_rect_instance else None,
    }


    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=4, ensure_ascii=False)
        if DEBUG_SAVE_LOAD:
            print(f"SAVE_LOAD: Partita salvata con successo in {file_path}")
        return True
    # ... (blocchi except come prima) ...
    except IOError as e:
        print(f"ERRORE SAVE_LOAD: Errore di I/O durante il salvataggio: {e}")
        return False
    except TypeError as e:
        print(f"ERRORE SAVE_LOAD: Errore di tipo durante la serializzazione JSON: {e}. ")
        return False
    except Exception as e:
        print(f"ERRORE SAVE_LOAD: Errore imprevisto durante il salvataggio: {e}")
        return False


def load_game_state(game_state_to_populate, filename=None, sprite_sheet_manager=None, font=None):
    """
    Carica lo stato del gioco da un file JSON e popola l'istanza game_state_to_populate.
    """
    actual_filename = filename if filename is not None else config.DEFAULT_SAVE_FILENAME
    file_path = get_save_file_path(actual_filename) # Usa actual_filename

    if not os.path.exists(file_path):
        if DEBUG_SAVE_LOAD:
            print(f"SAVE_LOAD: File '{file_path}' non trovato. Impossibile caricare.")
        return None 

    if DEBUG_SAVE_LOAD:
        print(f"SAVE_LOAD: Tentativo di caricamento partita da {file_path}...")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
    # ... (blocchi except come prima) ...
    except IOError as e:
        print(f"ERRORE SAVE_LOAD: Errore di I/O durante il caricamento: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"ERRORE SAVE_LOAD: Errore durante il parsing del JSON: {e}. Il file potrebbe essere corrotto.")
        return None
    
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
