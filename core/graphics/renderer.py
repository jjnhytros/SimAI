# core/graphics/renderer.py
"""
Gestisce l'inizializzazione di Pygame, la finestra di gioco e il loop di rendering principale.
Riferimento TODO: I.1
"""
import pygame
from typing import Optional, TYPE_CHECKING, List, Tuple # Aggiunto Tuple per type hint

from core import settings
from core.config import ui_config
from core.enums import Gender, ObjectType 

if TYPE_CHECKING:
    from core.simulation import Simulation
    from core.character import Character
    from core.world.game_object import GameObject
    from core.world.location import Location

class Renderer:
    TILE_SIZE = 32 
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
        pygame.font.init()

        self.base_width = width
        self.base_height = height
        self.width = self.base_width + self.PANEL_WIDTH 
        self.height = self.base_height
        self.screen_size = (self.width, self.height)
        
        display_flags = pygame.RESIZABLE 
        self.screen = pygame.display.set_mode(self.screen_size, display_flags)
        pygame.display.set_caption(caption)

        self.clock = pygame.time.Clock()
        self.is_running = False

        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GREY = (128, 128, 128)
        self.RED_OBJ = (200, 0, 0)

        try:
            self.font_debug = pygame.font.Font(None, 22)
            self.font_panel_title = pygame.font.Font(None, 28)
            self.font_panel_text = pygame.font.Font(None, 20)
            common_system_font_name = "arial"
            try:
                self.font_main = pygame.font.SysFont(common_system_font_name, 48)
            except pygame.error:
                if settings.DEBUG_MODE:
                    print(f"  [Renderer WARN] Font di sistema '{common_system_font_name}' non trovato.")
                self.font_main = pygame.font.Font(None, 48)
        except pygame.error as e:
            if settings.DEBUG_MODE:
                print(f"  [Renderer ERROR] Errore imprevisto inizializzazione font: {e}.")
            self.font_debug = pygame.font.Font(None, 22)
            self.font_panel_title = pygame.font.Font(None, 28)
            self.font_panel_text = pygame.font.Font(None, 20)
            self.font_main = pygame.font.Font(None, 48)

        self.current_visible_location_id: Optional[str] = None
        self.location_keys_list: List[str] = []
        self.current_location_index: int = 0
        
        self.camera_offset_x: int = 0
        self.camera_offset_y: int = 0
        self.selected_npc_id: Optional[str] = None
        self.zoom_level: float = 1.0

        if settings.DEBUG_MODE:
            print(f"  [Renderer] Inizializzato Pygame con finestra {self.width}x{self.height} (Area gioco: {self.base_width}x{self.base_height}, Pannello: {self.PANEL_WIDTH}x{self.base_height})")

    @property
    def effective_tile_size(self) -> float:
        return self.TILE_SIZE * self.zoom_level

    @property
    def effective_npc_radius(self) -> int:
        base_radius = self.TILE_SIZE / 2 - 3 
        return max(2, int(base_radius * self.zoom_level))

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

    def _handle_events(self, simulation: Optional['Simulation']):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            elif event.type == pygame.MOUSEWHEEL:
                self.zoom_level += event.y * 0.1
                self.zoom_level = max(self.MIN_ZOOM, min(self.zoom_level, self.MAX_ZOOM))
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

    def _draw_npc(self, character: 'Character'):
        if character.logical_x is None or character.logical_y is None:
            return 
        npc_screen_x, npc_screen_y = self._map_logical_to_screen(float(character.logical_x), float(character.logical_y))
        npc_color = ui_config.NPC_GENDER_COLORS.get(character.gender, ui_config.DEFAULT_NPC_COLOR)
        
        current_radius = self.effective_npc_radius
        pygame.draw.circle(self.screen, npc_color, (npc_screen_x, npc_screen_y), current_radius)

        is_selected = self.selected_npc_id == character.npc_id
        has_critical_need = False
        if character.needs: 
            for need in character.needs.values():
                if hasattr(settings, 'NEED_CRITICAL_THRESHOLD') and \
                   need.get_value() <= settings.NEED_CRITICAL_THRESHOLD:
                    has_critical_need = True
                    break
        
        if is_selected:
            pygame.draw.circle(self.screen, self.SELECTION_BORDER_COLOR, (npc_screen_x, npc_screen_y), current_radius + 2, self.SELECTION_BORDER_WIDTH)
        elif has_critical_need: 
            pygame.draw.circle(self.screen, ui_config.NPC_CRITICAL_NEED_INDICATOR_COLOR, (npc_screen_x, npc_screen_y), current_radius, 3)
        
        if self.font_debug and self.zoom_level >= 0.7: # Mostra nome se lo zoom è sufficiente
            name_surface = self.font_debug.render(character.name, True, self.BLACK)
            name_rect = name_surface.get_rect(center=(npc_screen_x, npc_screen_y + current_radius + int(10 * self.zoom_level)))
            self.screen.blit(name_surface, name_rect)

    def _draw_game_object(self, game_obj: 'GameObject'):
        if game_obj.logical_x is None or game_obj.logical_y is None:
            return
        obj_screen_x, obj_screen_y = self._map_logical_to_screen(float(game_obj.logical_x), float(game_obj.logical_y))
        effective_obj_size_padding = max(1, int(4 * self.zoom_level))
        obj_width = self.effective_tile_size - effective_obj_size_padding 
        obj_height = self.effective_tile_size - effective_obj_size_padding
        
        obj_width = max(1, int(obj_width))
        obj_height = max(1, int(obj_height))

        obj_rect = pygame.Rect(obj_screen_x - obj_width // 2, obj_screen_y - obj_height // 2, obj_width, obj_height)
        obj_color = ui_config.GAME_OBJECT_TYPE_COLORS.get(game_obj.object_type, ui_config.DEFAULT_GAME_OBJECT_COLOR)
        pygame.draw.rect(self.screen, obj_color, obj_rect)
        
        if game_obj.is_water_source:
             pygame.draw.rect(self.screen, self.BLACK, obj_rect, max(1,int(2 * self.zoom_level)))
        
        if self.font_debug and self.zoom_level >= 0.8:
            display_name = game_obj.name if len(game_obj.name) < 15 else game_obj.object_type.name
            name_surface = self.font_debug.render(display_name, True, self.BLACK)
            name_rect = name_surface.get_rect(center=(obj_screen_x, obj_screen_y + obj_height // 2 + int(10 * self.zoom_level)))
            self.screen.blit(name_surface, name_rect)
    def _draw_text_in_panel(self, text: str, x: int, y: int, font=None, color=None, max_width: Optional[int] = None) -> int:
        """
        Disegna testo nel pannello. Se max_width è specificato, il testo andrà a capo.
        Restituisce la coordinata y sotto l'ultima linea di testo disegnata.
        """
        if font is None: font = self.font_panel_text
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

    def _render_gui(self, simulation: Optional['Simulation']):
        game_area_rect = pygame.Rect(0, 0, self.base_width, self.base_height)
        self.screen.fill(self.GREY, game_area_rect)

        panel_rect = pygame.Rect(self.base_width, 0, self.PANEL_WIDTH, self.height)
        self.screen.fill(self.PANEL_BG_COLOR, panel_rect)
        pygame.draw.line(self.screen, self.BLACK, (self.base_width, 0), (self.base_width, self.height), 2)

        panel_padding = 10
        text_indent = panel_padding + 15 # Indentazione per i valori dopo le etichette
        value_max_width = self.PANEL_WIDTH - text_indent - panel_padding # Max larghezza per i valori wrappati

        current_y = panel_padding
        
        npc_to_display_in_panel: Optional['Character'] = None
        current_location_instance_for_panel: Optional['Location'] = None

        if simulation:
            if self.current_visible_location_id:
                current_location_instance_for_panel = simulation.get_location_by_id(self.current_visible_location_id)

            if self.selected_npc_id:
                npc_to_display_in_panel = simulation.get_npc_by_id(self.selected_npc_id)
                if npc_to_display_in_panel and npc_to_display_in_panel.current_location_id != self.current_visible_location_id:
                    npc_to_display_in_panel = None 
            
            if npc_to_display_in_panel is None and current_location_instance_for_panel and current_location_instance_for_panel.npcs_present_ids:
                first_npc_id_in_loc = next(iter(current_location_instance_for_panel.npcs_present_ids), None)
                if first_npc_id_in_loc:
                    npc_to_display_in_panel = simulation.get_npc_by_id(first_npc_id_in_loc)
            
            if current_location_instance_for_panel:
                for game_obj in current_location_instance_for_panel.get_objects():
                    self._draw_game_object(game_obj)
                for npc_id_in_loc in current_location_instance_for_panel.npcs_present_ids:
                    npc_in_loc = simulation.get_npc_by_id(npc_id_in_loc)
                    if npc_in_loc:
                        self._draw_npc(npc_in_loc)
            
        current_y = self._draw_text_in_panel("Info Panel", panel_padding, current_y, font=self.font_panel_title, color=self.WHITE)
        current_y += 5
        
        # --- INIZIO BLOCCO DATA/ORA CON DEBUG DETTAGLIATO ---
        if simulation and simulation.time_manager:
            if self.font_debug: # Assicurati prima che il font esista
                datetime_info = simulation.time_manager.get_ath_detailed_datetime()
                year_val = int(datetime_info.get('year', 0))
                day_val = int(datetime_info.get('day_of_month', 0))
                month_name_val = str(datetime_info.get('month_name', "N/D"))
                hour_val = int(datetime_info.get('hour', 0))
                minute_val = int(datetime_info.get('minute', 0))
                day_name_val = str(datetime_info.get('day_name', "N/D"))
                
                datetime_str = f"{day_name_val}, {day_val} {month_name_val} {year_val:04d} - {hour_val:02d}:{minute_val:02d}"

                # Variabili per il posizionamento
                target_x_coord = self.base_width + panel_padding
                target_y_coord = current_y

                # --- STAMPE DI DEBUG CRUCIALI ---
                if settings.DEBUG_MODE:
                    print(f"--- DEBUG DATETIME DRAW ---")
                    print(f"datetime_str: '{datetime_str}'")
                    print(f"self.font_debug: {self.font_debug} (Tipo: {type(self.font_debug)})")
                    print(f"self.base_width: {self.base_width} (Tipo: {type(self.base_width)})")
                    print(f"panel_padding: {panel_padding} (Tipo: {type(panel_padding)})")
                    print(f"current_y (prima del blit): {current_y} (Tipo: {type(current_y)})")
                    print(f"Coordinate calcolate per blit (target_x_coord, target_y_coord): ({target_x_coord}, {target_y_coord})")
                # --- FINE STAMPE DI DEBUG ---

                try:
                    # Assicurati che le coordinate siano esplicitamente intere
                    final_blit_x = int(target_x_coord)
                    final_blit_y = int(target_y_coord)

                    dt_text_surface = self.font_debug.render(datetime_str, True, self.WHITE)
                    self.screen.blit(dt_text_surface, (final_blit_x, final_blit_y))
                    current_y += self.LINE_HEIGHT 
                except Exception as e:
                    if settings.DEBUG_MODE:
                        print(f"  [Renderer EXCEPTION] Eccezione nel blocco DATETIME: {e}")
                        # Stampa lo stato delle variabili anche in caso di eccezione
                        print(f"    DEBUG EXCEPTION - datetime_str: '{datetime_str}'")
                        print(f"    DEBUG EXCEPTION - self.font_debug: {self.font_debug}")
                        print(f"    DEBUG EXCEPTION - target_x_coord: {target_x_coord}, target_y_coord: {target_y_coord}")

            else: # Caso in cui self.font_debug è None
                if settings.DEBUG_MODE:
                    print(f"  [Renderer ERROR] self.font_debug è None. Impossibile renderizzare datetime_str.")
                # Potresti voler disegnare un placeholder o semplicemente avanzare current_y
                current_y += self.LINE_HEIGHT 

        # --- FINE BLOCCO DATA/ORA CON DEBUG DETTAGLIATO ---

        if current_location_instance_for_panel:
            loc_name = current_location_instance_for_panel.name
            num_npcs = len(current_location_instance_for_panel.npcs_present_ids)
            num_objs = len(current_location_instance_for_panel.get_objects())
            cam_off = f"({self.camera_offset_x:.1f},{self.camera_offset_y:.1f})" # Mostra float per offset
            current_y = self._draw_text_in_panel(f"Loc: {loc_name}", panel_padding, current_y, font=self.font_debug, color=self.WHITE)
            current_y = self._draw_text_in_panel(f"  NPCs: {num_npcs}, Oggetti: {num_objs}, Cam: {cam_off}", panel_padding, current_y, font=self.font_debug, color=self.WHITE)
        elif self.current_visible_location_id:
            current_y = self._draw_text_in_panel(f"Loc ID: {self.current_visible_location_id} (Non Trovata!)", panel_padding, current_y, font=self.font_debug, color=self.RED_OBJ)
        else:
            current_y = self._draw_text_in_panel("Nessuna locazione selezionata.", panel_padding, current_y, font=self.font_debug, color=self.WHITE)
        current_y += self.LINE_HEIGHT 

        if npc_to_display_in_panel:
            npc = npc_to_display_in_panel
            current_y = self._draw_text_in_panel(f"NPC Sel: {npc.name}", panel_padding, current_y, font=self.font_panel_title)
            
            age_str = f"{npc.get_age_in_years_float():.1f} anni"
            gender_str = npc.gender.display_name_it() if npc.gender else "N/D"
            lifestage_str = npc.life_stage.display_name_it() if npc.life_stage else "N/D"
            current_y = self._draw_text_in_panel(f"  {gender_str}, {age_str} ({lifestage_str})", panel_padding, current_y)
            current_y += 5

            if npc.current_action:
                action_name = npc.current_action.action_type_name
                progress = npc.current_action.get_progress_percentage()
                action_info_str = f"  Azione: {action_name} ({progress:.0f}%)"
                # Qui potremmo usare il wrapping se action_name è molto lungo
                current_y = self._draw_text_in_panel(action_info_str, panel_padding, current_y, max_width=self.PANEL_WIDTH - panel_padding * 2)
            else:
                current_y = self._draw_text_in_panel("  Azione: Idle", panel_padding, current_y)
            current_y += 5

            current_y = self._draw_text_in_panel("Personalità:", panel_padding, current_y, font=self.font_debug, color=self.WHITE)
            
            trait_display_names = [trait_obj.display_name for trait_obj in npc.traits.values()]
            trait_str = ", ".join(sorted(trait_display_names)) if trait_display_names else "Nessuno"
            # Utilizzo del metodo di wrapping per i tratti
            current_y = self._draw_text_in_panel("  Tratti: " + trait_str, panel_padding, current_y, max_width=self.PANEL_WIDTH - panel_padding * 2)

            asp_name = npc.aspiration.display_name_it() if npc.aspiration else "Nessuna"
            asp_prog = npc.aspiration_progress
            # Utilizzo del metodo di wrapping per l'aspirazione
            current_y = self._draw_text_in_panel(f"  Aspirazione: {asp_name} ({asp_prog:.0%})", panel_padding, current_y, max_width=self.PANEL_WIDTH - panel_padding * 2)
            
            interest_names = [i.name.replace("_", " ").title() for i in npc.get_interests()]
            interest_str = ", ".join(sorted(interest_names)) if interest_names else "Nessuno"
            # Utilizzo del metodo di wrapping per gli interessi
            current_y = self._draw_text_in_panel(f"  Interessi: {interest_str}", panel_padding, current_y, max_width=self.PANEL_WIDTH - panel_padding * 2)
            current_y += self.LINE_HEIGHT

            current_y = self._draw_text_in_panel("Bisogni:", panel_padding, current_y, font=self.font_debug, color=self.WHITE)
            if npc.needs:
                for need_type, need_obj in sorted(npc.needs.items(), key=lambda item: item[0].name):
                    val_str = f"{need_obj.get_value():.0f}"
                    need_ui_info = ui_config.NEED_UI_CONFIG.get(need_type, {})
                    need_color_name = need_ui_info.get("color_pygame", "white") # Assumiamo 'color_pygame'
                    try: bar_fill_color = pygame.Color(need_color_name)
                    except ValueError: bar_fill_color = pygame.Color(self.WHITE) 
                    
                    bar_x = self.base_width + panel_padding + 85
                    bar_max_width = self.PANEL_WIDTH - panel_padding * 2 - 90
                    bar_current_width = int((need_obj.get_value() / settings.NEED_MAX_VALUE) * bar_max_width)
                    bar_height = self.LINE_HEIGHT - 8
                    bar_y_offset = current_y + 4
                    
                    pygame.draw.rect(self.screen, (80,80,80), (bar_x, bar_y_offset, bar_max_width, bar_height))
                    if bar_current_width > 0 : pygame.draw.rect(self.screen, bar_fill_color, (bar_x, bar_y_offset, bar_current_width, bar_height))
                    current_y = self._draw_text_in_panel(f"    {need_obj.get_display_name()}: {val_str}", panel_padding, current_y)
            else:
                 current_y = self._draw_text_in_panel("    (Nessun bisogno definito)", panel_padding, current_y)
        elif self.font_debug:
            current_y = self._draw_text_in_panel("Nessun NPC selezionato.", panel_padding, current_y)
        else: 
            if self.font_main:
                text_surface = self.font_main.render("SimAI - GUI (Nessuna Simulazione)", True, self.BLACK)
                text_rect = text_surface.get_rect(center=(self.width // 2, self.height // 2))
                self.screen.blit(text_surface, text_rect)

        if settings.DEBUG_MODE and self.font_debug:
            fps_text = self.font_debug.render(f"FPS: {self.clock.get_fps():.2f}", True, self.BLACK)
            self.screen.blit(fps_text, (10, 10)) 
            
        pygame.display.flip()

    def run_game_loop(self, simulation: Optional['Simulation'] = None):
        if settings.DEBUG_MODE:
            print(f"  [Renderer] Avvio Game Loop Pygame...")
        if simulation and simulation.locations:
            self.location_keys_list = sorted(list(simulation.locations.keys()))
            if self.location_keys_list:
                self.current_location_index = 0
                self.current_visible_location_id = self.location_keys_list[self.current_location_index]
                # if settings.DEBUG_MODE:
                #     print(f"  [Renderer Loop Start] Visualizzazione iniziale locazione: {self.current_visible_location_id}")
        else:
            self.location_keys_list = []
            self.current_visible_location_id = None
        
        self.is_running = True
        while self.is_running:
            self._handle_events(simulation)
            self._update_game_state(simulation) 
            self._render_gui(simulation)
            
            # Usa FPS da settings se disponibile, altrimenti default
            fps_to_use = settings.FPS if hasattr(settings, 'FPS') else 60
            self.clock.tick(fps_to_use) 
        self._quit_pygame()

    def _quit_pygame(self):
        if settings.DEBUG_MODE:
            print(f"  [Renderer] Chiusura Pygame...")
        pygame.font.quit() 
        pygame.quit()
