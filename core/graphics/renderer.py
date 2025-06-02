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

    def __init__(self, width: int = 1280, height: int = 768, caption: str = "SimAI Game"):
        pygame.init()
        pygame.font.init()

        self.width = width
        self.height = height
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
            self.font_debug = pygame.font.Font(None, 24)
            common_system_font_name = "arial"
            try:
                self.font_main = pygame.font.SysFont(common_system_font_name, 48)
            except pygame.error:
                if settings.DEBUG_MODE:
                    print(f"  [Renderer WARN] Font di sistema '{common_system_font_name}' non trovato. Uso font default Pygame per font_main.")
                self.font_main = pygame.font.Font(None, 48)
        except pygame.error as e:
            if settings.DEBUG_MODE:
                print(f"  [Renderer ERROR] Errore imprevisto inizializzazione font: {e}. Uso font default Pygame.")
            self.font_debug = pygame.font.Font(None, 24)
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

    def _render_gui(self, simulation: Optional['Simulation']):
        self.screen.fill(self.GREY)

        if simulation:
            active_location_id_to_render = self.current_visible_location_id
            # Determina la locazione da visualizzare (es. la locazione del primo NPC)
            active_location_id: Optional[str] = None
            if simulation.npcs:
                first_npc = next(iter(simulation.npcs.values()))
                active_location_id = first_npc.current_location_id
            
            if active_location_id:
                current_location = simulation.get_location_by_id(active_location_id)
                if current_location:
                    if self.font_debug:
                        loc_text = self.font_debug.render(f"Locazione Attiva: {current_location.name}", True, self.BLACK)
                        self.screen.blit(loc_text, (10, 40)) # Posizione diversa per non sovrapporsi agli FPS

                    # Disegna oggetti nella locazione attiva
                    for game_obj in current_location.get_objects():
                        self._draw_game_object(game_obj) # Passa solo l'oggetto

                    # Disegna NPC nella locazione attiva
                    for npc_id in current_location.npcs_present_ids:
                        npc = simulation.get_npc_by_id(npc_id)
                        if npc:
                            self._draw_npc(npc) # Passa solo l'NPC
                elif self.font_debug:
                    loc_err_text = self.font_debug.render(f"Locazione ID '{active_location_id}' non trovata!", True, self.RED)
                    self.screen.blit(loc_err_text, (10, 40))
            elif self.font_debug:
                no_loc_text = self.font_debug.render("Nessun NPC o locazione attiva da visualizzare.", True, self.BLACK)
                self.screen.blit(no_loc_text, (10, 40))
        else:
            if self.font_main:
                text_surface = self.font_main.render("SimAI - GUI Attiva (Nessuna Simulazione Caricata)", True, self.BLACK)
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