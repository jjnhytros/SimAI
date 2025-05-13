# simai/game/simai_save_load_system.py
import sqlite3
import json # json potrebbe non servire se salviamo attributi primitivi
import os
import datetime
# Importa Character per usare Character.from_data
# Questo crea una dipendenza, ma è necessaria per ricreare gli oggetti
try:
    from game.src.entities.character import Character
    from game import config # Per i valori di default/configurazione al caricamento
except ImportError:
    print("ERRORE CRITICO (SaveLoadSystem): Impossibile importare Character o Config.")
    # Definisci placeholder o fai sys.exit()
    Character = None 
    config = None 

DB_FILENAME = "simai.db" # Nome del file database

def connect_db(db_name=DB_FILENAME):
    """Connette al database SQLite e restituisce l'oggetto connessione."""
    # Il database sarà creato nella stessa cartella di main.py se non esiste
    # Per una build, potresti volerlo in una cartella utente apposita
    conn = sqlite3.connect(db_name)
    conn.execute("PRAGMA foreign_keys = ON;") # Abilita supporto chiavi esterne
    return conn

def create_tables_if_not_exist(conn):
    """Crea le tabelle nel database se non esistono già."""
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS GameSaves (
        save_id INTEGER PRIMARY KEY AUTOINCREMENT,
        save_name TEXT NOT NULL UNIQUE,
        timestamp TEXT NOT NULL,
        current_game_year INTEGER,
        current_game_month INTEGER,
        current_game_day INTEGER,
        current_game_hour_float REAL,
        current_game_total_sim_hours_elapsed REAL,
        current_time_speed_index INTEGER,
        food_visible BOOLEAN,
        food_cooldown_timer REAL,
        ui_selected_char_uuid TEXT 
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS SavedCharacters (
        character_uuid TEXT NOT NULL,
        save_id INTEGER NOT NULL,
        name TEXT,
        gender TEXT,
        x_pos REAL,
        y_pos REAL,
        current_action TEXT,
        target_partner_uuid TEXT,
        age_in_total_game_days REAL,
        is_pregnant BOOLEAN,
        pregnancy_progress_days REAL,
        time_in_current_action REAL,
        PRIMARY KEY (character_uuid, save_id),
        FOREIGN KEY (save_id) REFERENCES GameSaves (save_id) ON DELETE CASCADE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS SavedCharacterNeeds (
        need_save_id INTEGER PRIMARY KEY AUTOINCREMENT,
        character_uuid TEXT NOT NULL,
        save_id INTEGER NOT NULL,
        need_name TEXT NOT NULL, 
        current_value REAL NOT NULL,
        FOREIGN KEY (character_uuid, save_id) REFERENCES SavedCharacters (character_uuid, save_id) ON DELETE CASCADE,
        UNIQUE (character_uuid, save_id, need_name)
    )
    """)
    
    conn.commit()
    # print("DB INFO: Tabelle controllate/create.")


def save_current_game_state(conn, save_name_str, global_state_dict, characters_list):
    """Salva lo stato corrente del gioco nel database."""
    if not conn: return False
    cursor = conn.cursor()
    current_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with conn: # Gestisce commit/rollback automaticamente
            # Inserisci o aggiorna lo slot di salvataggio
            cursor.execute("""
                INSERT INTO GameSaves (save_name, timestamp, current_game_year, current_game_month, current_game_day,
                                         current_game_hour_float, current_game_total_sim_hours_elapsed,
                                         current_time_speed_index, food_visible, food_cooldown_timer,
                                         ui_selected_char_uuid)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(save_name) DO UPDATE SET
                    timestamp=excluded.timestamp, current_game_year=excluded.current_game_year,
                    current_game_month=excluded.current_game_month, current_game_day=excluded.current_game_day,
                    current_game_hour_float=excluded.current_game_hour_float,
                    current_game_total_sim_hours_elapsed=excluded.current_game_total_sim_hours_elapsed,
                    current_time_speed_index=excluded.current_time_speed_index,
                    food_visible=excluded.food_visible, food_cooldown_timer=excluded.food_cooldown_timer,
                    ui_selected_char_uuid=excluded.ui_selected_char_uuid
            """, (save_name_str, current_timestamp, 
                  global_state_dict['year'], global_state_dict['month'], global_state_dict['day'],
                  global_state_dict['hour_float'], global_state_dict['total_sim_hours'],
                  global_state_dict['speed_index'], global_state_dict['food_visible'],
                  global_state_dict['food_cooldown'], global_state_dict['selected_char_uuid']))
            
            # Ottieni il save_id per questo salvataggio
            cursor.execute("SELECT save_id FROM GameSaves WHERE save_name = ?", (save_name_str,))
            result = cursor.fetchone()
            if not result: print("ERRORE DB: Impossibile ottenere save_id."); return False
            current_save_id = result[0]

            # Cancella i vecchi dati dei personaggi e bisogni per questo save_id per evitare duplicati se sovrascriviamo
            cursor.execute("DELETE FROM SavedCharacterNeeds WHERE save_id = ?", (current_save_id,))
            cursor.execute("DELETE FROM SavedCharacters WHERE save_id = ?", (current_save_id,))

            # Salva ogni personaggio
            for char_obj in characters_list:
                char_data_to_save = char_obj.to_dict()
                
                cursor.execute("""
                    INSERT INTO SavedCharacters 
                        (character_uuid, save_id, name, gender, x_pos, y_pos, current_action, 
                         target_partner_uuid, age_in_total_game_days, is_pregnant, 
                         pregnancy_progress_days, time_in_current_action)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (char_obj.uuid, current_save_id, char_obj.name, char_obj.gender, 
                      char_obj.x, char_obj.y, char_obj.current_action,
                      char_data_to_save.get('target_partner_uuid'), # Da to_dict()
                      char_obj.age_in_total_game_days, char_obj.is_pregnant, 
                      char_obj.pregnancy_progress_days, char_obj.time_in_current_action))

                # Salva i bisogni del personaggio
                for need_key, need_data_dict in char_data_to_save.get("needs", {}).items():
                    cursor.execute("""
                        INSERT INTO SavedCharacterNeeds 
                            (character_uuid, save_id, need_name, current_value)
                        VALUES (?, ?, ?, ?)
                    """, (char_obj.uuid, current_save_id, need_key, need_data_dict.get("current_value")))
            
        print(f"INFO DB: Partita '{save_name_str}' salvata con ID: {current_save_id}")
        return True
    except sqlite3.Error as e:
        print(f"ERRORE DB durante il salvataggio '{save_name_str}': {e}")
        return False

def get_available_save_slots(conn):
    """Restituisce una lista di (save_id, save_name, timestamp) ordinati per timestamp."""
    if not conn: return []
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT save_id, save_name, timestamp FROM GameSaves ORDER BY timestamp DESC")
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"ERRORE DB leggendo lista salvataggi: {e}")
        return []

def load_game_state_from_db(conn, save_id_to_load):
    """Carica lo stato del gioco e degli NPC. Restituisce (game_state_globals, loaded_characters_list)."""
    if not conn or Character is None or config is None: # Controlla se Character e config sono importati
        print("ERRORE LOAD: DB non connesso o Character/Config non disponibili.")
        return None, None
        
    cursor = conn.cursor()
    loaded_game_globals = {}
    recreated_characters_list = []

    try:
        # Carica stato globale del gioco
        cursor.execute("SELECT * FROM GameSaves WHERE save_id = ?", (save_id_to_load,))
        gs_row_tuple = cursor.fetchone()
        if not gs_row_tuple: print(f"ERRORE DB: Salvataggio ID {save_id_to_load} non trovato."); return None, None
        
        # Mappa i nomi delle colonne ai valori
        gs_cols = [desc[0] for desc in cursor.description]
        gs_data = dict(zip(gs_cols, gs_row_tuple))

        loaded_game_globals = {
            "save_name": gs_data["save_name"], "timestamp": gs_data["timestamp"], 
            "year": gs_data["current_game_year"], "month": gs_data["current_game_month"], 
            "day": gs_data["current_game_day"], "hour_float": gs_data["current_game_hour_float"], 
            "total_sim_hours": gs_data["current_game_total_sim_hours_elapsed"],
            "speed_index": gs_data["current_time_speed_index"], 
            "food_visible": bool(gs_data["food_visible"]), 
            "food_cooldown": gs_data["food_cooldown_timer"],
            "selected_char_uuid": gs_data["ui_selected_char_uuid"]
        }

        # Carica personaggi
        cursor.execute("SELECT * FROM SavedCharacters WHERE save_id = ?", (save_id_to_load,))
        char_cols = [desc[0] for desc in cursor.description]
        
        temp_char_map_by_uuid = {} # Per ricollegare target_partner
        for char_row_tuple in cursor.fetchall():
            char_data_from_db = dict(zip(char_cols, char_row_tuple))
            char_data_for_from_dict = { # Prepara il dizionario per Character.from_data
                "uuid": char_data_from_db["character_uuid"], "name": char_data_from_db["name"], 
                "gender": char_data_from_db["gender"], "x": char_data_from_db["x_pos"], "y": char_data_from_db["y_pos"],
                "current_action": char_data_from_db["current_action"],
                "target_partner_uuid": char_data_from_db["target_partner_uuid"], 
                "age_in_total_game_days": char_data_from_db["age_in_total_game_days"], 
                "is_pregnant": bool(char_data_from_db["is_pregnant"]),
                "pregnancy_progress_days": char_data_from_db["pregnancy_progress_days"], 
                "time_in_current_action": char_data_from_db["time_in_current_action"],
                "needs": {}
            }
            
            cursor.execute("SELECT need_name, current_value FROM SavedCharacterNeeds WHERE character_uuid = ? AND save_id = ?",
                           (char_data_from_db["character_uuid"], save_id_to_load))
            for need_name_db, current_val_db in cursor.fetchall():
                char_data_for_from_dict["needs"][need_name_db.lower()] = {"current_value": current_val_db}
            
            # Determina parametri non salvati (colore, ecc.) per il costruttore
            # Questa parte è un po' un hack, idealmente si salverebbe il "tipo" di NPC o più dettagli
            char_r_load = min(15, getattr(config, 'TILE_SIZE', 32)//2-2)
            speed_load = getattr(config, 'NPC_SPEED', 80)
            color_load = getattr(config, 'NPC_ALPHA_COLOR_MALE', (100,149,237)) 
            spritesheet_fn_load = "male.png"
            if "Beta" in char_data_from_db["name"]: # Semplice distinzione
                 color_load = getattr(config, 'NPC_BETA_COLOR_FEMALE', (255,105,180))
                 spritesheet_fn_load = "female.png"
                 if hasattr(config, 'NPC_SPEED'): speed_load = config.NPC_SPEED -10

            new_char_obj = Character.from_data(char_data_for_from_dict, color_load, char_r_load, speed_load, spritesheet_fn_load, False)
            recreated_characters_list.append(new_char_obj)
            temp_char_map_by_uuid[new_char_obj.uuid] = new_char_obj
        
        # Secondo passaggio per ricollegare i target_partner
        for char_obj in recreated_characters_list:
            # Trova i dati originali di questo char per ottenere il target_partner_uuid
            original_char_data = next((cd for cd in raw_character_data_list if cd["uuid"] == char_obj.uuid), None)
            if original_char_data and original_char_data["target_partner_uuid"]:
                partner_obj = temp_char_map_by_uuid.get(original_char_data["target_partner_uuid"])
                if partner_obj:
                    char_obj.target_partner = partner_obj

        print(f"INFO DB: Partita '{loaded_game_globals['save_name']}' (ID: {save_id_to_load}) caricata.")
        return loaded_game_globals, recreated_characters_list

    except sqlite3.Error as e:
        print(f"ERRORE DB durante il caricamento del salvataggio ID {save_id_to_load}: {e}")
        return None, None
    except Exception as ex_gen:
        print(f"ERRORE GENERICO durante caricamento: {ex_gen}")
        return None, None