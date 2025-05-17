# simai_save_load_system.py
import json
import os
import pygame # Per Rect, se necessario
from collections import deque # Per deserializzare self.path in Character

# Importa le classi necessarie (aggiusta i percorsi se la tua struttura è diversa)
from src.entities.character import Character, NPC_PREGNANCY_DURATION_DAYS, CHARACTER_SPEED # Assumendo che le costanti siano qui o in config
import config

# Se GameState è una classe definita altrove (es. in main.py o un game_state.py),
# dovrai assicurarti che sia importabile o che tu possa accedere ai suoi attributi.
# Per ora, assumiamo che 'game_state' sia l'oggetto passato alle funzioni.


SAVE_GAME_DIR = "saves"  # Cartella per i file di salvataggio
DEFAULT_SAVE_FILENAME = "anthalys_save.json"

def ensure_save_directory_exists():
    """Assicura che la cartella dei salvataggi (definita in config.py) esista."""
    if not os.path.exists(config.SAVE_GAME_SAVE_DIR):
        try:
            os.makedirs(config.SAVE_GAME_SAVE_DIR)
            print(f"Cartella di salvataggio '{config.SAVE_GAME_SAVE_DIR}' creata.")
        except OSError as e:
            print(f"ERRORE: Impossibile creare la cartella di salvataggio '{config.SAVE_GAME_SAVE_DIR}': {e}")
            # Potresti voler sollevare l'eccezione o gestire diversamente
            raise  # Rilancia l'eccezione per ora
    else:
        print(f"Cartella di salvataggio '{config.SAVE_GAME_SAVE_DIR}' già esistente.")


def get_save_file_path(filename=DEFAULT_SAVE_FILENAME):
    """Restituisce il percorso completo del file di salvataggio."""
    return os.path.join(config.SAVE_GAME_SAVE_DIR, filename)


def save_game_state(game_state, filename=DEFAULT_SAVE_FILENAME):
    """Salva lo stato completo del gioco in un file JSON."""
    ensure_save_directory_exists() # Assicura che la dir esista prima di salvare
    file_path = get_save_file_path(filename)
    
    if hasattr(game_state, 'DEBUG_AI_ACTIVE') and game_state.DEBUG_AI_ACTIVE:
        print(f"SAVE_LOAD: Tentativo di salvataggio partita in {file_path}...")

    save_data = {
        # Stato di GameTimeManager (o l'oggetto che gestisce il tempo in game_state)
        "game_time_details": {
            "day": game_state.game_time_handler.day,
            "month": game_state.game_time_handler.month,
            "year": game_state.game_time_handler.year,
            "hour": game_state.game_time_handler.hour,
            "minute": game_state.game_time_handler.minute,
            "total_game_seconds_elapsed": game_state.game_time_handler.total_game_seconds_elapsed,
            "current_period_name": game_state.game_time_handler.current_period_name,
        },
        "time_speed_index": game_state.time_speed_index,
        # "time_speed_multiplier" è derivato, non strettamente necessario salvarlo
        "current_sky_color_index": game_state.game_time_handler.current_sky_color_index, # Preso da game_time_handler
        "is_paused_by_player": game_state.is_paused_by_player,
        "is_sleep_fast_forward_active": game_state.is_sleep_fast_forward_active,
        "previous_time_speed_index_before_sleep_ff": game_state.previous_time_speed_index_before_sleep_ff,
        "npcs": [npc.to_dict() for npc in game_state.npcs], # Usa il metodo to_dict di Character
        # TODO: Aggiungere la serializzazione per gli oggetti del mondo (game_state.all_objects)
        # "world_objects": [obj.to_dict() for obj in game_state.all_objects if hasattr(obj, 'to_dict')],
        "last_auto_save_time": game_state.last_auto_save_time, # Salva il timestamp dell'ultimo auto-salvataggio
        # Aggiungere qui altri stati globali se necessario
    }

    try:
        with open(file_path, 'w', encoding='utf-8') as f: # Specificare encoding='utf-8' è una buona pratica
            json.dump(save_data, f, indent=4, ensure_ascii=False)
        if hasattr(game_state, 'DEBUG_AI_ACTIVE') and game_state.DEBUG_AI_ACTIVE:
            print(f"SAVE_LOAD: Partita salvata con successo in {file_path}")
        return True
    except IOError as e:
        print(f"ERRORE SAVE_LOAD: Errore di I/O durante il salvataggio: {e}")
        return False
    except TypeError as e:
        print(f"ERRORE SAVE_LOAD: Errore di tipo durante la serializzazione JSON: {e}. "
              "Verifica i metodi to_dict() e che restituiscano tipi serializzabili.")
        return False
    except Exception as e:
        print(f"ERRORE SAVE_LOAD: Errore imprevisto durante il salvataggio: {e}")
        # import traceback # Per debug più dettagliato
        # traceback.print_exc()
        return False


def load_game_state(game_state_to_populate, filename=DEFAULT_SAVE_FILENAME, sprite_sheet_manager=None, font=None):
    """
    Carica lo stato del gioco da un file JSON e popola l'istanza game_state_to_populate.
    Richiede sprite_sheet_manager e font per ricreare correttamente gli NPC.
    """
    file_path = get_save_file_path(filename)
    if not os.path.exists(file_path):
        if hasattr(game_state_to_populate, 'DEBUG_AI_ACTIVE') and game_state_to_populate.DEBUG_AI_ACTIVE:
            print(f"SAVE_LOAD: File di salvataggio '{file_path}' non trovato. Impossibile caricare.")
        return None 

    if hasattr(game_state_to_populate, 'DEBUG_AI_ACTIVE') and game_state_to_populate.DEBUG_AI_ACTIVE:
        print(f"SAVE_LOAD: Tentativo di caricamento partita da {file_path}...")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
    except IOError as e:
        print(f"ERRORE SAVE_LOAD: Errore di I/O durante il caricamento: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"ERRORE SAVE_LOAD: Errore durante il parsing del JSON: {e}. Il file potrebbe essere corrotto.")
        return None

    try:
        # Popola l'istanza di GameState (game_state_to_populate)
        
        # Ripristina GameTimeHandler
        time_details = loaded_data.get("game_time_details", {})
        gt_handler = game_state_to_populate.game_time_handler
        gt_handler.day = time_details.get("day", 1)
        gt_handler.month = time_details.get("month", 1)
        gt_handler.year = time_details.get("year", 1)
        gt_handler.hour = time_details.get("hour", 7) 
        gt_handler.minute = time_details.get("minute", 0)
        gt_handler.total_game_seconds_elapsed = time_details.get("total_game_seconds_elapsed", 0.0)
        # current_period_name verrà ricalcolato da update_time
        # È cruciale chiamare update_time per ricalcolare current_period, sky_color etc.
        # Passiamo 0 come dt_simulated per non far avanzare il tempo, ma solo per aggiornare lo stato interno.
        gt_handler.update_time(0) 
        
        # Ripristina l'indice e il colore del cielo esplicitamente se necessario
        # game_state_to_populate.current_sky_color_index = loaded_data.get("current_sky_color_index", 0) # L'indice è ora in gt_handler
        gt_handler.current_sky_color_index = loaded_data.get("current_sky_color_index", gt_handler.current_sky_color_index)
        gt_handler.current_sky_color = gt_handler.sky_colors[gt_handler.current_sky_color_index] # Applica il colore corretto

        # Ripristina velocità di gioco e stato di pausa
        game_state_to_populate.time_speed_index = loaded_data.get("time_speed_index", gt_handler.default_speed_index)
        game_state_to_populate.time_speed_multiplier = gt_handler.time_speeds[game_state_to_populate.time_speed_index]['multiplier']
        game_state_to_populate.is_paused_by_player = loaded_data.get("is_paused_by_player", False)

        # Ripristina stato accelerazione sonno
        game_state_to_populate.is_sleep_fast_forward_active = loaded_data.get("is_sleep_fast_forward_active", False)
        game_state_to_populate.previous_time_speed_index_before_sleep_ff = loaded_data.get(
            "previous_time_speed_index_before_sleep_ff", 
            game_state_to_populate.time_speed_index # Default alla velocità corrente se non salvato
        )

        # Ripristina timestamp auto-salvataggio
        game_state_to_populate.last_auto_save_time = loaded_data.get("last_auto_save_time", pygame.time.get_ticks())


        # Ricrea NPC
        loaded_npcs_data = loaded_data.get("npcs", [])
        game_state_to_populate.npcs = []  # Svuota la lista NPC corrente prima di popolarla
        
        if not sprite_sheet_manager:
            print("ERRORE SAVE_LOAD: sprite_sheet_manager non fornito a load_game_state. Impossibile caricare gli sprite degli NPC.")
        if not font:
             print("ERRORE SAVE_LOAD: font non fornito a load_game_state. Testo degli NPC potrebbe non essere corretto.")

        for i, npc_data in enumerate(loaded_npcs_data):
            try:
                # Passa game_state_to_populate (che è l'istanza di GameState)
                # a Character.from_dict per accedere a game_time_handler e altre dipendenze.
                character = Character.from_dict(npc_data, sprite_sheet_manager, font, game_state_to_populate)
                game_state_to_populate.npcs.append(character)
            except Exception as e:
                print(f"ERRORE SAVE_LOAD: durante la creazione dell'NPC #{i} ('{npc_data.get('name', 'ID Sconosciuto')}') dai dati. Errore: {e}")
                # import traceback # Per debug
                # traceback.print_exc()
                # Potresti decidere di continuare a caricare gli altri NPC o interrompere.
                # Per ora, continuiamo.

        # TODO: Deserializzare gli oggetti del mondo (game_state.all_objects)
        # loaded_world_objects_data = loaded_data.get("world_objects", [])
        # game_state_to_populate.all_objects = [] # Svuota e ripopola
        # for obj_data in loaded_world_objects_data:
        #     # Qui avrai bisogno di un modo per determinare il tipo di oggetto e chiamare il suo from_dict
        #     # Esempio:
        #     # obj_type = obj_data.get("type")
        #     # if obj_type == "Bed":
        #     #    new_obj = Bed.from_dict(obj_data, sprite_sheet_manager)
        #     #    game_state_to_populate.all_objects.append(new_obj)
        #     pass
        
        if hasattr(game_state_to_populate, 'DEBUG_AI_ACTIVE') and game_state_to_populate.DEBUG_AI_ACTIVE:
            print(f"SAVE_LOAD: Partita caricata con successo da {file_path}. NPC caricati: {len(game_state_to_populate.npcs)}")
        
        return game_state_to_populate # Restituisce l'istanza di game_state popolata (anche se è la stessa passata)

    except KeyError as e:
        print(f"ERRORE SAVE_LOAD: Chiave mancante nel file di salvataggio: '{e}'. "
              "Il file potrebbe essere corrotto, di una vecchia versione, o un errore nel metodo to_dict/from_dict.")
        return None
    except Exception as e:
        print(f"ERRORE SAVE_LOAD: Errore imprevisto durante il caricamento dei dati: {e}")
        # import traceback
        # traceback.print_exc()
        return None
