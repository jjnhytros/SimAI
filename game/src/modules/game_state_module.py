# /home/nhytros/work/clair/simai/game/src/modules/game_state_module.py
import pygame # Per pygame.Rect e potenzialmente altri tipi pygame

# Importa config in modo che GameState possa accedervi per i valori iniziali.
# Dato che questo modulo è in game/src/modules/, e config è in game/,
# l'import corretto quando si esegue con 'python -m game.main' è:
from game import config # Cercherà simai/game/config.py

# Forward declaration per type hinting, se Character non viene importato direttamente qui
from typing import TYPE_CHECKING, List, Optional, Tuple, Dict # Aggiungi Dict
if TYPE_CHECKING:
    from game.src.entities.character import Character
    # Se usi altre classi per type hinting qui, aggiungile sotto TYPE_CHECKING
    # Esempio:
    # from ..asset_manager import SpriteSheetManager 
    # from ..time_manager import GameTimeManager
    # from ..ui_manager import UIManager

class GameState:
    def __init__(self):
        # Attributi dalla tua definizione originale in main.py
        self.current_time_speed_index: int = 0 
        self.previous_time_speed_index_before_sleep_ffwd: int = 0 
        self.is_sleep_fast_forward_active: bool = False 
        self.is_paused_by_player: bool = False # Inizializza lo stato di pausa manuale
        self.current_game_total_sim_hours_elapsed: float = 0.0
        self.current_game_hour_float: float = config.INITIAL_START_HOUR # Da config
        self.current_game_day: int = 1
        self.current_game_month: int = 1 
        self.current_game_year: int = 1
        self.food_visible: bool = True 
        self.food_cooldown_timer: float = 0.0 

        # Per il letto
        self.bed_rect: Optional[pygame.Rect] = None
        self.bed_images: Dict[str, Optional[pygame.Surface]] = {"base": None, "cover": None}
        self.bed_slot_1_interaction_pos_world: Optional[Tuple[float, float]] = None
        self.bed_slot_1_occupied_by: Optional[str] = None 
        self.bed_slot_1_sleep_pos_world: Optional[Tuple[float, float]] = None
        self.bed_slot_2_interaction_pos_world: Optional[Tuple[float, float]] = None
        self.bed_slot_2_occupied_by: Optional[str] = None
        self.bed_slot_2_sleep_pos_world: Optional[Tuple[float, float]] = None

        # Per il bagno
        self.toilet_facing_direction: Optional[str] = None # Se lo usi
        self.toilet_interaction_point_world: Optional[Tuple[float, float]] = None
        self.toilet_rect_instance: Optional[pygame.Rect] = None
        self.toilet_sit_point_world: Optional[Tuple[int, int]] = None # Dove l'NPC si siede visivamente

        # Attributi aggiunti per una gestione più centralizzata dello stato,
        # questi verranno inizializzati in main.py dopo la creazione dell'istanza di GameState.
        self.screen: Optional[pygame.Surface] = None
        self.main_font: Optional[pygame.font.Font] = None # Font principale per Character, UI, ecc.
        self.debug_font: Optional[pygame.font.Font] = None # Font per info di debug

        self.sprite_sheet_manager = None # Istanza di SpriteSheetManager (da game_utils o asset_manager)
        self.game_time_handler = None    # Istanza di GameTimeManager (da time_manager)
        self.ui_manager_instance = None  # Istanza di pygame_gui.UIManager

        self.all_npc_characters_list: List['Character'] = [] # Lista degli NPC (usa forward reference)
        self.world_objects_list: List[pygame.Rect] = [] # Lista di Rect per ostacoli fissi, o lista di oggetti più complessi
        self.a_star_grid_instance = None  # Griglia per il pathfinding

        # Elementi UI (esempi, potrebbero essere gestiti interamente da ui_manager_instance)
        self.time_display_ui_element = None # Riferimento a un elemento di pygame_gui
        # self.speed_buttons_gui = [] # Lista di riferimenti a bottoni pygame_gui

        self.DEBUG_AI_ACTIVE: bool = getattr(config, 'DEBUG_AI_ACTIVE', False)
        self.last_auto_save_time: float = 0.0 # Per l'auto-salvataggio (ticks)

    # Potresti voler spostare qui alcuni metodi helper da main.py che operano su GameState,
    # o aggiungere metodi per una gestione più pulita dello stato.
    # Esempio:
    def set_managers(self, screen, main_font, debug_font, sprite_sheet_manager, game_time_handler, ui_manager_instance):
        self.screen = screen
        self.main_font = main_font
        self.debug_font = debug_font
        self.sprite_sheet_manager = sprite_sheet_manager
        self.game_time_handler = game_time_handler
        self.ui_manager_instance = ui_manager_instance

    # I metodi to_dict_for_json e populate_from_dict che avevamo discusso andrebbero qui,
    # adattati per usare gli attributi di questa classe GameState.
    # Li ometto per brevità qui, ma li abbiamo già definiti.
    # Assicurati che facciano riferimento agli attributi corretti di questa classe.
    # Esempio parziale:
    def to_dict_for_json(self):
        # Prepara i dati degli NPC
        npcs_data = []
        if self.all_npc_characters_list: # Controlla se la lista esiste ed è popolata
             npcs_data = [npc.to_dict() for npc in self.all_npc_characters_list]

        time_details_data = {}
        if self.game_time_handler: # Controlla se game_time_handler è stato inizializzato
            time_details_data = {
                "day": self.game_time_handler.day,
                "month": self.game_time_handler.month,
                # ... e così via ...
                "current_sky_color_index": self.game_time_handler.current_sky_color_index,
            }
        else: # Fallback se game_time_handler non è pronto (improbabile se la logica di init è corretta)
            time_details_data = {
                "day": self.current_game_day, "month": self.current_game_month, "year": self.current_game_year,
                "hour": self.current_game_hour_float, "minute": int((self.current_game_hour_float % 1) * 60),
                "total_game_seconds_elapsed": self.current_game_total_sim_hours_elapsed * 3600, # Converti ore in secondi
                # "current_period_name": calcola da self.current_game_hour_float,
                # "current_sky_color_index": calcola o default
            }


        bed_rect_data = [self.bed_rect.x, self.bed_rect.y, self.bed_rect.width, self.bed_rect.height] if self.bed_rect else None
        toilet_rect_data = [self.toilet_rect_instance.x, self.toilet_rect_instance.y, self.toilet_rect_instance.width, self.toilet_rect_instance.height] if self.toilet_rect_instance else None


        return {
            "current_time_speed_index": self.current_time_speed_index,
            "previous_time_speed_index_before_sleep_ffwd": self.previous_time_speed_index_before_sleep_ffwd,
            "is_sleep_fast_forward_active": self.is_sleep_fast_forward_active,
            "food_visible": self.food_visible,
            "food_cooldown_timer": self.food_cooldown_timer,
            "bed_rect_data": bed_rect_data,
            "bed_slot_1_occupied_by": self.bed_slot_1_occupied_by,
            "bed_slot_2_occupied_by": self.bed_slot_2_occupied_by,
            "toilet_rect_data": toilet_rect_data, # Esempio se vuoi salvare il rect del bagno
            "all_npc_characters_data": npcs_data,
            "game_time_details_data": time_details_data,
            "last_auto_save_time": self.last_auto_save_time,
        }

    def populate_from_dict(self, data, character_class_ref):
        # Asset manager e font dovrebbero essere già in self.sprite_sheet_manager e self.main_font
        # se impostati correttamente in main.py prima di chiamare load_game_state_json.

        self.current_time_speed_index = data.get("current_time_speed_index", 0)
        self.previous_time_speed_index_before_sleep_ffwd = data.get("previous_time_speed_index_before_sleep_ffwd", 0)
        self.is_sleep_fast_forward_active = data.get("is_sleep_fast_forward_active", False)
        self.food_visible = data.get("food_visible", True)
        self.food_cooldown_timer = data.get("food_cooldown_timer", 0.0)
        self.last_auto_save_time = data.get("last_auto_save_time", pygame.time.get_ticks()) # Resetta se non trovato

        time_details_data = data.get("game_time_details_data", {})
        if self.game_time_handler and time_details_data:
            self.game_time_handler.day = time_details_data.get("day", 1)
            self.game_time_handler.month = time_details_data.get("month", 1)
            self.game_time_handler.year = time_details_data.get("year", 1)
            self.game_time_handler.hour = time_details_data.get("hour", config.INITIAL_START_HOUR)
            self.game_time_handler.minute = time_details_data.get("minute", 0)
            self.game_time_handler.total_game_seconds_elapsed = time_details_data.get("total_game_seconds_elapsed", 0.0)
            self.game_time_handler.current_sky_color_index = time_details_data.get("current_sky_color_index", 0)
            self.game_time_handler.update_time(0) 
        else: # Fallback se game_time_handler non è ancora inizializzato o dati mancanti
            self.current_game_day = time_details_data.get("day", 1)
            # ... (imposta gli attributi _day, _month, _hour_float direttamente)

        bed_rect_data = data.get("bed_rect_data")
        if bed_rect_data:
            self.bed_rect = pygame.Rect(bed_rect_data)
            # Ricalcola posizioni slot qui, come facevi in main.py
            if hasattr(config, 'BED_SLOT_1_INTERACTION_OFFSET'):
                s1_io, s2_io = config.BED_SLOT_1_INTERACTION_OFFSET, config.BED_SLOT_2_INTERACTION_OFFSET
                s1_so, s2_so = config.BED_SLOT_1_SLEEP_POS_OFFSET, config.BED_SLOT_2_SLEEP_POS_OFFSET
                self.bed_slot_1_interaction_pos_world = (self.bed_rect.left + s1_io[0], self.bed_rect.top + s1_io[1])
                self.bed_slot_2_interaction_pos_world = (self.bed_rect.left + s2_io[0], self.bed_rect.top + s2_io[1])
                self.bed_slot_1_sleep_pos_world = (self.bed_rect.left + s1_so[0], self.bed_rect.top + s1_so[1])
                self.bed_slot_2_sleep_pos_world = (self.bed_rect.left + s2_so[0], self.bed_rect.top + s2_so[1])


        self.bed_slot_1_occupied_by = data.get("bed_slot_1_occupied_by")
        self.bed_slot_2_occupied_by = data.get("bed_slot_2_occupied_by")

        toilet_rect_data = data.get("toilet_rect_data")
        if toilet_rect_data:
             self.toilet_rect_instance = pygame.Rect(toilet_rect_data)
        elif hasattr(config, 'TOILET_RECT_PARAMS'): # Ricrea da config se non salvato
            params = config.TOILET_RECT_PARAMS
            self.toilet_rect_instance = pygame.Rect(params["x"], params["y"], params["w"], params["h"])


        self.all_npc_characters_list = []
        loaded_npcs_data = data.get("all_npc_characters_data", [])
        if self.sprite_sheet_manager and self.main_font:
            for npc_data in loaded_npcs_data:
                try:
                    character = character_class_ref.from_dict(npc_data, self.sprite_sheet_manager, self.main_font, self)
                    self.all_npc_characters_list.append(character)
                except Exception as e_npc_load:
                    if self.DEBUG_AI_ACTIVE: print(f"GAME_STATE ERROR: Caricamento NPC '{npc_data.get('name')}': {e_npc_load}")
        elif self.DEBUG_AI_ACTIVE:
            print("GAME_STATE WARN: SpriteSheetManager o Font non impostati in GameState prima di caricare NPC.")

        if self.DEBUG_AI_ACTIVE: print(f"GAME_STATE: Popolato. NPC: {len(self.all_npc_characters_list)}")