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
    from core.world.location import Location # Importa Location

class Renderer:
    TILE_SIZE = 32 # Dimensione di una "cella" logica in pixel (esempio)
    PANEL_WIDTH = 300 # Larghezza del pannello informativo
    TEXT_COLOR = (230, 230, 230) # Colore testo quasi bianco per il pannello
    PANEL_BG_COLOR = (40, 40, 60) # Colore di sfondo per il pannello (blu scuro/grigio)
    LINE_HEIGHT = 20 # Altezza linea per il testo nel pannello

    def __init__(self, width: int = 1280, height: int = 768, caption: str = "SimAI Game"):
        pygame.init()
        pygame.font.init()

        self.base_width = width
        self.base_height = height
        # La larghezza effettiva dello schermo Pygame include il pannello
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
        # self.BLUE = (0, 0, 255)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0) # Per gli oggetti senza nome specifico
        self.GREEN_OBJ = (0, 180, 0) # Colore più scuro per gli oggetti
        self.RED_OBJ = (200, 0, 0)   # Colore più scuro per gli oggetti

        try:
            self.font_debug = pygame.font.Font(None, 22) # Leggermente più piccolo per più info
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
                print(f"  [Renderer ERROR] Errore inizializzazione font: {e}.")
            self.font_debug = pygame.font.Font(None, 22)
            self.font_panel_title = pygame.font.Font(None, 28)
            self.font_panel_text = pygame.font.Font(None, 20)
            self.font_main = pygame.font.Font(None, 48)
        self.current_visible_location_id: Optional[str] = None
        self.location_keys_list: List[str] = []
        self.current_location_index: int = 0
        self.camera_offset_x: int = 0
        self.camera_offset_y: int = 0

        if settings.DEBUG_MODE:
            print(f"  [Renderer] Inizializzato Pygame con finestra {self.width}x{self.height}")

    def _handle_events(self, simulation: Optional['Simulation']):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            elif event.type == pygame.VIDEORESIZE:
                self.width = event.w
                self.height = event.h
                self.screen_size = (self.width, self.height)
                self.screen = pygame.display.set_mode(self.screen_size, pygame.RESIZABLE)
                if settings.DEBUG_MODE:
                    print(f"  [Renderer] Finestra ridimensionata a: {self.width}x{self.height}")
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB: # Usa TAB per ciclare le locazioni
                    if self.location_keys_list: # Se ci sono locazioni
                        self.current_location_index = (self.current_location_index + 1) % len(self.location_keys_list)
                        self.current_visible_location_id = self.location_keys_list[self.current_location_index]
                        if settings.DEBUG_MODE:
                            print(f"  [Renderer] Cambiata locazione visualizzata a: ID '{self.current_visible_location_id}' (Indice: {self.current_location_index})")
                # Determina i limiti massimi per l'offset basati sulla locazione corrente e la dimensione dello schermo
                max_offset_x = 0
                max_offset_y = 0
                current_loc: Optional['Location'] = None # Dichiarazione per type hinting
                
                if simulation and self.current_visible_location_id:
                    current_loc = simulation.get_location_by_id(self.current_visible_location_id)
                
                if current_loc:
                    visible_tiles_x = self.width // self.TILE_SIZE
                    visible_tiles_y = self.height // self.TILE_SIZE
                    max_offset_x = max(0, current_loc.logical_width - visible_tiles_x)
                    max_offset_y = max(0, current_loc.logical_height - visible_tiles_y)

                if event.key == pygame.K_LEFT:
                    self.camera_offset_x = max(0, self.camera_offset_x - 1)
                elif event.key == pygame.K_RIGHT:
                    self.camera_offset_x = min(max_offset_x, self.camera_offset_x + 1)
                elif event.key == pygame.K_UP:
                    self.camera_offset_y = max(0, self.camera_offset_y - 1)
                elif event.key == pygame.K_DOWN:
                    self.camera_offset_y = min(max_offset_y, self.camera_offset_y + 1)

    def _update_game_state(self, simulation: Optional['Simulation']):
        pass

    def _map_logical_to_screen(self, logical_x: int, logical_y: int) -> tuple[int, int]:
        """Converte coordinate logiche (basate su griglia) in coordinate schermo."""
        # Per ora, semplice offset e moltiplicazione per TILE_SIZE.
        # Potrebbe includere lo scroll della telecamera in futuro.
        screen_x = logical_x * self.TILE_SIZE + self.TILE_SIZE // 2 # Centra nella cella
        screen_y = logical_y * self.TILE_SIZE + self.TILE_SIZE // 2
        return screen_x, screen_y

    def _draw_npc(self, character: 'Character'): # Rimosso 'position' dai parametri
        """Disegna un NPC usando le sue coordinate logiche."""
        screen_x, screen_y = self._map_logical_to_screen(character.logical_x, character.logical_y)
        
        npc_radius = self.TILE_SIZE // 2 - 2 # Raggio leggermente più piccolo della cella
        npc_color = ui_config.NPC_GENDER_COLORS.get(character.gender, ui_config.DEFAULT_NPC_COLOR)
        pygame.draw.circle(self.screen, npc_color, (screen_x, screen_y), npc_radius)
        has_critical_need = False
        if character.needs: # Assicurati che il dizionario dei bisogni esista
            for need in character.needs.values():
                if need.get_value() <= settings.NEED_CRITICAL_THRESHOLD:
                    has_critical_need = True
                    break # Trovato un bisogno critico, non serve continuare

        if has_critical_need:
            # Disegna un bordo rosso attorno al cerchio
            pygame.draw.circle(self.screen,
                               ui_config.NPC_CRITICAL_NEED_INDICATOR_COLOR,
                               (screen_x, screen_y),
                               npc_radius, # Stesso raggio del cerchio interno
                               3) # Spessore del bordo in pixel
        
        if self.font_debug:
            name_surface = self.font_debug.render(character.name, True, self.BLACK)
            name_rect = name_surface.get_rect(center=(screen_x, screen_y + npc_radius + 10))
            self.screen.blit(name_surface, name_rect)

    def _draw_game_object(self, game_obj: 'GameObject'):
        """Disegna un GameObject usando un colore basato sul suo ObjectType."""
        screen_x, screen_y = self._map_logical_to_screen(game_obj.logical_x, game_obj.logical_y)
        
        obj_width = self.TILE_SIZE - 4
        obj_height = self.TILE_SIZE - 4
        obj_rect = pygame.Rect(screen_x - obj_width // 2, screen_y - obj_height // 2, obj_width, obj_height)
        
        obj_color = ui_config.GAME_OBJECT_TYPE_COLORS.get(game_obj.object_type, ui_config.DEFAULT_GAME_OBJECT_COLOR)
        pygame.draw.rect(self.screen, obj_color, obj_rect)

        # Opzionale: aggiungi un bordo se è una fonte d'acqua, per esempio
        if game_obj.is_water_source:
            pygame.draw.rect(self.screen, self.BLACK, obj_rect, 2) # Bordo nero di spessore 2

        if self.font_debug:
            display_name = game_obj.name if len(game_obj.name) < 15 else game_obj.object_type.name
            name_surface = self.font_debug.render(display_name, True, self.BLACK)
            name_rect = name_surface.get_rect(center=(screen_x, screen_y + obj_height // 2 + 10))
            self.screen.blit(name_surface, name_rect)

    def _draw_text_in_panel(self, text: str, x: int, y: int, font=None, color=None) -> int:
        """Disegna testo nel pannello e restituisce la coordinata y per la riga successiva."""
        if font is None: font = self.font_panel_text
        if color is None: color = self.TEXT_COLOR
        
        if font: # Assicurati che il font sia stato caricato
            text_surface = font.render(text, True, color)
            self.screen.blit(text_surface, (self.base_width + x, y))
            return y + self.LINE_HEIGHT # Spazio per la prossima riga
        return y # Non fare nulla se il font non è disponibile

    def _render_gui(self, simulation: Optional['Simulation']):
        game_area_rect = pygame.Rect(0, 0, self.base_width, self.base_height)
        self.screen.fill(self.GREY, game_area_rect)

        panel_rect = pygame.Rect(self.base_width, 0, self.PANEL_WIDTH, self.height)
        self.screen.fill(self.PANEL_BG_COLOR, panel_rect)
        pygame.draw.line(self.screen, self.BLACK, (self.base_width, 0), (self.base_width, self.height), 2)

        panel_padding = 10
        current_y = panel_padding
        npc_to_display_in_panel: Optional['Character'] = None # Per il pannello informativo

        if simulation:
            active_location_id_to_render = self.current_visible_location_id
            current_location_instance: Optional['Location'] = None # Definisci qui per un ambito più ampio

            if active_location_id_to_render:
                current_location_instance = simulation.get_location_by_id(active_location_id_to_render)
                if current_location_instance:
                    # Disegna oggetti e NPC nell'area di gioco
                    for game_obj in current_location_instance.get_objects():
                        self._draw_game_object(game_obj)
                    for npc_id_in_loc in current_location_instance.npcs_present_ids:
                        npc_in_loc = simulation.get_npc_by_id(npc_id_in_loc)
                        if npc_in_loc:
                            self._draw_npc(npc_in_loc)
                            if npc_to_display_in_panel is None: # Prendi il primo NPC della locazione per il pannello
                                npc_to_display_in_panel = npc_in_loc
                    
                    # Info Locazione nel Pannello
                    if self.font_debug: # Usiamo font_debug per il testo della locazione nel pannello
                        cam_offset_text = f"Cam Offset: ({self.camera_offset_x},{self.camera_offset_y})"
                        loc_text_str = f"Loc: {current_location_instance.name} {cam_offset_text}"
                        current_y = self._draw_text_in_panel(loc_text_str, panel_padding, current_y, font=self.font_debug, color=self.WHITE) # Usa font_debug e un colore visibile
                        current_y = self._draw_text_in_panel(f"  NPCs: {len(current_location_instance.npcs_present_ids)}", panel_padding, current_y, font=self.font_debug, color=self.WHITE)
                        current_y = self._draw_text_in_panel(f"  Oggetti: {len(current_location_instance.get_objects())}", panel_padding, current_y, font=self.font_debug, color=self.WHITE)

                elif self.font_debug: # current_location_instance è None ma active_location_id_to_render esiste
                    current_y = self._draw_text_in_panel(f"Loc ID: {active_location_id_to_render} (Non Trovata!)", panel_padding, current_y, font=self.font_debug, color=self.RED_OBJ)
            
            # Se nessun NPC è stato selezionato dalla locazione, prendi il primo della simulazione (se esiste)
            if npc_to_display_in_panel is None and simulation.npcs:
                sorted_npcs = sorted(list(simulation.npcs.values()), key=lambda npc: npc.npc_id)
                if sorted_npcs:
                    npc_to_display_in_panel = sorted_npcs[0]
            
            current_y += self.LINE_HEIGHT # Spazio

            # Info NPC nel Pannello (se ne abbiamo uno da mostrare)
            if npc_to_display_in_panel:
                current_y = self._draw_text_in_panel(f"NPC: {npc_to_display_in_panel.name}", panel_padding, current_y, font=self.font_panel_title)
                if npc_to_display_in_panel.current_action:
                    action_name = npc_to_display_in_panel.current_action.action_type_name
                    progress = npc_to_display_in_panel.current_action.get_progress_percentage()
                    current_y = self._draw_text_in_panel(f"  Azione: {action_name} ({progress:.0f}%)", panel_padding, current_y)
                else:
                    current_y = self._draw_text_in_panel(f"  Azione: Idle", panel_padding, current_y)
                
                current_y = self._draw_text_in_panel("  Bisogni:", panel_padding, current_y)
                if npc_to_display_in_panel.needs:
                    for need_type, need_obj in sorted(npc_to_display_in_panel.needs.items(), key=lambda item: item[0].name):
                        val_str = f"{need_obj.get_value():.0f}"
                        need_ui_info = ui_config.NEED_UI_CONFIG.get(need_type, {})
                        need_color_str = need_ui_info.get("color", "gray") # Default a grigio se non specificato
                        
                        # Pygame non accetta nomi di colori stringa direttamente per il disegno,
                        # quindi avremmo bisogno di un mapping nome colore -> RGB, o usare colori RGB.
                        # Per ora, usiamo un colore di default per la barra se non è RGB.
                        try:
                            bar_fill_color = pygame.Color(need_color_str)
                        except ValueError:
                            bar_fill_color = self.WHITE # Fallback se il nome colore non è valido

                        bar_x = self.base_width + panel_padding + 75
                        bar_max_width = self.PANEL_WIDTH - panel_padding * 2 - 80
                        bar_current_width = int((need_obj.get_value() / settings.NEED_MAX_VALUE) * bar_max_width)
                        bar_height = self.LINE_HEIGHT - 8
                        bar_y_offset = current_y + 4

                        pygame.draw.rect(self.screen, (80,80,80), (bar_x, bar_y_offset, bar_max_width, bar_height)) # Sfondo barra
                        pygame.draw.rect(self.screen, bar_fill_color, (bar_x, bar_y_offset, bar_current_width, bar_height))
                        
                        current_y = self._draw_text_in_panel(f"    {need_obj.get_display_name()}: {val_str}", panel_padding, current_y)
                else:
                    current_y = self._draw_text_in_panel("    (Nessun bisogno definito)", panel_padding, current_y)
            elif self.font_debug: # Se npc_to_display_in_panel è ancora None
                current_y = self._draw_text_in_panel("Nessun NPC da mostrare nel pannello.", panel_padding, current_y)

        else: # Nessuna simulazione caricata
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