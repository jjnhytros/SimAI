# core/graphics/renderer.py
"""
Gestisce l'inizializzazione di Pygame, la finestra di gioco e il loop di rendering principale.
Riferimento TODO: I.1
"""
import pygame
from typing import Optional, TYPE_CHECKING, List

from core import settings
from core.config import ui_config
from core.enums import Gender, ObjectType

if TYPE_CHECKING:
    from core.simulation import Simulation
    from core.character import Character
    from core.world.game_object import GameObject
    from core.world.location import Location

class Renderer:
    TILE_SIZE = 32 # Dimensione di una "cella" logica in pixel (esempio)
    PANEL_WIDTH = 300 # Larghezza del pannello informativo
    TEXT_COLOR = (230, 230, 230) # Colore testo quasi bianco per il pannello
    PANEL_BG_COLOR = (40, 40, 60) # Colore di sfondo per il pannello (blu scuro/grigio)
    LINE_HEIGHT = 20 # Altezza linea per il testo nel pannello
    NPC_RADIUS = TILE_SIZE // 2 - 3 # Raggio NPC per disegno e click
    SELECTION_BORDER_COLOR = (255, 255, 0) # Giallo per selezione
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
        self.GREEN_OBJ = (0, 180, 0)
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
        # Assicurati che il raggio non diventi troppo piccolo o troppo grande
        # Usiamo max(1, ...) per evitare un raggio di 0 se si zooma troppo indietro
        base_radius = self.TILE_SIZE / 2 - 3
        return max(2, int(base_radius * self.zoom_level))

    def _center_camera_on_npc(self, npc: 'Character', current_location: Optional['Location']):
        """Calcola e imposta l'offset della telecamera per centrare l'NPC."""
        if not current_location: return

        # Coordinate logiche dell'NPC
        npc_logical_x = npc.logical_x
        npc_logical_y = npc.logical_y

        # Calcola quante celle sono visibili
        visible_tiles_x = self.base_width // self.TILE_SIZE
        visible_tiles_y = self.base_height // self.TILE_SIZE

        # Calcola l'offset per centrare l'NPC
        # L'obiettivo è che la cella (npc_logical_x, npc_logical_y) sia al centro dell'area di gioco
        # (npc_logical_x - camera_offset_x) dovrebbe essere circa visible_tiles_x / 2
        # camera_offset_x = npc_logical_x - (visible_tiles_x / 2)
        self.camera_offset_x = npc_logical_x - (visible_tiles_x // 2)
        self.camera_offset_y = npc_logical_y - (visible_tiles_y // 2)

        # Applica i limiti della telecamera
        max_offset_x = max(0, current_location.logical_width - visible_tiles_x)
        max_offset_y = max(0, current_location.logical_height - visible_tiles_y)

        self.camera_offset_x = max(0, min(self.camera_offset_x, max_offset_x))
        self.camera_offset_y = max(0, min(self.camera_offset_y, max_offset_y))

        if settings.DEBUG_MODE:
            print(f"  [Renderer] Telecamera centrata su {npc.name}. Offset: ({self.camera_offset_x}, {self.camera_offset_y})")

    def _handle_events(self, simulation: Optional['Simulation']):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            elif event.type == pygame.MOUSEWHEEL:
                # Per ora, lo zoom è centrato sullo schermo. Uno zoom centrato sul cursore è più complesso.
                self.zoom_level += event.y * 0.1 # event.y è +1 per scroll up, -1 per scroll down
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
                                        distance_sq = (mouse_x - npc_screen_x)**2 + (mouse_y - npc_screen_y)**2
                                        if distance_sq <= (self.NPC_RADIUS)**2:
                                            self.selected_npc_id = npc.npc_id
                                            clicked_on_npc_this_turn = True
                                            if settings.DEBUG_MODE:
                                                print(f"  [Renderer] NPC Selezionato: {npc.name} (ID: {npc.npc_id})")
                                            # --- NUOVO: Centra la telecamera sull'NPC selezionato ---
                                            self._center_camera_on_npc(npc, current_loc)
                                            # --- FINE NUOVO ---
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
                    visible_tiles_x = self.base_width // self.TILE_SIZE 
                    visible_tiles_y = self.base_height // self.TILE_SIZE
                    max_offset_x = max(0, current_loc_for_bounds_calc.logical_width - visible_tiles_x)
                    max_offset_y = max(0, current_loc_for_bounds_calc.logical_height - visible_tiles_y)

                if event.key == pygame.K_TAB:
                    if self.location_keys_list:
                        self.current_location_index = (self.current_location_index + 1) % len(self.location_keys_list)
                        self.current_visible_location_id = self.location_keys_list[self.current_location_index]
                        self.camera_offset_x = 0
                        self.camera_offset_y = 0
                        self.selected_npc_id = None 
                        if settings.DEBUG_MODE:
                            print(f"  [Renderer] Cambiata locazione visualizzata a: ID '{self.current_visible_location_id}' (Indice: {self.current_location_index})")
                elif event.key == pygame.K_LEFT:
                    self.camera_offset_x = max(0, self.camera_offset_x - 1)
                elif event.key == pygame.K_RIGHT:
                    self.camera_offset_x = min(max_offset_x, self.camera_offset_x + 1)
                elif event.key == pygame.K_UP:
                    self.camera_offset_y = max(0, self.camera_offset_y - 1)
                elif event.key == pygame.K_DOWN:
                    self.camera_offset_y = min(max_offset_y, self.camera_offset_y + 1)
                elif event.key == pygame.K_c: # Tasto 'C' per centrare
                    if simulation and self.selected_npc_id and current_loc_for_bounds_calc: # Assicurati che la locazione sia valida
                        selected_npc = simulation.get_npc_by_id(self.selected_npc_id)
                        if selected_npc and selected_npc.current_location_id == self.current_visible_location_id:
                            self._center_camera_on_npc(selected_npc, current_loc_for_bounds_calc)
                        elif settings.DEBUG_MODE:
                            print(f"  [Renderer] Impossibile centrare: NPC non selezionato o non nella locazione corrente.")


    def _update_game_state(self, simulation: Optional['Simulation']):
        pass

    def _map_logical_to_screen(self, logical_x: int, logical_y: int) -> tuple[int, int]:
        screen_x = (logical_x - self.camera_offset_x) * self.TILE_SIZE + self.TILE_SIZE // 2 
        screen_y = (logical_y - self.camera_offset_y) * self.TILE_SIZE + self.TILE_SIZE // 2
        return screen_x, screen_y

    def _draw_npc(self, character: 'Character'):
        screen_x, screen_y = self._map_logical_to_screen(character.logical_x, character.logical_y)
        print(f"[DEBUG_GUI] _draw_npc: {character.name} -> logici ({character.logical_x},{character.logical_y}) -> schermo ({screen_x},{screen_y})") # DEBUG
        npc_color = ui_config.NPC_GENDER_COLORS.get(character.gender, ui_config.DEFAULT_NPC_COLOR)

        pygame.draw.circle(self.screen, npc_color, (screen_x, screen_y), self.NPC_RADIUS)

        is_selected = self.selected_npc_id == character.npc_id
        has_critical_need = False
        if character.needs:
            for need in character.needs.values():
                if need.get_value() <= settings.NEED_CRITICAL_THRESHOLD:
                    has_critical_need = True
                    break
        
        if is_selected:
            # Disegna un bordo di selezione più evidente
            pygame.draw.circle(self.screen, self.SELECTION_BORDER_COLOR, (screen_x, screen_y), self.NPC_RADIUS + 2, self.SELECTION_BORDER_WIDTH)
        elif has_critical_need: 
            pygame.draw.circle(self.screen, ui_config.NPC_CRITICAL_NEED_INDICATOR_COLOR, (screen_x, screen_y), self.NPC_RADIUS, 3)
        
        if self.font_debug:
            name_surface = self.font_debug.render(character.name, True, self.BLACK)
            name_rect = name_surface.get_rect(center=(screen_x, screen_y + self.NPC_RADIUS + 10))
            self.screen.blit(name_surface, name_rect)

    def _draw_game_object(self, game_obj: 'GameObject'):
        # ... (come prima) ...
        screen_x, screen_y = self._map_logical_to_screen(game_obj.logical_x, game_obj.logical_y)
        obj_width = self.TILE_SIZE - 4
        obj_height = self.TILE_SIZE - 4
        obj_rect = pygame.Rect(screen_x - obj_width // 2, screen_y - obj_height // 2, obj_width, obj_height)
        obj_color = ui_config.GAME_OBJECT_TYPE_COLORS.get(game_obj.object_type, ui_config.DEFAULT_GAME_OBJECT_COLOR)
        pygame.draw.rect(self.screen, obj_color, obj_rect)
        if game_obj.is_water_source:
            pygame.draw.rect(self.screen, self.BLACK, obj_rect, 2) 
        if self.font_debug:
            display_name = game_obj.name if len(game_obj.name) < 15 else game_obj.object_type.name
            name_surface = self.font_debug.render(display_name, True, self.BLACK)
            name_rect = name_surface.get_rect(center=(screen_x, screen_y + obj_height // 2 + 10))
            self.screen.blit(name_surface, name_rect)

    def _draw_text_in_panel(self, text: str, x: int, y: int, font=None, color=None) -> int:
        """Disegna testo nel pannello e restituisce la coordinata y per la riga successiva."""
        if font is None: font = self.font_panel_text
        if color is None: color = self.TEXT_COLOR
        if font:
            text_surface = font.render(text, True, color)
            self.screen.blit(text_surface, (self.base_width + x, y))
            return y + self.LINE_HEIGHT
        return y

    def _render_gui(self, simulation: Optional['Simulation']):
        # La tua logica di debug print iniziale può rimanere se ti è utile
        if settings.DEBUG_MODE and simulation:
            print(f"  [Render GUI] Locazione da renderizzare: {self.current_visible_location_id}")
            # ... (altre tue stampe di debug qui) ...

        game_area_rect = pygame.Rect(0, 0, self.base_width, self.base_height)
        self.screen.fill(self.GREY, game_area_rect)

        panel_rect = pygame.Rect(self.base_width, 0, self.PANEL_WIDTH, self.height)
        self.screen.fill(self.PANEL_BG_COLOR, panel_rect)
        pygame.draw.line(self.screen, self.BLACK, (self.base_width, 0), (self.base_width, self.height), 2)

        panel_padding = 10
        current_y = panel_padding
        
        npc_to_display_in_panel: Optional['Character'] = None
        current_location_instance_for_panel: Optional['Location'] = None # Rinominato per chiarezza

        if simulation:
            # Determina la locazione corrente per le informazioni del pannello
            if self.current_visible_location_id:
                current_location_instance_for_panel = simulation.get_location_by_id(self.current_visible_location_id)

            # Determina l'NPC da mostrare nel pannello (la tua logica è già qui e corretta)
            if self.selected_npc_id:
                npc_to_display_in_panel = simulation.get_npc_by_id(self.selected_npc_id)
                if npc_to_display_in_panel and npc_to_display_in_panel.current_location_id != self.current_visible_location_id:
                    npc_to_display_in_panel = None 
            
            if npc_to_display_in_panel is None and current_location_instance_for_panel and current_location_instance_for_panel.npcs_present_ids:
                first_npc_id_in_loc = next(iter(current_location_instance_for_panel.npcs_present_ids), None)
                if first_npc_id_in_loc:
                    npc_to_display_in_panel = simulation.get_npc_by_id(first_npc_id_in_loc)
            
            # Disegna elementi nell'area di gioco (la tua logica qui è corretta)
            if current_location_instance_for_panel: # Usiamo questa istanza anche per disegnare l'area gioco
                for game_obj in current_location_instance_for_panel.get_objects():
                    self._draw_game_object(game_obj)
                for npc_id_in_loc in current_location_instance_for_panel.npcs_present_ids:
                    npc_in_loc = simulation.get_npc_by_id(npc_id_in_loc)
                    if npc_in_loc:
                        self._draw_npc(npc_in_loc) # La tua logica di disegno NPC è corretta
            
            # 1. Titolo Pannello e ORA/DATA
        if self.font_panel_title:
            title_surf = self.font_panel_title.render("Info Panel", True, self.WHITE)
            self.screen.blit(title_surf, (self.base_width + panel_padding, current_y))
            current_y += self.LINE_HEIGHT + 5
        
        if simulation and simulation.time_manager and self.font_debug:
            datetime_info = simulation.time_manager.get_ath_detailed_datetime() # Chiama il metodo
            
            # Ora datetime_info è un dizionario, usalo direttamente
            year_val = int(datetime_info['year'])
            day_val = int(datetime_info['day_of_month'])
            month_val = int(datetime_info['month_of_year'])
            hour_val = int(datetime_info['hour'])
            minute_val = int(datetime_info['minute'])
            # Se vuoi i secondi, aggiungili qui e al dizionario in TimeManager se non già presenti
            # second_val = int(datetime_info['second']) 

            date_part = f"{year_val:04d}, {day_val:02d}/{month_val:02d}"
            time_part = f"{hour_val:02d}:{minute_val:02d}" # O includi i secondi se li hai
            # time_part = f"{hour_val:02d}:{minute_val:02d}:{second_val:02d}"
            
            day_name = str(datetime_info['day_name'])
            
            prefix_str = f"{date_part} {time_part} ("
            
            prefix_surface = self.font_debug.render(prefix_str, True, self.WHITE)
            self.screen.blit(prefix_surface, (self.base_width + panel_padding, current_y))
            
            current_x_pos = self.base_width + panel_padding + prefix_surface.get_width()
            
            day_color = self.RED_OBJ if day_name == "Nijah" else self.WHITE
            day_surface = self.font_debug.render(day_name, True, day_color)
            self.screen.blit(day_surface, (current_x_pos, current_y))

            current_x_pos += day_surface.get_width()
            suffix_surface = self.font_debug.render(")", True, self.WHITE)
            self.screen.blit(suffix_surface, (current_x_pos, current_y))

            current_y += self.LINE_HEIGHT # Rimosso il +5 per ora, possiamo aggiustare la spaziatura dopo
        elif settings.DEBUG_MODE:
            print(f"  [Renderer WARN] TimeManager non ha 'sim_time.get_datetime_str()'.")

            # 2. Info Locazione (come prima, ma usando current_location_instance_for_panel)
            if current_location_instance_for_panel:
                loc_name = current_location_instance_for_panel.name
                num_npcs = len(current_location_instance_for_panel.npcs_present_ids)
                num_objs = len(current_location_instance_for_panel.get_objects())
                cam_off = f"({self.camera_offset_x},{self.camera_offset_y})"
                current_y = self._draw_text_in_panel(f"Loc: {loc_name}", panel_padding, current_y, font=self.font_debug, color=self.WHITE)
                current_y = self._draw_text_in_panel(f"  NPCs: {num_npcs}, Oggetti: {num_objs}, Cam: {cam_off}", panel_padding, current_y, font=self.font_debug, color=self.WHITE)
            elif self.current_visible_location_id and self.font_debug:
                current_y = self._draw_text_in_panel(f"Loc ID: {self.current_visible_location_id} (Non Trovata!)", panel_padding, current_y, font=self.font_debug, color=self.RED_OBJ)
            elif self.font_debug :
                current_y = self._draw_text_in_panel("Nessuna locazione selezionata.", panel_padding, current_y, font=self.font_debug, color=self.WHITE)
            
            current_y += self.LINE_HEIGHT # Spazio

            # 3. Info NPC (con più dettagli)
            if npc_to_display_in_panel:
                npc = npc_to_display_in_panel # Alias per brevità
                
                # Intestazione NPC
                current_y = self._draw_text_in_panel(f"NPC Sel: {npc.name}", panel_padding, current_y, font=self.font_panel_title)
                
                # Info Generali NPC
                age_str = f"{npc.get_age_in_years_float():.1f} anni"
                gender_str = npc.gender.display_name_it() if npc.gender else "N/D"
                lifestage_str = npc.life_stage.display_name_it() if npc.life_stage else "N/D"
                current_y = self._draw_text_in_panel(f"  {gender_str}, {age_str} ({lifestage_str})", panel_padding, current_y)
                current_y += 5

                # Azione Corrente (come prima)
                if npc.current_action:
                    action_name = npc.current_action.action_type_name
                    progress = npc.current_action.get_progress_percentage()
                    current_y = self._draw_text_in_panel(f"  Azione: {action_name} ({progress:.0f}%)", panel_padding, current_y)
                else:
                    current_y = self._draw_text_in_panel("  Azione: Idle", panel_padding, current_y)
                current_y += 5

                # Personalità
                current_y = self._draw_text_in_panel("Personalità:", panel_padding, current_y, font=self.font_debug, color=self.WHITE)
                
                trait_display_names = [trait_obj.display_name for trait_obj in npc.traits.values()]
                trait_str = ", ".join(sorted(trait_display_names)) if trait_display_names else "Nessuno"
                # Semplice gestione a capo per i tratti (può essere migliorata)
                if self.font_panel_text:
                    prefix_tratti = "  Tratti: "
                    remaining_width = self.PANEL_WIDTH - panel_padding * 2 - self.font_panel_text.size(prefix_tratti)[0]
                    
                    if self.font_panel_text.size(trait_str)[0] > remaining_width:
                        # Semplice split se troppo lungo, potremmo fare un wrapping migliore
                        parts = []
                        current_part = ""
                        for word in trait_str.split(', '):
                            if self.font_panel_text.size(current_part + word + ", ")[0] < remaining_width:
                                current_part += word + ", "
                            else:
                                parts.append(current_part.rstrip(", "))
                                current_part = word + ", "
                        parts.append(current_part.rstrip(", "))
                        current_y = self._draw_text_in_panel(f"{prefix_tratti}{parts[0]}", panel_padding, current_y)
                        for part in parts[1:]:
                           current_y = self._draw_text_in_panel(f"    {part}", panel_padding, current_y)
                    else:
                        current_y = self._draw_text_in_panel(f"{prefix_tratti}{trait_str}", panel_padding, current_y)
                
                asp_name = npc.aspiration.display_name_it() if npc.aspiration else "Nessuna"
                asp_prog = npc.aspiration_progress
                current_y = self._draw_text_in_panel(f"  Aspirazione: {asp_name} ({asp_prog:.0%})", panel_padding, current_y)
                
                interest_names = [i.name.replace("_", " ").title() for i in npc.get_interests()]
                interest_str = ", ".join(sorted(interest_names)) if interest_names else "Nessuno"
                current_y = self._draw_text_in_panel(f"  Interessi: {interest_str}", panel_padding, current_y) # Anche qui, no wrapping per ora
                current_y += self.LINE_HEIGHT

                # Bisogni (come prima)
                current_y = self._draw_text_in_panel("Bisogni:", panel_padding, current_y, font=self.font_debug, color=self.WHITE)
                if npc.needs:
                    for need_type, need_obj in sorted(npc.needs.items(), key=lambda item: item[0].name):
                        # ... (la tua logica per disegnare le barre dei bisogni è già qui e va bene) ...
                        val_str = f"{need_obj.get_value():.0f}"
                        need_ui_info = ui_config.NEED_UI_CONFIG.get(need_type, {})
                        need_color_name = need_ui_info.get("color", "gray")
                        try: bar_fill_color = pygame.Color(need_color_name)
                        except ValueError: bar_fill_color = self.WHITE 
                        bar_x = self.base_width + panel_padding + 85 # Leggermente aggiustato
                        bar_max_width = self.PANEL_WIDTH - panel_padding * 2 - 90 # Leggermente aggiustato
                        bar_current_width = int((need_obj.get_value() / settings.NEED_MAX_VALUE) * bar_max_width)
                        bar_height = self.LINE_HEIGHT - 8
                        bar_y_offset = current_y + 4
                        pygame.draw.rect(self.screen, (80,80,80), (bar_x, bar_y_offset, bar_max_width, bar_height))
                        if bar_current_width > 0 : pygame.draw.rect(self.screen, bar_fill_color, (bar_x, bar_y_offset, bar_current_width, bar_height))
                        current_y = self._draw_text_in_panel(f"    {need_obj.get_display_name()}:", panel_padding, current_y) # Rimosso val_str da qui per allineare con la barra
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
            self.location_keys_list = sorted(list(simulation.locations.keys())) # Ordina per avere un ciclo consistente
            if self.location_keys_list:
                self.current_location_index = 0
                self.current_visible_location_id = self.location_keys_list[self.current_location_index]
                print(f"[DEBUG_GUI_INIT] Locazione iniziale da visualizzare: {self.current_visible_location_id}")
                if settings.DEBUG_MODE:
                    print(f"  [Renderer Loop Start] Visualizzazione iniziale locazione: {self.current_visible_location_id}")

        else:
            self.location_keys_list = []
            self.current_visible_location_id = None
        self.is_running = True
        while self.is_running:
            self._handle_events(simulation)
            
            if not settings.DEBUG_MODE and simulation:
                simulation._update_simulation_state() 
            
            self._update_game_state(simulation) 
            self._render_gui(simulation)
            self.clock.tick(60) 
        self._quit_pygame()

    def _quit_pygame(self):
        if settings.DEBUG_MODE:
            print(f"  [Renderer] Chiusura Pygame...")
        pygame.font.quit() 
        pygame.quit()