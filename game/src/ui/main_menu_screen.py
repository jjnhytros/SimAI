import pygame
import pygame_gui
import random # Per la generazione casuale dei nomi/dati
from typing import Optional, Tuple, List, Dict, Any # Per i type hints

# Importa config per accedere alle costanti di schermo e ai GAME_FLOW_STATE_*
from game import config # Accede a simai/game/config.py

# Non dovrebbe importare CharacterManager o Character qui, se vogliamo che restituisca solo dati.
# SpriteSheetManager potrebbe servire se il menu avesse anteprime grafiche complesse,
# ma per ora lo passiamo solo per coerenza con la firma __init__ precedente.
# from game.src.managers.asset_manager import SpriteSheetManager


class MainMenuScreen:
    def __init__(self, 
                 ui_manager: pygame_gui.UIManager, 
                 screen_surface: pygame.Surface, 
                 character_manager_ref: Optional[Any], # Mantenuto Optional, ma idealmente non usato per la creazione qui
                 sprite_sheet_manager_ref: Optional[Any] # Mantenuto Optional
                ):
        self.ui_manager = ui_manager
        self.screen_surface = screen_surface
        # self.character_manager = character_manager_ref # Non useremo CM per creare Character qui
        # self.sprite_sheet_manager = sprite_sheet_manager_ref # Non usato attivamente in questa versione semplice

        self.next_flow_state_signal: Optional[str] = None
        self.player_character_data_to_pass: Optional[Dict[str, Any]] = None # Non usato da MainMenu, ma per coerenza con il return
        self.debug_npc_data_to_pass: List[Dict[str, Any]] = []

        self.is_running = False # Controlla il loop interno di questa schermata

        self._build_ui()

    def _build_ui(self):
        # Usa le dimensioni da config se disponibili, altrimenti valori di fallback
        screen_width = getattr(config, 'SCREEN_WIDTH', 1024)
        screen_height = getattr(config, 'SCREEN_HEIGHT', 768)

        panel_width = 450 
        panel_height = 320 
        panel_x = (screen_width - panel_width) // 2
        panel_y = (screen_height - panel_height) // 2

        self.menu_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((panel_x, panel_y), (panel_width, panel_height)),
            manager=self.ui_manager,
            object_id='#main_menu_panel' 
        )

        button_width = panel_width - 40
        button_height = 50
        current_y = 20 

        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, current_y), (panel_width - 20, 40)),
            text=getattr(config, 'GAME_NAME', "SimAI") + " - Anthalys", 
            manager=self.ui_manager,
            container=self.menu_panel,
            object_id='@main_title_label' 
        )
        current_y += 60 

        self.new_game_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((20, current_y), (button_width, button_height)),
            text="Nuova Partita (Crea Personaggio)",
            manager=self.ui_manager,
            container=self.menu_panel,
            object_id='#new_game_button'
        )
        current_y += button_height + 15

        self.new_random_game_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((20, current_y), (button_width, button_height)),
            text="Nuova Partita Random (Debug)",
            manager=self.ui_manager,
            container=self.menu_panel,
            object_id='#new_random_game_button'
        )
        current_y += button_height + 15
        
        self.exit_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((20, current_y), (button_width, button_height)),
            text="Esci dal Gioco",
            manager=self.ui_manager,
            container=self.menu_panel,
            object_id='#exit_button'
        )

    def _create_random_debug_npc_data(self) -> List[Dict[str, Any]]:
        """Crea DATI per 2 NPC (M & F) con valori casuali per il debug."""
        genders = ["Male", "Female"]
        npc_data_list: List[Dict[str, Any]] = []
        
        male_names = getattr(config, 'NPC_NAME_LIST_MALE', ["Bob", "John"])
        female_names = getattr(config, 'NPC_NAME_LIST_FEMALE', ["Alice", "Eva"])
        surnames = getattr(config, 'NPC_NAME_LIST_LAST', ["Rossi", "Bianchi"]) 

        for gender_choice in genders:
            first_name = ""
            if gender_choice == "Male":
                first_name = random.choice(male_names) if male_names else "DebugMaschio"
            else: 
                first_name = random.choice(female_names) if female_names else "DebugFemmina"
            
            last_name = random.choice(surnames) if surnames else "DebugCognome"
            
            npc_data = {
                "first_name": first_name,
                "last_name": last_name,
                "gender": gender_choice,
                "age_years": random.randint(config.NPC_INITIAL_AGE_YEARS_MIN, config.NPC_INITIAL_AGE_YEARS_MAX)
            }
            npc_data_list.append(npc_data)
            print(f"MainMenu: Dati NPC Debug generati: {first_name} {last_name}, Genere: {gender_choice}")
            
        return npc_data_list

    def process_event(self, event: pygame.event.Event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.new_game_button:
                print("MainMenu: Bottone Nuova Partita (Crea Personaggio) premuto.")
                self.next_flow_state_signal = config.GAME_STATE_CHARACTER_CREATION # Da config
                self.is_running = False 
            elif event.ui_element == self.new_random_game_button:
                print("MainMenu: Bottone Nuova Partita Random (Debug) premuto.")
                self.debug_npc_data_to_pass = self._create_random_debug_npc_data()
                if not self.debug_npc_data_to_pass or len(self.debug_npc_data_to_pass) < 2:
                    print("MainMenu: ATTENZIONE - Non sono stati generati dati per 2 NPC di debug.")
                self.next_flow_state_signal = config.GAME_STATE_GAMEPLAY # Da config
                self.is_running = False 
            elif event.ui_element == self.exit_button:
                print("MainMenu: Bottone Esci premuto.")
                self.next_flow_state_signal = config.GAME_STATE_QUIT # Da config
                self.is_running = False 
        
        self.ui_manager.process_events(event)


    def update(self, time_delta: float):
        self.ui_manager.update(time_delta)

    def draw(self):
        self.ui_manager.draw_ui(self.screen_surface)

    def run(self) -> Tuple[Optional[str], Optional[Dict[str, Any]], List[Dict[str, Any]]]:
        self.is_running = True
        self.next_flow_state_signal = None 
        self.player_character_data_to_pass = None 
        self.debug_npc_data_to_pass = []      

        if hasattr(self, 'menu_panel'): self.menu_panel.show()

        clock = pygame.time.Clock()

        while self.is_running:
            time_delta = clock.tick(getattr(config, 'FPS', 30)) / 1000.0
            if time_delta <=0: time_delta = 1/ getattr(config, 'FPS', 30)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                    self.next_flow_state_signal = config.GAME_FLOW_STATE_QUIT # Da config
                
                self.process_event(event)

            self.update(time_delta)
            
            self.screen_surface.fill(pygame.Color(getattr(config, 'MAIN_MENU_BG_COLOR', (30, 30, 60))))
            self.draw()
            
            pygame.display.flip()
        
        if hasattr(self, 'menu_panel'): self.menu_panel.hide()

        return self.next_flow_state_signal, self.player_character_data_to_pass, self.debug_npc_data_to_pass