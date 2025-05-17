# /home/nhytros/work/clair/simai/game/src/modules/game_state_module.py
import pygame # Necessario per pygame.Rect

# Importa config in modo che GameState possa accedervi per i valori iniziali.
# Dato che questo modulo è in game/src/modules/, e config è in game/,
# l'import corretto quando si esegue con 'python -m game.main' è:
from game import config # Cercherà simai/game/config.py
# Se Character e altri tipi sono necessari per type hinting qui, importali con il percorso completo
# from game.src.entities.character import Character # Esempio per type hinting

class GameState:
    def __init__(self):
        # Attributi dalla tua definizione originale
        self.current_time_speed_index: int = 0 
        self.previous_time_speed_index_before_sleep_ffwd: int = 0 
        self.is_sleep_fast_forward_active: bool = False 
        self.current_game_total_sim_hours_elapsed: float = 0.0 
        self.current_game_hour_float: float = config.INITIAL_START_HOUR 
        self.current_game_day: int = 1
        self.current_game_month: int = 1 
        self.current_game_year: int = 1
        self.food_visible: bool = True 
        self.food_cooldown_timer: float = 0.0 
        
        self.bed_rect: pygame.Rect | None = None
        self.bed_images: dict = {"base": None, "cover": None} # Sarà popolato da game_utils.load_all_game_assets()
        self.bed_slot_1_occupied_by: str | None = None 
        self.bed_slot_2_occupied_by: str | None = None
        self.bed_slot_1_interaction_pos_world: tuple | None = None
        self.bed_slot_2_interaction_pos_world: tuple | None = None
        self.bed_slot_1_sleep_pos_world: tuple | None = None
        self.bed_slot_2_sleep_pos_world: tuple | None = None
        
        self.toilet_rect_instance: pygame.Rect | None = None
        
        # Attributi che avevamo discusso per una gestione più centralizzata
        # Questi verranno inizializzati/popolati in main.py dopo la creazione di GameState
        self.screen: pygame.Surface | None = None
        self.main_font: pygame.font.Font | None = None
        self.debug_font: pygame.font.Font | None = None
        self.sprite_sheet_manager = None # Sarà un'istanza di SpriteSheetManager
        self.game_time_handler = None    # Sarà un'istanza di GameTimeManager
        self.ui_manager = None           # Sarà un'istanza di UIManager (pygame_gui)
        
        self.all_npc_characters_list: list['Character'] = [] # Lista degli NPC, usa forward reference per Character
        self.world_objects_list: list = [] # Lista per oggetti del mondo come Bed, Toilet (se hanno stato da salvare)
        self.a_star_grid_instance = None  # Griglia per il pathfinding
        
        # UI Elements (questi potrebbero essere gestiti da ui_manager o direttamente qui se preferisci)
        self.time_display_ui_element = None # Esempio se gestito qui (o riferimento a elemento in UIManager)
        # self.speed_buttons = [] # Esempio

        # Per il debug e l'auto-salvataggio
        self.DEBUG_AI_ACTIVE: bool = getattr(config, 'DEBUG_AI_ACTIVE', False)
        self.last_auto_save_time: float = 0.0 # Memorizza come float (ticks)

    # Potresti aggiungere metodi helper a GameState in futuro, ad esempio:
    # def initialize_managers(self, screen, main_font, debug_font, sprite_sheet_manager, day_duration, sky_colors, period_definitions):
    #     self.screen = screen
    #     self.main_font = main_font
    #     self.debug_font = debug_font
    #     self.sprite_sheet_manager = sprite_sheet_manager
    #     self.game_time_handler = GameTimeManager(day_duration, sky_colors, period_definitions)
    #     # Inizializza ui_manager qui se vuoi
    #     grid_width_actual = config.SCREEN_WIDTH // config.TILE_SIZE
    #     grid_height_actual = (config.SCREEN_HEIGHT - config.PANEL_UI_HEIGHT) // config.TILE_SIZE
    #     self.a_star_grid_instance = initialize_grid(grid_width_actual, grid_height_actual, config.TILE_SIZE)


    def initialize_world_objects_and_grid(self, generate_objects_func, setup_grid_func):
        """Metodo per inizializzare gli oggetti del mondo e la griglia A*."""
        if self.sprite_sheet_manager is None:
            print("ERRORE (GameState): SpriteSheetManager non inizializzato prima di creare oggetti del mondo.")
            return

        # self.all_objects è usato nel tuo main.py originale, lo rinomino in world_objects_list per coerenza
        self.world_objects_list = generate_objects_func(self.sprite_sheet_manager, self) # Passa game_state se necessario
        
        if self.a_star_grid_instance is None: # Evita di ricreare se esiste già (es. dopo un caricamento)
            grid_width_actual = config.SCREEN_WIDTH // config.TILE_SIZE
            grid_height_actual = (config.SCREEN_HEIGHT - config.PANEL_UI_HEIGHT) // config.TILE_SIZE
            self.a_star_grid_instance = setup_grid_func([], grid_width_actual, grid_height_actual, config.TILE_SIZE) # Passa ostacoli iniziali vuoti

        self.update_grid_for_pathfinding()


    def initialize_npcs(self, num_npcs: int, initialize_npcs_func):
        """Metodo per inizializzare gli NPC."""
        if not self.a_star_grid_instance:
            print("ERRORE (GameState): a_star_grid_instance non inizializzata prima di initialize_npcs.")
            return
        if not self.sprite_sheet_manager or not self.main_font:
            print("ERRORE (GameState): sprite_sheet_manager o main_font non inizializzati prima di initialize_npcs.")
            return
            
        self.all_npc_characters_list = initialize_npcs_func(self, num_npcs) # Passa self (GameState)
        self.update_grid_for_pathfinding()


    def update_grid_for_pathfinding(self):
        """Aggiorna la griglia A* con gli ostacoli correnti (oggetti e NPC)."""
        if self.a_star_grid_instance:
            # Prepara la lista degli ostacoli basata su world_objects_list
            obstacle_rects_for_grid = []
            for obj in self.world_objects_list:
                if hasattr(obj, 'rect') and obj.rect and getattr(obj, 'is_obstacle', True): # Se ha un rect ed è un ostacolo
                    obstacle_rects_for_grid.append(obj.rect)
            
            # La funzione setup_pathfinding_grid che usi sembra prendere solo rects,
            # dovresti avere una funzione update_grid_obstacles che prende anche gli NPC se bloccano dinamicamente.
            # Per ora, usiamo la tua setup_pathfinding_grid se è l'unica disponibile.
            # Idealmente, setup_pathfinding_grid crea la griglia, update_grid_obstacles la aggiorna.
            # main_pathfinding_grid = game_utils.setup_pathfinding_grid(obstacle_rects_for_grid)
            # Se game_utils.setup_pathfinding_grid ritorna la griglia:
            # self.a_star_grid_instance = game_utils.setup_pathfinding_grid(obstacle_rects_for_grid, 
            #                                                             self.all_npc_characters_list,
            #                                                             self.a_star_grid_instance.width, # o calcola da config
            #                                                             self.a_star_grid_instance.height, # o calcola da config
            #                                                             config.TILE_SIZE)
            # Altrimenti, se hai una funzione di update separata:
            self.a_star_grid_instance.update_grid_obstacles(self.world_objects_list, self.all_npc_characters_list) # Assumendo che esista
        elif self.DEBUG_AI_ACTIVE:
            print("GAME_STATE: Tentativo di aggiornare la griglia A* ma non è inizializzata.")

    # Metodi per il salvataggio/caricamento JSON (che verranno chiamati da simai_save_load_system)
    # Questi sono solo esempi di come potresti strutturare, la logica principale è in simai_save_load_system

    def to_dict_for_json(self):
        """Prepara un dizionario di GameState per la serializzazione JSON."""
        # Non includere oggetti Pygame non serializzabili come Surface, Font, o istanze complesse
        # che verranno ricreate al caricamento (es. sprite_sheet_manager, ui_manager).
        
        # Prepara i dati degli NPC
        npcs_data = [npc.to_dict() for npc in self.all_npc_characters_list]
        
        # Prepara i dati degli oggetti del mondo (se hanno un metodo to_dict e stato da salvare)
        world_objects_data = []
        for obj in self.world_objects_list:
            if hasattr(obj, 'to_dict'):
                world_objects_data.append(obj.to_dict())
            # else: potresti salvare info base come tipo e posizione se non hanno to_dict

        # Dati del GameTimeHandler
        time_details_data = {}
        if self.game_time_handler:
            time_details_data = {
                "day": self.game_time_handler.day,
                "month": self.game_time_handler.month,
                "year": self.game_time_handler.year,
                "hour": self.game_time_handler.hour,
                "minute": self.game_time_handler.minute,
                "total_game_seconds_elapsed": self.game_time_handler.total_game_seconds_elapsed,
                "current_period_name": self.game_time_handler.current_period_name,
                "current_sky_color_index": self.game_time_handler.current_sky_color_index,
            }
        
        # Dati del Bed (esempio, se non hai una classe BedObject con to_dict)
        bed_rect_data = [self.bed_rect.x, self.bed_rect.y, self.bed_rect.width, self.bed_rect.height] if self.bed_rect else None

        return {
            "current_time_speed_index": self.current_time_speed_index,
            "previous_time_speed_index_before_sleep_ffwd": self.previous_time_speed_index_before_sleep_ffwd,
            "is_sleep_fast_forward_active": self.is_sleep_fast_forward_active,
            # Non salviamo current_game_total_sim_hours_elapsed, current_game_hour_float, ecc.
            # direttamente qui se sono già in time_details_data e vengono ripristinati tramite GameTimeHandler.
            "food_visible": self.food_visible,
            "food_cooldown_timer": self.food_cooldown_timer,
            
            "bed_rect_data": bed_rect_data, # Esempio se non hai una classe Bed
            "bed_slot_1_occupied_by": self.bed_slot_1_occupied_by,
            "bed_slot_2_occupied_by": self.bed_slot_2_occupied_by,
            # bed_slot_..._pos_world sono derivati da bed_rect e config, non serve salvarli se bed_rect è salvato
            
            # toilet_rect_instance è anch'esso probabilmente definito da config, quindi non serve salvarlo
            # a meno che la sua posizione o stato non cambi dinamicamente.

            "all_npc_characters_data": npcs_data,
            "world_objects_data": world_objects_data, # Se implementato
            "game_time_details_data": time_details_data,
            "last_auto_save_time": self.last_auto_save_time,
            # Aggiungi qui qualsiasi altro attributo di GameState che sia serializzabile e necessario
        }

    def populate_from_dict(self, data, sprite_sheet_manager_asset, main_font_asset, character_class_ref):
        """Popola GameState da un dizionario (dati JSON caricati)."""
        # sprite_sheet_manager_asset e main_font_asset sono gli asset reali
        # character_class_ref è un riferimento alla classe Character per creare istanze
        
        self.current_time_speed_index = data.get("current_time_speed_index", 0)
        self.previous_time_speed_index_before_sleep_ffwd = data.get("previous_time_speed_index_before_sleep_ffwd", 0)
        self.is_sleep_fast_forward_active = data.get("is_sleep_fast_forward_active", False)
        self.food_visible = data.get("food_visible", True)
        self.food_cooldown_timer = data.get("food_cooldown_timer", 0.0)
        self.last_auto_save_time = data.get("last_auto_save_time", 0.0) # Usa 0.0 o pygame.time.get_ticks() come default sensato

        # Ripristina GameTimeHandler
        time_details_data = data.get("game_time_details_data", {})
        if self.game_time_handler and time_details_data:
            self.game_time_handler.day = time_details_data.get("day", 1)
            self.game_time_handler.month = time_details_data.get("month", 1)
            self.game_time_handler.year = time_details_data.get("year", 1)
            self.game_time_handler.hour = time_details_data.get("hour", config.INITIAL_START_HOUR)
            self.game_time_handler.minute = time_details_data.get("minute", 0)
            self.game_time_handler.total_game_seconds_elapsed = time_details_data.get("total_game_seconds_elapsed", 0.0)
            self.game_time_handler.current_sky_color_index = time_details_data.get("current_sky_color_index", 0)
            self.game_time_handler.update_time(0) # Forza ricalcolo periodo, colore cielo, ecc.
        
        # Ricostruisci il letto se non hai una classe BedObject dedicata
        bed_rect_data = data.get("bed_rect_data")
        if bed_rect_data:
            self.bed_rect = pygame.Rect(bed_rect_data)
            # Ricalcola le posizioni degli slot basate su bed_rect e config
            if hasattr(config, 'BED_SLOT_1_INTERACTION_OFFSET'): # Verifica se le costanti esistono
                s1_inter_offset = config.BED_SLOT_1_INTERACTION_OFFSET
                s2_inter_offset = config.BED_SLOT_2_INTERACTION_OFFSET
                s1_sleep_offset = config.BED_SLOT_1_SLEEP_POS_OFFSET
                s2_sleep_offset = config.BED_SLOT_2_SLEEP_POS_OFFSET
                self.bed_slot_1_interaction_pos_world = (self.bed_rect.left + s1_inter_offset[0], self.bed_rect.top + s1_inter_offset[1])
                self.bed_slot_2_interaction_pos_world = (self.bed_rect.left + s2_inter_offset[0], self.bed_rect.top + s2_inter_offset[1])
                self.bed_slot_1_sleep_pos_world = (self.bed_rect.left + s1_sleep_offset[0], self.bed_rect.top + s1_sleep_offset[1])
                self.bed_slot_2_sleep_pos_world = (self.bed_rect.left + s2_sleep_offset[0], self.bed_rect.top + s2_sleep_offset[1])

        self.bed_slot_1_occupied_by = data.get("bed_slot_1_occupied_by")
        self.bed_slot_2_occupied_by = data.get("bed_slot_2_occupied_by")

        # Ricrea NPC
        self.all_npc_characters_list = []
        loaded_npcs_data = data.get("all_npc_characters_data", [])
        if not sprite_sheet_manager_asset or not main_font_asset:
            if self.DEBUG_AI_ACTIVE: print("GAME_STATE WARN: SpriteSheetManager o Font non disponibili durante il caricamento degli NPC.")
        else:
            for npc_data in loaded_npcs_data:
                try:
                    # Passa self (l'istanza di GameState) a Character.from_dict
                    character = character_class_ref.from_dict(npc_data, sprite_sheet_manager_asset, main_font_asset, self)
                    self.all_npc_characters_list.append(character)
                except Exception as e_npc_load:
                    if self.DEBUG_AI_ACTIVE: print(f"GAME_STATE ERROR: Errore nel caricare NPC '{npc_data.get('name', 'Sconosciuto')}': {e_npc_load}")
        
        # TODO: Ricrea world_objects_list
        # loaded_world_objects_data = data.get("world_objects_data", [])
        # for obj_data in loaded_world_objects_data:
        #    ... (logica per determinare il tipo di oggetto e chiamare il suo from_dict) ...

        if self.DEBUG_AI_ACTIVE: print(f"GAME_STATE: Popolato da dizionario. NPC: {len(self.all_npc_characters_list)}")