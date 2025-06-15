# core/graphics/renderer.py
"""
Gestisce l'inizializzazione di Pygame, la finestra di gioco e il loop di rendering principale.
Riferimento TODO: I.1
"""
import pygame
import time

from typing import Dict, Optional, TYPE_CHECKING, List, Tuple
from pygame.surface import Surface

from core import settings
from core.config import (npc_config, ui_config, time_config, graphics_config)
from core.config.graphics_config import SHEET_DOORS, SHEET_FLOORS

from core.enums import Gender
from core.enums.tile_types import TileType
from core.modules.time_manager import TimeManager 
from assets.asset_manager import AssetManager

if TYPE_CHECKING:
    from core.simulation import Simulation
    from core.character import Character
    from core.world.game_object import GameObject
    from core.world.location import Location

class Renderer:
    TILE_SIZE = 18 
    PANEL_WIDTH = 300 
    TEXT_COLOR = (230, 230, 230) 
    PANEL_BG_COLOR = (40, 40, 60) 
    LINE_HEIGHT = 20 
    NPC_RADIUS = TILE_SIZE // 2 - 3 
    SELECTION_BORDER_COLOR = (255, 255, 0) 
    SELECTION_BORDER_WIDTH = 3
    MIN_ZOOM = 0.5
    MAX_ZOOM = 3.0

    def __init__(self, width: int = 1280, height: int = 768, caption: str = "SimAI Game"):
        pygame.init()
        self.width = width
        self.height = height
        
        # Definiamo le dimensioni delle aree prima di creare lo schermo
        self.PANEL_WIDTH = ui_config.PANEL_WIDTH
        self.base_width = self.width - self.PANEL_WIDTH
        self.base_height = self.height
        
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        pygame.display.set_caption(f"SimAI {settings.GAME_VERSION} - GUI Edition")
        
        self.clock = pygame.time.Clock()
        self.is_running = False

        # --- Sezione Colori ---
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.PANEL_BG_COLOR = (30, 30, 40)
        self.SELECTION_COLOR = (255, 255, 0)
        self.current_contrast_color = self.WHITE

        # --- Caricamento Font ---
        self._load_fonts()
        
        # --- Asset Manager e Tiles ---
        self.tile_size = 32
        self.asset_manager = AssetManager()
        self.asset_manager.load_assets(tile_size=(self.tile_size, self.tile_size))
        
        # --- Camera e Stato UI ---
        self.camera_offset_x = 0.0
        self.camera_offset_y = 0.0
        self.zoom_level = 1.0
        self.background_cache: Dict[Tuple[str, float], Surface] = {}
        
        self.location_keys_list: List[str] = []
        self.current_location_index: int = 0
        self.current_visible_location_id: Optional[str] = None
        
        self.selected_npc_id: Optional[str] = None
        self.hovered_npc: Optional['Character'] = None
        self.hovered_object: Optional['GameObject'] = None

        if settings.DEBUG_MODE:
            print(f"  [Renderer] Inizializzato Pygame con finestra {self.width}x{self.height} (Area gioco: {self.base_width}x{self.base_height}, Pannello: {self.PANEL_WIDTH}x{self.base_height})")

    @property
    def effective_tile_size(self) -> float:
        return self.TILE_SIZE * self.zoom_level

    @property
    def effective_npc_radius(self) -> int:
        base_radius = self.TILE_SIZE / 2 - 3 
        return max(2, int(base_radius * self.zoom_level))

    def _load_fonts(self):
        """
        Carica tutti i font necessari per la GUI con una logica di fallback.
        """
        print("  [Renderer] Caricamento fonts...")
        try:
            # 1. Prova a caricare il font personalizzato
            print(f"    - Tento di caricare font personalizzato: '{ui_config.FONT_PATH}'")
            self.font_large = pygame.font.Font(ui_config.FONT_PATH, ui_config.FONT_SIZE_LARGE)
            self.font_medium_bold = pygame.font.Font(ui_config.FONT_PATH, ui_config.FONT_SIZE_MEDIUM_BOLD)
            self.font_small = pygame.font.Font(ui_config.FONT_PATH, ui_config.FONT_SIZE_SMALL)
            self.font_debug = pygame.font.Font(ui_config.FONT_PATH, ui_config.FONT_SIZE_DEBUG)
            print("    -> Font personalizzato caricato con successo.")
        except pygame.error:
            print(f"  [Renderer WARN] Font '{ui_config.FONT_PATH}' non trovato o illeggibile.")
            try:
                # 2. Se fallisce, prova a caricare un font di sistema comune
                print(f"    - Tento di caricare font di sistema: '{ui_config.FONT_FALLBACK_SYSTEM}'")
                self.font_large = pygame.font.SysFont(ui_config.FONT_FALLBACK_SYSTEM, ui_config.FONT_SIZE_LARGE)
                self.font_medium_bold = pygame.font.SysFont(ui_config.FONT_FALLBACK_SYSTEM, ui_config.FONT_SIZE_MEDIUM_BOLD)
                self.font_small = pygame.font.SysFont(ui_config.FONT_FALLBACK_SYSTEM, ui_config.FONT_SIZE_SMALL)
                self.font_debug = pygame.font.SysFont(ui_config.FONT_FALLBACK_SYSTEM, ui_config.FONT_SIZE_DEBUG)
                print("    -> Font di sistema caricato con successo.")
            except pygame.error:
                # 3. Se fallisce anche quello, usa il font di default di Pygame
                print(f"  [Renderer WARN] Font di sistema non trovato. Caricamento font di default.")
                self.font_large = pygame.font.Font(None, ui_config.FONT_SIZE_LARGE + 2) # Aumento leggermente per compensare
                self.font_medium_bold = pygame.font.Font(None, ui_config.FONT_SIZE_MEDIUM_BOLD)
                self.font_small = pygame.font.Font(None, ui_config.FONT_SIZE_SMALL)
                self.font_debug = pygame.font.Font(None, ui_config.FONT_SIZE_DEBUG)
        
        # Imposta il grassetto dove serve
        self.font_medium_bold.set_bold(True)

    def _center_camera_on_npc(self, npc: 'Character', current_location: Optional['Location']):
        if not current_location: return

        npc_logical_x = npc.logical_x
        npc_logical_y = npc.logical_y

        visible_tiles_x_at_current_zoom = self.base_width // self.effective_tile_size
        visible_tiles_y_at_current_zoom = self.base_height // self.effective_tile_size
        
        self.camera_offset_x = npc_logical_x - (int(visible_tiles_x_at_current_zoom) // 2)
        self.camera_offset_y = npc_logical_y - (int(visible_tiles_y_at_current_zoom) // 2)

        max_offset_x = max(0, current_location.logical_width - int(visible_tiles_x_at_current_zoom))
        max_offset_y = max(0, current_location.logical_height - int(visible_tiles_y_at_current_zoom))
        
        self.camera_offset_x = max(0, min(self.camera_offset_x, max_offset_x))
        self.camera_offset_y = max(0, min(self.camera_offset_y, max_offset_y))

        if settings.DEBUG_MODE:
            print(f"  [Renderer] Telecamera centrata su {npc.name}. Offset logico: ({self.camera_offset_x}, {self.camera_offset_y})")

    def _get_object_at_screen_pos(self, screen_pos: Tuple[int, int], simulation: 'Simulation') -> Optional['GameObject']:
        """
        Restituisce l'oggetto GameObject che si trova in una data posizione dello schermo.
        """
        if not self.current_visible_location_id: return None
        location = simulation.get_location_by_id(self.current_visible_location_id)
        if not location: return None

        for obj in location.get_objects():
            sprite_def = graphics_config.SPRITE_DEFINITIONS.get(obj.style, {}).get(obj.object_type)
            if not sprite_def: continue

            obj_rect_on_sheet = pygame.Rect(sprite_def['rect'])
            obj_screen_x, obj_screen_y = self._map_logical_to_screen(obj.logical_x, obj.logical_y)
            
            # Crea il rettangolo dell'oggetto sullo schermo
            obj_screen_rect = pygame.Rect(obj_screen_x, obj_screen_y, obj_rect_on_sheet.width * self.zoom_level, obj_rect_on_sheet.height * self.zoom_level)

            if obj_screen_rect.collidepoint(screen_pos):
                return obj
        
        return None

    def _handle_events(self, simulation: Optional['Simulation']):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            elif event.type == pygame.MOUSEWHEEL:
                self.zoom_level += event.y * 0.1
                self.zoom_level = max(self.MIN_ZOOM, min(self.zoom_level, self.MAX_ZOOM))
                self.background_cache.clear()
                if settings.DEBUG_MODE:
                    print(f"  [Renderer] Zoom cambiato a: {self.zoom_level:.2f}")
            elif event.type == pygame.VIDEORESIZE:
                self.width = max(event.w, self.PANEL_WIDTH + 200) 
                self.height = event.h
                self.base_width = self.width - self.PANEL_WIDTH
                self.base_height = self.height
                self.screen_size = (self.width, self.height)
                self.screen = pygame.display.set_mode(self.screen_size, pygame.RESIZABLE)
                if settings.DEBUG_MODE:
                    print(f"  [Renderer] Finestra ridimensionata a: {self.width}x{self.height}")

            elif event.type == pygame.MOUSEMOTION:
                if simulation:
                    mouse_pos = event.pos
                    # Diamo priorità all'NPC se si sovrappone a un oggetto
                    self.hovered_npc = self._get_npc_at_screen_pos(mouse_pos, simulation)
                    if self.hovered_npc:
                        self.hovered_object = None # Se siamo su un NPC, non mostriamo il tooltip dell'oggetto
                    else:
                        self.hovered_object = self._get_object_at_screen_pos(mouse_pos, simulation)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: 
                    mouse_x, mouse_y = event.pos
                    clicked_on_npc_this_turn = False 
                    if mouse_x < self.base_width: 
                        if simulation and self.current_visible_location_id:
                            current_loc = simulation.get_location_by_id(self.current_visible_location_id)
                            if current_loc:
                                for npc_id_in_loc in current_loc.npcs_present_ids:
                                    npc = simulation.get_npc_by_id(npc_id_in_loc)
                                    if npc:
                                        npc_screen_x, npc_screen_y = self._map_logical_to_screen(npc.logical_x, npc.logical_y)
                                        # Usiamo effective_npc_radius per il click detection
                                        distance_sq = (mouse_x - npc_screen_x)**2 + (mouse_y - npc_screen_y)**2
                                        if distance_sq <= (self.effective_npc_radius)**2:
                                            self.selected_npc_id = npc.npc_id
                                            clicked_on_npc_this_turn = True
                                            if settings.DEBUG_MODE:
                                                print(f"  [Renderer] NPC Selezionato: {npc.name} (ID: {npc.npc_id})")
                                            self._center_camera_on_npc(npc, current_loc)
                                            break 
                                if not clicked_on_npc_this_turn:
                                    self.selected_npc_id = None 
                                    if settings.DEBUG_MODE:
                                        print(f"  [Renderer] Selezione NPC resettata (click su vuoto).")
            elif event.type == pygame.KEYDOWN:
                current_loc_for_bounds_calc: Optional['Location'] = None
                if simulation and self.current_visible_location_id:
                    current_loc_for_bounds_calc = simulation.get_location_by_id(self.current_visible_location_id)

                max_offset_x = 0
                max_offset_y = 0
                if current_loc_for_bounds_calc:
                    visible_tiles_x = self.base_width // self.effective_tile_size
                    visible_tiles_y = self.base_height // self.effective_tile_size
                    max_offset_x = max(0, current_loc_for_bounds_calc.logical_width - int(visible_tiles_x))
                    max_offset_y = max(0, current_loc_for_bounds_calc.logical_height - int(visible_tiles_y))

                if event.key == pygame.K_TAB:
                    if self.location_keys_list:
                        self.current_location_index = (self.current_location_index + 1) % len(self.location_keys_list)
                        self.current_visible_location_id = self.location_keys_list[self.current_location_index]
                        self.camera_offset_x = 0 
                        self.camera_offset_y = 0
                        self.selected_npc_id = None 
                        if settings.DEBUG_MODE:
                            print(f"  [Renderer] Cambiata locazione visualizzata a: ID '{self.current_visible_location_id}'")
                elif event.key == pygame.K_SPACE:
                    if simulation and simulation.npcs:
                        
                        # 1. Filtra per ottenere solo gli ID degli NPC contrassegnati come "giocabili"
                        player_npc_ids = sorted([
                            npc.npc_id for npc in simulation.npcs.values() if npc.is_player_character
                        ])
                        
                        # Se non ci sono NPC giocabili, non fare nulla
                        if not player_npc_ids:
                            continue

                        next_index = 0
                        
                        # 2. Cerca l'NPC attualmente selezionato nella lista filtrata
                        if self.selected_npc_id in player_npc_ids:
                            try:
                                current_index = player_npc_ids.index(self.selected_npc_id)
                                # Calcola l'indice del prossimo NPC, tornando all'inizio se necessario
                                next_index = (current_index + 1) % len(player_npc_ids)
                            except ValueError:
                                # Se c'è un errore (improbabile), seleziona il primo
                                next_index = 0
                        
                        # 3. Imposta il nuovo NPC selezionato
                        self.selected_npc_id = player_npc_ids[next_index]
                        newly_selected_npc = simulation.get_npc_by_id(self.selected_npc_id)
                        
                        if newly_selected_npc and newly_selected_npc.current_location_id:
                            new_location_id = newly_selected_npc.current_location_id
                            
                            # 4. Cambia la vista alla locazione del nuovo NPC se è diversa da quella attuale
                            if self.current_visible_location_id != new_location_id:
                                self.current_visible_location_id = new_location_id
                                # Sincronizza l'indice della locazione per il tasto TAB
                                if new_location_id in self.location_keys_list:
                                    self.current_location_index = self.location_keys_list.index(new_location_id)
                                if settings.DEBUG_MODE:
                                    print(f"  [Renderer] Vista cambiata a: '{new_location_id}' per seguire l'NPC.")

                            # 5. Centra la telecamera sul nuovo NPC nella sua locazione
                            current_loc = simulation.get_location_by_id(new_location_id)
                            if current_loc:
                                self._center_camera_on_npc(newly_selected_npc, current_loc)

                            if settings.DEBUG_MODE:
                                print(f"  [Renderer] NPC selezionato con Spazio: {newly_selected_npc.name}")
                elif event.key == pygame.K_LEFT:
                    self.camera_offset_x = max(0, self.camera_offset_x - 1)
                elif event.key == pygame.K_RIGHT:
                    self.camera_offset_x = min(max_offset_x, self.camera_offset_x + 1)
                elif event.key == pygame.K_UP:
                    self.camera_offset_y = max(0, self.camera_offset_y - 1)
                elif event.key == pygame.K_DOWN:
                    self.camera_offset_y = min(max_offset_y, self.camera_offset_y + 1)
                elif event.key == pygame.K_c:
                    if simulation and self.selected_npc_id and current_loc_for_bounds_calc:
                        selected_npc = simulation.get_npc_by_id(self.selected_npc_id)
                        if selected_npc and selected_npc.current_location_id == self.current_visible_location_id:
                            self._center_camera_on_npc(selected_npc, current_loc_for_bounds_calc)
                        elif settings.DEBUG_MODE:
                            print(f"  [Renderer] Impossibile centrare: NPC non selezionato o non nella locazione corrente.")

    def _update_game_state(self, simulation: Optional['Simulation']):
        """Aggiorna lo stato della simulazione se la GUI è attiva."""
        if not settings.DEBUG_MODE and simulation:
            simulation._update_simulation_state() # Chiamiamo qui l'update della simulazione

    def _map_logical_to_screen(self, logical_x: float, logical_y: float) -> Tuple[int, int]:
        # Calcola la posizione centrale della cella logica sullo schermo
        # considerando l'offset della telecamera e lo zoom
        screen_x = (logical_x - self.camera_offset_x + 0.5) * self.effective_tile_size
        screen_y = (logical_y - self.camera_offset_y + 0.5) * self.effective_tile_size
        return int(screen_x), int(screen_y)

    def _draw_npc(self, npc: 'Character'): # <-- Il parametro è chiamato 'npc'
        """Disegna un singolo NPC nell'area di gioco, con i suoi indicatori."""
        if not self.font_small: return

        # Calcola la posizione sullo schermo
        npc_screen_x, npc_screen_y = self._map_logical_to_screen(npc.logical_x, npc.logical_y)
        
        # Disegna il cerchio che rappresenta l'NPC
        npc_color = ui_config.NPC_GENDER_COLORS.get(npc.gender, ui_config.DEFAULT_NPC_COLOR)
        pygame.draw.circle(self.screen, npc_color, (npc_screen_x, npc_screen_y), self.effective_npc_radius)
        
        # Disegna un indicatore se un bisogno è critico
        has_critical_need = False
        # Usiamo 'npc' qui, che è il parametro ricevuto dal metodo
        for need in npc.needs.values(): 
            if need.get_value() <= npc_config.NEED_CRITICAL_THRESHOLD:
                has_critical_need = True
                break
        
        if has_critical_need:
            pygame.draw.circle(self.screen, ui_config.NPC_CRITICAL_NEED_INDICATOR_COLOR, (npc_screen_x, npc_screen_y), self.effective_npc_radius + 2, 3)
        
        # Disegna il cerchio di selezione
        if self.selected_npc_id == npc.npc_id:
            pygame.draw.circle(self.screen, self.SELECTION_COLOR, (npc_screen_x, npc_screen_y), self.effective_npc_radius, 2)

        # Disegna il nome dell'NPC
        text_surface = self.font_small.render(npc.name, True, self.current_contrast_color)
        text_rect = text_surface.get_rect(center=(npc_screen_x, npc_screen_y - self.effective_npc_radius - 10))
        self.screen.blit(text_surface, text_rect)

    def _draw_tilemap(self, location: 'Location'):
        """
        Disegna la mappa a mattonelle leggendo la mappa processata e scalando le tile.
        Include stampe di debug per trovare l'errore dello schermo nero.
        """
        # print("\n[Debug Tilemap] Avvio _draw_tilemap...")
        
        if not location.processed_tile_map:
            print("[Debug Tilemap] ERRORE: La 'processed_tile_map' della location è vuota! La logica in Location.__post_init__ potrebbe essere fallita.")
            return
        
        # print(f"[Debug Tilemap] Mappa processata trovata. Dimensioni: {len(location.processed_tile_map[0])}x{len(location.processed_tile_map)}")
        
        scaled_tile_size = int(self.tile_size * self.zoom_level)
        # print(f"[Debug Tilemap] Livello di zoom: {self.zoom_level:.2f}, Dimensione tile scalata: {scaled_tile_size}px")

        if scaled_tile_size <= 1:
            print("[Debug Tilemap] Uscita: tile troppo piccole per essere disegnate a questo livello di zoom.")
            return

        # Itera sulla mappa della location
        for y, row in enumerate(location.processed_tile_map):
            for x, tile_info in enumerate(row):
                tile_type = tile_info.get("type")
                variant_index = tile_info.get("variant_index", 0)

                if not tile_type or tile_type == TileType.EMPTY:
                    continue

                # Stampa di debug per ogni singola mattonella
                # print(f"  [Debug Tile] Cella ({x},{y}): Tipo={tile_type.name}, Variante={variant_index}")

                style_name = SHEET_DOORS if tile_type in (TileType.DOORWAY, TileType.DOOR_MAIN_ENTRANCE) else SHEET_FLOORS
                spritesheet = self.asset_manager.get_spritesheet(style_name)
                
                if not spritesheet:
                    print(f"    -> ERRORE: Spritesheet '{style_name}' non trovato nell'AssetManager!")
                    continue

                tile_def_or_list = graphics_config.TILE_DEFINITIONS.get(style_name, {}).get(tile_type)
                
                if not tile_def_or_list:
                    print(f"    -> ERRORE: Nessuna definizione trovata per {tile_type.name} in graphics_config.py!")
                    continue
                
                if isinstance(tile_def_or_list, list):
                    if variant_index >= len(tile_def_or_list):
                        print(f"    -> ERRORE: Indice variante {variant_index} fuori dai limiti per {tile_type.name}")
                        continue
                    chosen_def = tile_def_or_list[variant_index]
                else:
                    chosen_def = tile_def_or_list
                
                tile_rect_to_cut = pygame.Rect(chosen_def['rect'])
                # print(f"    -> OK! Uso lo spritesheet '{style_name}' e ritaglio il rettangolo: {tile_rect_to_cut}")

                try:
                    tile_image = spritesheet.subsurface(tile_rect_to_cut)
                    scaled_tile_image = pygame.transform.scale(tile_image, (scaled_tile_size, scaled_tile_size))
                    
                    screen_x, screen_y = self._map_logical_to_screen(x, y)
                    sprite_height = scaled_tile_image.get_height()
                    if sprite_height > scaled_tile_size:
                        screen_y -= (sprite_height - scaled_tile_size)

                    self.screen.blit(scaled_tile_image, (screen_x, screen_y))
                except ValueError as e:
                    print(f"    -> ERRORE PYGAME: Impossibile ritagliare o scalare lo sprite. {e}")

    def _get_npc_at_screen_pos(self, screen_pos: Tuple[int, int], simulation: 'Simulation') -> Optional['Character']:
        """
        Restituisce l'oggetto NPC che si trova in una data posizione dello schermo, se presente.
        """
        # Dobbiamo controllare solo gli NPC nella locazione attualmente visibile
        if not self.current_visible_location_id:
            return None
            
        location = simulation.get_location_by_id(self.current_visible_location_id)
        if not location:
            return None

        # Itera sugli NPC in ordine inverso di disegno (così becchiamo quello sopra)
        # se fossero sovrapposti. Per ora non è un problema.
        for npc_id in location.npcs_present_ids:
            npc = simulation.get_npc_by_id(npc_id)
            if not npc:
                continue

            # Calcola la posizione e l'area cliccabile dell'NPC sullo schermo
            npc_screen_x, npc_screen_y = self._map_logical_to_screen(npc.logical_x, npc.logical_y)
            radius = self.effective_npc_radius
            
            # Crea un rettangolo per il "bounding box" dell'NPC
            npc_rect = pygame.Rect(
                npc_screen_x - radius, 
                npc_screen_y - radius, 
                radius * 2, 
                radius * 2
            )
            
            # Controlla se il punto del mouse è dentro il rettangolo dell'NPC
            if npc_rect.collidepoint(screen_pos):
                return npc # Trovato! Restituisci questo NPC.
        
        return None # Nessun NPC trovato in quella posizione

    def _draw_game_object(self, game_obj: 'GameObject'):
        """Disegna un oggetto leggendo il suo stile."""
        # 1. Ottieni lo stile e il tipo dell'oggetto
        obj_style_name = game_obj.style
        obj_type = game_obj.object_type

        # 2. Trova la definizione dello sprite nello spritesheet corretto
        sprite_def = graphics_config.SPRITE_DEFINITIONS.get(obj_style_name, {}).get(obj_type)
        
        if not sprite_def: return # Non disegna nulla se non trova la definizione

        # 3. Ottieni lo spritesheet corretto dall'AssetManager
        spritesheet_surface = self.asset_manager.get_spritesheet(obj_style_name)
        if not spritesheet_surface: return

        # 3. Calcola dove disegnare l'oggetto sullo schermo
        screen_x, screen_y = self._map_logical_to_screen(game_obj.logical_x, game_obj.logical_y)
        
        # 4. L'area da "ritagliare" dallo spritesheet
        sprite_rect_to_cut = pygame.Rect(sprite_def['rect'])
        
        # 5. Disegna solo quella porzione dell'immagine sulla schermo
        #    La magia la fa il terzo argomento di blit (l'area)
        self.screen.blit(spritesheet_surface, (screen_x, screen_y), area=sprite_rect_to_cut)

        # Disegna il nome dell'oggetto se lo zoom è sufficiente (logica esistente)
        if self.font_debug and self.zoom_level >= 0.8:
            text = self.font_debug.render(f"{game_obj.name}", True, self.BLACK)
            text_rect = text.get_rect(center=(screen_x + sprite_rect_to_cut.width / 2, screen_y - 10))
            self.screen.blit(text, text_rect)

    def _draw_text_in_panel(self, text: str, x: int, y: int, font=None, color=None, max_width: Optional[int] = None) -> int:
        """
        Disegna testo nel pannello. Se max_width è specificato, il testo andrà a capo.
        Restituisce la coordinata y sotto l'ultima linea di testo disegnata.
        """
        if font is None: font = self.font_small
        if color is None: color = self.TEXT_COLOR
        
        if not font: return y # Non possiamo disegnare senza un font

        start_x_abs = self.base_width + x # Coordinata x assoluta sullo schermo

        if max_width is None: # Disegna una singola linea se max_width non è specificato
            text_surface = font.render(text, True, color)
            self.screen.blit(text_surface, (start_x_abs, y))
            return y + self.LINE_HEIGHT
        else: # Gestisci il wrapping
            words = text.split(' ')
            current_line_text = ""
            lines_rendered_count = 0

            for i, word in enumerate(words):
                separator = " " if current_line_text else ""
                test_line = current_line_text + separator + word
                
                test_line_width, _ = font.size(test_line)

                if test_line_width <= max_width or not current_line_text:
                    current_line_text = test_line
                else:
                    if current_line_text.strip():
                        line_surface = font.render(current_line_text.strip(), True, color)
                        self.screen.blit(line_surface, (start_x_abs, y))
                        lines_rendered_count +=1
                    y += self.LINE_HEIGHT
                    current_line_text = word # La nuova linea inizia con la parola corrente
            
            # Renderizza l'ultima linea rimasta
            if current_line_text.strip():
                line_surface = font.render(current_line_text.strip(), True, color)
                self.screen.blit(line_surface, (start_x_abs, y))
                lines_rendered_count +=1
            
            if lines_rendered_count > 0 :
                return y + self.LINE_HEIGHT
            elif text.strip(): # C'era testo, è stato disegnato su una linea senza wrapping
                return y + self.LINE_HEIGHT
            return y # Nessun testo disegnato (stringa vuota in input)

    def _render_wrapped_text_in_panel(self, text_to_wrap: str, x: int, y: int, max_width: int, font: pygame.font.Font, color: Tuple[int, int, int]) -> int:
        """
        Renderizza il testo nel pannello, andando a capo automaticamente.
        Restituisce la coordinata y sotto l'ultima linea di testo disegnata.
        """
        if not font: return y

        words = text_to_wrap.split(' ')
        current_line_text = ""
        start_x = self.base_width + x

        for word in words:
            # Prova ad aggiungere la parola alla linea corrente
            test_line = current_line_text + word + " "
            test_line_width, _ = font.size(test_line.strip()) # Calcola la larghezza senza lo spazio finale

            if test_line_width <= max_width:
                current_line_text = test_line
            else:
                # La parola corrente fa sforare la linea, quindi renderizza la linea precedente
                if current_line_text.strip(): # Evita di renderizzare linee vuote se la prima parola è troppo lunga
                    line_surface = font.render(current_line_text.strip(), True, color)
                    self.screen.blit(line_surface, (start_x, y))
                y += self.LINE_HEIGHT # Spostati alla linea successiva
                current_line_text = word + " " # La nuova linea inizia con la parola corrente
                # Se una singola parola è più lunga di max_width, verrà comunque disegnata su una linea
                # ma potrebbe sforare. Gestione avanzata del troncamento per singole parole lunghe
                # potrebbe essere aggiunta qui se necessario.
                
        # Renderizza l'ultima linea rimasta
        if current_line_text.strip():
            line_surface = font.render(current_line_text.strip(), True, color)
            self.screen.blit(line_surface, (start_x, y))
            y += self.LINE_HEIGHT
        
        return y

    def _lerp_color(self, color1: Tuple[int, int, int], color2: Tuple[int, int, int], factor: float) -> Tuple[int, int, int]:
        """Interpola linearmente (lerp) tra due colori RGB."""
        factor = max(0.0, min(1.0, factor))
        r = int(color1[0] * (1 - factor) + color2[0] * factor)
        g = int(color1[1] * (1 - factor) + color2[1] * factor)
        b = int(color1[2] * (1 - factor) + color2[2] * factor)
        return (r, g, b)

    def _get_interpolated_sky_color(self, time_manager: 'TimeManager') -> Tuple[int, int, int]:
        """
        Calcola il colore del cielo sfumato usando i keyframes di colore.
        """
        keyframes = ui_config.DAY_NIGHT_COLOR_KEYFRAMES
        sorted_hours = sorted(keyframes.keys())
        
        current_hour = time_manager.get_current_hour_float()
        
        # Trova i due keyframe (ore) tra cui si trova l'ora corrente
        start_hour = sorted_hours[0]
        end_hour = sorted_hours[-1]
        
        # Caso speciale per la notte che scavalca la mezzanotte
        if current_hour >= sorted_hours[-1]:
            start_hour = sorted_hours[-1]
            end_hour = sorted_hours[0] + time_config.HXD # Aggiunge 28 ore
        else:
            for i in range(len(sorted_hours) - 1):
                if sorted_hours[i] <= current_hour < sorted_hours[i+1]:
                    start_hour = sorted_hours[i]
                    end_hour = sorted_hours[i+1]
                    break
        
        # Normalizza l'ora corrente se la transizione scavalca la mezzanotte
        norm_current_hour = current_hour
        if end_hour > time_config.HXD and norm_current_hour < start_hour:
            norm_current_hour += time_config.HXD

        # Calcola il progresso (factor) tra i due keyframe
        phase_duration = end_hour - start_hour
        time_into_phase = norm_current_hour - start_hour
        progress = time_into_phase / phase_duration if phase_duration > 0 else 0
        
        # Prendi i colori corrispondenti ai keyframe
        start_color = keyframes[start_hour]
        end_color = keyframes[end_hour % time_config.HXD if end_hour >= time_config.HXD else end_hour] # Usa modulo per il wrap around

        # Interpola e restituisce il colore finale
        return self._lerp_color(start_color, end_color, progress)

    def _get_contrast_color(self, bg_color: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """
        Calcola un colore di testo ad alto contrasto (bianco o nero)
        per un dato colore di sfondo.
        """
        # Calcola la luminosità percepita del colore di sfondo
        luminance = (0.299 * bg_color[0] + 0.587 * bg_color[1] + 0.114 * bg_color[2])
        
        # Se la luminosità è alta (> 128), lo sfondo è "chiaro", quindi usiamo il testo nero.
        # Altrimenti, lo sfondo è "scuro", e usiamo il testo bianco.
        # Puoi usare i tuoi colori self.BLACK e self.WHITE se li hai definiti.
        return (0, 0, 0) if luminance > 128 else (255, 255, 255)

    def _get_need_bar_color(self, value: float) -> Tuple[int, int, int]:
        """
        Restituisce il colore corretto per la barra di un bisogno in base al suo valore.
        """
        if value <= 6.25:
            return ui_config.NEED_BAR_DARK_RED
        elif value <= 12.5:
            return ui_config.NEED_BAR_RED
        elif value <= 25:
            return ui_config.NEED_BAR_ORANGE
        elif value <= 50:
            return ui_config.NEED_BAR_YELLOW
        else: # > 50
            return ui_config.NEED_BAR_GREEN

    def _draw_text_and_get_surface(self, text: str, x: int, y: int, font=None, color=None, max_width=None) -> Optional[Surface]:
        """
        Disegna il testo sullo schermo e restituisce la superficie pygame creata.
        Gestisce il wrapping del testo se viene superata una larghezza massima.
        
        Args:
            text (str): Il testo da disegnare.
            x (int): La coordinata x di partenza.
            y (int): La coordinata y di partenza.
            font (pygame.Font, optional): Il font da usare. Usa il font di debug di default.
            color (Tuple[int,int,int], optional): Il colore del testo. Usa il bianco di default.
            max_width (int, optional): La larghezza massima prima di andare a capo.

        Returns:
            Optional[Surface]: La superficie pygame del testo (o dell'ultima riga di testo),
                                o None se il font non è disponibile.
        """
        # Se non vengono passati font o colori, usa quelli di default
        active_font = font or self.font_debug
        active_color = color or self.WHITE

        if not active_font: 
            return None

        # Gestisce il wrapping del testo se supera la larghezza massima
        if max_width and active_font.size(text)[0] > max_width:
            words = text.split(' ')
            lines = []
            current_line = ""
            for word in words:
                # Controlla se la nuova parola fa sforare la linea
                if active_font.size(current_line + " " + word)[0] <= max_width:
                    current_line += " " + word if current_line else word
                else:
                    # Vai a capo
                    lines.append(current_line)
                    current_line = word
            lines.append(current_line)
            
            # Disegna ogni linea e restituisce solo la superficie dell'ultima linea
            # per calcoli di posizione successivi, se necessari.
            text_surface = None
            for i, line in enumerate(lines):
                text_surface = active_font.render(line, True, active_color)
                self.screen.blit(text_surface, (x, y + i * self.LINE_HEIGHT))
            return text_surface
        
        else:
            # Disegna il testo in una sola riga
            text_surface = active_font.render(text, True, active_color)
            self.screen.blit(text_surface, (x, y))
            return text_surface

    def _render_gui(self, simulation: Optional['Simulation']):
        # --- 1. PREPARAZIONE E CALCOLO COLORI ---
        # Calcoliamo i colori dinamici una sola volta all'inizio del frame.
        bg_color = ui_config.DEFAULT_DAY_BG_COLOR
        # Impostiamo un colore di contrasto di default
        self.current_contrast_color = self.WHITE 
        
        if simulation and simulation.time_manager:
            bg_color = self._get_interpolated_sky_color(simulation.time_manager)
            self.current_contrast_color = self._get_contrast_color(bg_color)
        
        # Pulizia dello schermo con un colore di fondo generico per l'area di gioco
        game_area_rect = pygame.Rect(0, 0, self.base_width, self.height)
        self.screen.fill(bg_color, game_area_rect)

        # --- 2. LOGICA DI SELEZIONE (senza disegnare nulla) ---
        npc_to_display_in_panel: Optional['Character'] = None
        current_location_instance: Optional['Location'] = None
        current_sim_time = None

        if simulation and simulation.time_manager:
            current_sim_time = simulation.time_manager.get_current_time()
            if self.current_visible_location_id:
                current_location_instance = simulation.get_location_by_id(self.current_visible_location_id)
            if self.selected_npc_id:
                npc_to_display_in_panel = simulation.get_npc_by_id(self.selected_npc_id)

        # --- 3. DISEGNO DEL MONDO (SFONDO, OGGETTI, NPC) ---
        if current_location_instance:
            # 3a. Disegna lo sfondo (pavimento/muri) usando la cache
            cache_key = (current_location_instance.location_id, self.zoom_level)
            background_surface = self.background_cache.get(cache_key)
            if background_surface is None:
                background_surface = self._create_static_background(current_location_instance, self.zoom_level)
                self.background_cache[cache_key] = background_surface
            
            self.screen.blit(background_surface, (-self.camera_offset_x, -self.camera_offset_y))

            # 3b. Disegna gli elementi dinamici (oggetti e NPC) sopra lo sfondo
            if simulation:
                for game_obj in current_location_instance.get_objects():
                    self._draw_game_object(game_obj)
                for npc_id in current_location_instance.npcs_present_ids:
                    npc_in_loc = simulation.get_npc_by_id(npc_id)
                    if npc_in_loc:
                        self._draw_npc(npc_in_loc)
        
        # --- 4. DISEGNO DEL PANNELLO LATERALE ---
        panel_rect = pygame.Rect(self.base_width, 0, self.PANEL_WIDTH, self.height)
        self.screen.fill(self.PANEL_BG_COLOR, panel_rect)
        pygame.draw.line(self.screen, self.BLACK, (self.base_width, 0), (self.base_width, self.height), 2)
        
        panel_padding = 10
        current_y = panel_padding

        # Blocco Data e Ora
        if simulation and simulation.time_manager:
            current_sim_time = simulation.time_manager.get_current_time()
            date_str = current_sim_time.format("D, Y, d/m (F)")
            time_str = current_sim_time.format("G:i")
            current_y = self._draw_text_in_panel(date_str, panel_padding, current_y, font=self.font_small, color=self.WHITE)
            current_y = self._draw_text_in_panel(time_str, panel_padding, current_y, font=self.font_medium_bold, color=self.WHITE)
        current_y += self.LINE_HEIGHT # Linea vuota

        # Blocco Info Locazione
        if current_location_instance:
            loc_name = current_location_instance.name
            current_y = self._draw_text_in_panel(loc_name, panel_padding, current_y, font=self.font_small, color=self.WHITE)
            
            # Riga opzionale
            num_npcs = len(current_location_instance.npcs_present_ids)
            num_objs = len(current_location_instance.get_objects())
            cam_off = f"({self.camera_offset_x:.0f},{self.camera_offset_y:.0f})"
            current_y = self._draw_text_in_panel(f"NPCs: {num_npcs}, Oggetti: {num_objs}, Cam: {cam_off}", panel_padding, current_y, font=self.font_small, color=self.WHITE)
        current_y += self.LINE_HEIGHT # Linea vuota

        # Blocco Dettagli NPC
        if npc_to_display_in_panel and current_sim_time:
            npc = npc_to_display_in_panel

            # --- Blocco Nome, Età, Azione ---
            name_surface = self.font_large.render(npc.name, True, self.WHITE)
            self.screen.blit(name_surface, (self.base_width + panel_padding, current_y))
            name_surface = self.font_large.render(npc.name, True, self.WHITE)
            self.screen.blit(name_surface, (self.base_width + panel_padding, current_y))
            gender_color = ui_config.NPC_GENDER_COLORS.get(
                npc.gender, 
                ui_config.NPC_GENDER_COLORS[Gender.UNKNOWN]
            )

            # Simbolo del genere accanto al nome
            gender_symbol_rect = pygame.Rect(
                self.base_width + panel_padding + name_surface.get_width() + 8, 
                current_y + 8, 
                10, 
                10
            )
            pygame.draw.rect(self.screen, gender_color, gender_symbol_rect)
            current_y += self.LINE_HEIGHT

            # DATA DI NASCITA E ETÀ
            birth_date_str = npc.birth_date.format("Y, d/m")
            lifestage_str = npc.life_stage.display_name_it(npc.gender) if npc.life_stage else "N/D"
            current_y = self._draw_text_in_panel(f"Nato/a il: {birth_date_str}", panel_padding, current_y, font=self.font_small)
            current_y = self._draw_text_in_panel(f"Età: {lifestage_str}", panel_padding, current_y, font=self.font_small)
            current_y += self.LINE_HEIGHT # Linea vuota

            # AZIONE
            action_str = f"Azione: {npc.current_action.action_type_name}" if npc.current_action else "Azione: Inattivo"
            current_y = self._draw_text_in_panel(action_str, panel_padding, current_y, font=self.font_small, max_width=self.PANEL_WIDTH - panel_padding * 2)
            current_y += self.LINE_HEIGHT # Linea vuota

            # --- Blocco Personalità ---
            current_y = self._draw_text_in_panel("Personalità", panel_padding, current_y, font=self.font_medium_bold)
            trait_str = ", ".join(sorted([t.display_name for t in npc.traits.values()]))
            current_y = self._draw_text_in_panel(f"Tratti: {trait_str}", panel_padding + 10, current_y, font=self.font_small, max_width=self.PANEL_WIDTH - panel_padding*2-10)
            asp_str = npc.aspiration.display_name_it(npc.gender) if npc.aspiration else "Nessuna"
            current_y = self._draw_text_in_panel(f"Aspirazione: {asp_str}", panel_padding + 10, current_y, font=self.font_small, max_width=self.PANEL_WIDTH - panel_padding*2-10)
            interest_str = ", ".join(sorted([i.display_name_it(npc.gender) for i in npc.get_interests()]))
            current_y = self._draw_text_in_panel(f"Interessi: {interest_str}", panel_padding + 10, current_y, font=self.font_small, max_width=self.PANEL_WIDTH - panel_padding*2-10)
            current_y += self.LINE_HEIGHT # Linea vuota

            # --- Blocco Stato Emotivo e Bisogni ---
            emotional_state_str = npc.moodlet_manager.get_dominant_emotion_display_name(npc.gender)
            current_y = self._draw_text_in_panel(f"Stato Emotivo: {emotional_state_str}", panel_padding, current_y, font=self.font_small)
            current_y += self.LINE_HEIGHT # Linea vuota

            current_y = self._draw_text_in_panel("Bisogni", panel_padding, current_y, font=self.font_medium_bold)
            
            if npc.needs:
                bar_x = self.base_width + panel_padding
                bar_max_width = self.PANEL_WIDTH - panel_padding * 2
                bar_height = self.font_small.get_height() + 2 # Altezza barra basata sul font

                for need_type, need_obj in sorted(npc.needs.items(), key=lambda item: item[0].name):
                    value = need_obj.get_value()
                    bar_color = self._get_need_bar_color(value)
                    bar_current_width = int((value / npc_config.NEED_MAX_VALUE) * bar_max_width)
                    
                    # Disegna lo sfondo della barra
                    bg_rect = pygame.Rect(bar_x, current_y, bar_max_width, bar_height)
                    pygame.draw.rect(self.screen, (50, 50, 50), bg_rect)
                    
                    # Disegna la barra colorata
                    if bar_current_width > 0:
                        fill_rect = pygame.Rect(bar_x, current_y, bar_current_width, bar_height)
                        pygame.draw.rect(self.screen, bar_color, fill_rect)
                    
                    # Disegna il testo SOPRA la barra
                    need_name_str = need_obj.get_display_name(npc.gender)
                    text_surface = self.font_small.render(need_name_str, True, self.WHITE)
                    # Centra verticalmente il testo nella barra
                    text_rect = text_surface.get_rect(centery=bg_rect.centery)
                    text_rect.left = bg_rect.left + 5 # Con un piccolo padding
                    self.screen.blit(text_surface, text_rect)
                    
                    current_y += bar_height + 4 # Avanza alla riga successiva
        else:
            current_y = self._draw_text_in_panel("Nessun NPC selezionato.", panel_padding, current_y)

        # --- 5. DISEGNO ELEMENTI SOVRAPPOSTI (TOOLTIP, FPS) ---
        tooltip_text = None
        if self.hovered_npc:
            tooltip_text = self.hovered_npc.name
        elif self.hovered_object:
            tooltip_text = self.hovered_object.name

        if tooltip_text and self.font_debug:
            text_surface = self.font_debug.render(tooltip_text, True, self.BLACK)
            text_rect = text_surface.get_rect()
            tooltip_bg_rect = pygame.Rect(
                text_rect.left - 5, text_rect.top - 3,
                text_rect.width + 10, text_rect.height + 6
            )
            mouse_pos = pygame.mouse.get_pos()
            tooltip_bg_rect.topleft = (mouse_pos[0] + 15, mouse_pos[1] + 10)
            
            pygame.draw.rect(self.screen, self.WHITE, tooltip_bg_rect)
            pygame.draw.rect(self.screen, self.BLACK, tooltip_bg_rect, 1)
            self.screen.blit(text_surface, (tooltip_bg_rect.left + 5, tooltip_bg_rect.top + 3))
        
        if settings.DEBUG_MODE and self.font_debug:
            fps_text = self.font_debug.render(f"FPS: {self.clock.get_fps():.2f}", True, self.BLACK)
            self.screen.blit(fps_text, (10, 10)) 

        # --- 6. AGGIORNAMENTO FINALE DELLO SCHERMO ---
        pygame.display.flip()

    def run_game_loop(self, simulation: Optional['Simulation']):
        if not simulation: return

        # --- CONFIGURAZIONE DEL TEMPO ---
        # Calcoliamo quanti nanosecondi reali dura un singolo tick della simulazione.
        # Questo valore rimane costante.
        ns_per_tick = (time_config.TICK_RATE_DENOMINATOR * time_config.NANOSECONDS_PER_SECOND) // time_config.TICK_RATE_NUMERATOR
        
        # L'accumulatore parte da zero.
        lag_accumulator_ns = 0
        last_frame_ns = time.monotonic_ns()

        self.is_running = True
        simulation.is_running = True
        
        while self.is_running:
            # 1. GESTIONE INPUT (invariato)
            self._handle_events(simulation)

            # --- 2. LOGICA DI AGGIORNAMENTO TEMPO ---
            current_ns = time.monotonic_ns()
            elapsed_ns = current_ns - last_frame_ns
            last_frame_ns = current_ns
            lag_accumulator_ns += elapsed_ns

            # 3. CICLO DI SIMULAZIONE
            # Esegui la logica della simulazione finché non abbiamo "recuperato" il tempo reale trascorso.
            ticks_processed_this_frame = 0
            while lag_accumulator_ns >= ns_per_tick:
                if simulation.is_running:
                    # Fai avanzare la simulazione di UN tick alla volta
                    simulation._update_simulation_state(ticks_to_process=1)
                
                # Sottrai il tempo di un tick dall'accumulatore
                lag_accumulator_ns -= ns_per_tick
                ticks_processed_this_frame += 1

                # Limite di sicurezza per evitare la "spirale della morte"
                if ticks_processed_this_frame >= time_config.MAX_TICKS_PER_FRAME:
                    # Se il gioco è troppo indietro, evita di bloccarlo resettando l'accumulatore
                    lag_accumulator_ns = 0 
                    break
            
            # 4. DISEGNO GRAFICA
            # Il disegno avviene sempre, una volta per frame, indipendentemente da quanti tick sono stati processati
            self._render_gui(simulation)
            
            # Limita l'FPS per non sprecare CPU, ma non influisce sulla velocità del tempo di gioco
            self.clock.tick(settings.FPS)

        self._quit_pygame()

    def _create_static_background(self, location: 'Location', zoom: float) -> Surface:
        """
        Crea e restituisce una singola superficie statica con l'intera mappa
        di mattonelle già disegnata e scalata per il livello di zoom corrente.
        """
        print(f"  [Renderer CACHE] Creo nuovo sfondo per '{location.name}' a zoom {zoom:.2f}x")
        
        scaled_tile_size = int(self.tile_size * zoom)
        
        map_width_px = location.logical_width * scaled_tile_size
        map_height_px = location.logical_height * scaled_tile_size
        
        background_surface = pygame.Surface((map_width_px, map_height_px), pygame.SRCALPHA)

        if scaled_tile_size <= 1: return background_surface

        for y, row in enumerate(location.processed_tile_map):
            for x, tile_info in enumerate(row):
                tile_type = tile_info.get("type")
                variant_index = tile_info.get("variant_index", 0)

                if not tile_type or tile_type == TileType.EMPTY:
                    continue

                # 1. Determina quale spritesheet usare
                style_name = SHEET_DOORS if tile_type in (TileType.DOORWAY, TileType.DOOR_MAIN_ENTRANCE) else SHEET_FLOORS
                spritesheet = self.asset_manager.get_spritesheet(style_name)

                # 2. Ora cerca la definizione della mattonella
                tile_def_or_list = graphics_config.TILE_DEFINITIONS.get(style_name, {}).get(tile_type)

                # 3. Solo adesso controlla se abbiamo trovato tutto il necessario
                if not tile_def_or_list or not spritesheet:
                    continue

                if isinstance(tile_def_or_list, list):
                    chosen_def = tile_def_or_list[variant_index]
                else:
                    chosen_def = tile_def_or_list
                
                try:
                    tile_rect_to_cut = pygame.Rect(chosen_def['rect'])
                    tile_image = spritesheet.subsurface(tile_rect_to_cut)
                    scaled_tile_image = pygame.transform.scale(tile_image, (scaled_tile_size, scaled_tile_size))
                    
                    dest_x = x * scaled_tile_size
                    dest_y = y * scaled_tile_size
                    
                    sprite_height_scaled = scaled_tile_image.get_height()
                    if sprite_height_scaled > scaled_tile_size:
                        dest_y -= (sprite_height_scaled - scaled_tile_size)

                    background_surface.blit(scaled_tile_image, (dest_x, dest_y))
                except ValueError as e:
                    print(f"  [Renderer ERROR] Errore nel processare la tile {tile_type.name}: {e}")
        
        return background_surface



    def _quit_pygame(self):
        if settings.DEBUG_MODE:
            print(f"  [Renderer] Chiusura Pygame...")
        pygame.font.quit() 
        pygame.quit()
