# simai/game/simai_save_load_system.py
# MODIFIED: Made save/load debug prints conditional on config.DEBUG_AI_ACTIVE.
# MODIFIED: Corrected target_partner reconstruction during load.
# MODIFIED: Added saving/loading of spritesheet filenames.

import sqlite3
import json
import os
import datetime
import sys # Aggiunto per sys.exit()

try:
    from game.src.entities.character import Character
    from game import config 
except ImportError as e:
    print(f"CRITICAL ERROR (SaveLoadSystem): Could not import Character or Config: {e}")
    # Se questi sono critici, il modulo non può funzionare.
    # Potresti voler uscire o sollevare l'eccezione.
    Character = None 
    config = None 
    # sys.exit() # Considera se uscire qui se config non è caricabile

DB_FILENAME = "simai.db"

# Leggi il flag di debug una volta a livello di modulo se config è disponibile
# Altrimenti, default a False per non stampare errori durante il tentativo di importazione.
DEBUG_MESSAGES_ACTIVE = True
if config: # Verifica se l'import di config è riuscito
    DEBUG_MESSAGES_ACTIVE = getattr(config, 'DEBUG_AI_ACTIVE', False) # Usa lo stesso flag dell'IA o crea uno dedicato


def connect_db(db_name=DB_FILENAME):
    conn = None
    try:
        conn = sqlite3.connect(db_name)
        conn.execute("PRAGMA foreign_keys = ON;")
    except sqlite3.Error as e_connect:
        if DEBUG_MESSAGES_ACTIVE: # Usa il flag qui
            print(f"DB CONNECTION ERROR: Could not connect to database '{db_name}': {e_connect}")
        # Considera di sollevare l'eccezione o ritornare None per una gestione più robusta in main.py
    return conn

def create_tables_if_not_exist(conn):
    if not conn: return
    cursor = conn.cursor()
    
    try:
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
            spritesheet_filename TEXT,
            sleep_spritesheet_filename TEXT,
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
        # if DEBUG_MESSAGES_ACTIVE: print("DB INFO: Tables checked/created.") # Meno verboso
    except sqlite3.Error as e_create:
        if DEBUG_MESSAGES_ACTIVE:
            print(f"DB ERROR creating tables: {e_create}")


def save_current_game_state(conn, save_name_str, global_state_dict, characters_list):
    if not conn or Character is None: 
        if DEBUG_MESSAGES_ACTIVE: print("SAVE ERROR: DB not connected or Character class not available.")
        return False
    cursor = conn.cursor()
    current_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with conn:
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
            
            cursor.execute("SELECT save_id FROM GameSaves WHERE save_name = ?", (save_name_str,))
            result = cursor.fetchone()
            if not result: 
                if DEBUG_MESSAGES_ACTIVE: print("DB ERROR: Could not retrieve save_id after insert/update.")
                return False
            current_save_id = result[0]

            cursor.execute("DELETE FROM SavedCharacterNeeds WHERE save_id = ?", (current_save_id,))
            cursor.execute("DELETE FROM SavedCharacters WHERE save_id = ?", (current_save_id,))

            for char_obj in characters_list:
                char_data_to_save = char_obj.to_dict()
                
                cursor.execute("""
                    INSERT INTO SavedCharacters 
                        (character_uuid, save_id, name, gender, x_pos, y_pos, current_action, 
                         target_partner_uuid, age_in_total_game_days, is_pregnant, 
                         pregnancy_progress_days, time_in_current_action,
                         spritesheet_filename, sleep_spritesheet_filename)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (char_obj.uuid, current_save_id, char_obj.name, char_obj.gender, 
                      char_obj.x, char_obj.y, char_obj.current_action,
                      char_data_to_save.get('target_partner_uuid'), 
                      char_obj.age_in_total_game_days, char_obj.is_pregnant, 
                      char_obj.pregnancy_progress_days, char_obj.time_in_current_action,
                      char_data_to_save.get('spritesheet_filename'),
                      char_data_to_save.get('sleep_spritesheet_filename')))

                for need_key, need_data_dict in char_data_to_save.get("needs", {}).items():
                    cursor.execute("""
                        INSERT INTO SavedCharacterNeeds 
                            (character_uuid, save_id, need_name, current_value)
                        VALUES (?, ?, ?, ?)
                    """, (char_obj.uuid, current_save_id, need_key, need_data_dict.get("current_value")))
            
        if DEBUG_MESSAGES_ACTIVE: print(f"DB INFO: Game '{save_name_str}' saved with ID: {current_save_id}")
        return True
    except sqlite3.Error as e:
        if DEBUG_MESSAGES_ACTIVE: print(f"DB ERROR during save '{save_name_str}': {e}")
        return False
    except Exception as ex_save:
        if DEBUG_MESSAGES_ACTIVE: print(f"GENERIC ERROR during save '{save_name_str}': {ex_save}")
        return False

def get_available_save_slots(conn):
    if not conn: return []
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT save_id, save_name, timestamp FROM GameSaves ORDER BY timestamp DESC")
        return cursor.fetchall()
    except sqlite3.Error as e:
        if DEBUG_MESSAGES_ACTIVE: print(f"DB ERROR reading save list: {e}")
        return []

def load_game_state_from_db(conn, save_id_to_load):
    if not conn or Character is None or config is None:
        if DEBUG_MESSAGES_ACTIVE: print("LOAD ERROR: DB not connected or Character/Config not available.")
        return None, None
        
    cursor = conn.cursor()
    loaded_game_globals = {}
    recreated_characters_list = []
    raw_character_data_for_linking = []

    try:
        cursor.execute("SELECT * FROM GameSaves WHERE save_id = ?", (save_id_to_load,))
        gs_row_tuple = cursor.fetchone()
        if not gs_row_tuple: 
            if DEBUG_MESSAGES_ACTIVE: print(f"DB ERROR: Save ID {save_id_to_load} not found.")
            return None, None
        
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

        cursor.execute("SELECT * FROM SavedCharacters WHERE save_id = ?", (save_id_to_load,))
        char_cols_desc = [desc[0] for desc in cursor.description]
        temp_char_map_by_uuid = {} 
        all_char_rows = cursor.fetchall()
        
        for char_row_tuple in all_char_rows:
            char_data_from_db = dict(zip(char_cols_desc, char_row_tuple))
            raw_character_data_for_linking.append(char_data_from_db)

            char_data_for_from_dict = {
                "uuid": char_data_from_db["character_uuid"], "name": char_data_from_db["name"], 
                "gender": char_data_from_db["gender"], "x": char_data_from_db["x_pos"], "y": char_data_from_db["y_pos"],
                "current_action": char_data_from_db["current_action"],
                "age_in_total_game_days": char_data_from_db["age_in_total_game_days"], 
                "is_pregnant": bool(char_data_from_db["is_pregnant"]),
                "pregnancy_progress_days": char_data_from_db["pregnancy_progress_days"], 
                "time_in_current_action": char_data_from_db["time_in_current_action"],
                "spritesheet_filename": char_data_from_db.get("spritesheet_filename"),
                "sleep_spritesheet_filename": char_data_from_db.get("sleep_spritesheet_filename"),
                "needs": {}
            }
            
            cursor.execute("SELECT need_name, current_value FROM SavedCharacterNeeds WHERE character_uuid = ? AND save_id = ?",
                           (char_data_from_db["character_uuid"], save_id_to_load))
            for need_name_db, current_val_db in cursor.fetchall():
                char_data_for_from_dict["needs"][need_name_db.lower()] = {"current_value": current_val_db}
            
            char_r_load = min(15, getattr(config, 'TILE_SIZE', 32)//2-2)
            speed_load = getattr(config, 'NPC_SPEED', 80)
            color_load = getattr(config, 'NPC_ALPHA_COLOR_MALE', (100,149,237)) # Fallback
            
            new_char_obj = Character.from_data(
                char_data_for_from_dict, 
                fallback_color=color_load,
                fallback_radius=char_r_load,
                speed=speed_load
            )
            recreated_characters_list.append(new_char_obj)
            temp_char_map_by_uuid[new_char_obj.uuid] = new_char_obj
        
        for char_obj in recreated_characters_list:
            original_data_for_this_char = next(
                (raw_data for raw_data in raw_character_data_for_linking if raw_data["character_uuid"] == char_obj.uuid), None
            )
            if original_data_for_this_char:
                target_uuid = original_data_for_this_char.get("target_partner_uuid")
                if target_uuid:
                    partner_obj = temp_char_map_by_uuid.get(target_uuid)
                    if partner_obj:
                        char_obj.target_partner = partner_obj
                    elif DEBUG_MESSAGES_ACTIVE:
                        print(f"LOAD WARNING: Partner UUID {target_uuid} for {char_obj.name} not found in current load batch.")
            
        if DEBUG_MESSAGES_ACTIVE: print(f"DB INFO: Game '{loaded_game_globals['save_name']}' (ID: {save_id_to_load}) loaded.")
        return loaded_game_globals, recreated_characters_list

    except sqlite3.Error as e:
        if DEBUG_MESSAGES_ACTIVE: print(f"DB ERROR during load of save ID {save_id_to_load}: {e}")
        return None, None
    except Exception as ex_gen:
        if DEBUG_MESSAGES_ACTIVE: print(f"GENERIC ERROR during load: {ex_gen}")
        return None, None