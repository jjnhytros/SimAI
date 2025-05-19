import pygame
import pygame_gui

# Potrebbe essere necessario importare la tua classe Character, CharacterManager,
# e le definizioni dei componenti da altri moduli del tuo progetto.
# Esempio:
# from src.entities.character import Character
# from src.managers.character_manager import CharacterManager
# from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, UI_THEME_PATH

# Placeholder per le costanti, da definire nel tuo config.py
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
UI_THEME_PATH = 'path_to_your_theme.json' # Se hai un tema per pygame_gui

class CharacterCreationScreen:
    def __init__(self, ui_manager, screen_surface, character_manager):
        self.ui_manager = ui_manager
        self.screen_surface = screen_surface
        self.character_manager = character_manager # Per finalizzare la creazione

        self.is_running = True # Flag per controllare lo stato della schermata
        self.character_data = {
            "first_name": "",
            "last_name": "",
            "gender": None, # Es. "Male", "Female"
            "age_group": "Young Adult", # Default
            # Altri dati verranno aggiunti qui
        }

        # --- Elementi UI ---
        self.window = None # La finestra principale della UI di creazione
        self.identity_panel = None
        self.first_name_entry = None
        self.last_name_entry = None
        self.gender_male_button = None
        self.gender_female_button = None
        
        self.character_preview_area = None # Rettangolo per l'anteprima del personaggio
        self.character_preview_image = None # Surface per l'immagine del personaggio

        self._build_ui()

    def _build_ui(self):
        # --- Finestra Principale (opzionale, o usa l'intera superficie) ---
        # Potresti avere un UIPanel grande come "sfondo" per organizzare tutto
        # Per ora, usiamo pannelli specifici per le sezioni.

        # --- Area Anteprima Personaggio (Placeholder) ---
        # A sinistra, circa 1/3 o 1/2 dello schermo
        preview_width = SCREEN_WIDTH // 3
        self.character_preview_area = pygame.Rect(50, 50, preview_width, SCREEN_HEIGHT - 100)
        # Carica un'immagine placeholder o disegna un rettangolo colorato
        self.character_preview_image = pygame.Surface((preview_width - 20, SCREEN_HEIGHT - 120))
        self.character_preview_image.fill(pygame.Color('darkgrey')) # Placeholder
        # Qui in futuro caricherai e aggiornerai l'immagine del personaggio
        # basata sugli asset LPC e le scelte dell'utente.

        # --- Pannello Identità ---
        # A destra dell'anteprima
        panel_left = self.character_preview_area.right + 50
        panel_top = 50
        panel_width = SCREEN_WIDTH - panel_left - 50
        panel_height = 250 # Altezza stimata per la sezione identità

        self.identity_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((panel_left, panel_top), (panel_width, panel_height)),
            manager=self.ui_manager,
            object_id='#identity_panel' # Per lo styling
        )

        current_y = 20 # Posizione y relativa all'interno del pannello

        # Titolo Sezione Identità
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, current_y), (panel_width - 20, 30)),
            text="👤 Identità",
            manager=self.ui_manager,
            container=self.identity_panel,
            object_id='@title_label'
        )
        current_y += 40

        # Nome
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, current_y), (100, 30)),
            text="Nome:",
            manager=self.ui_manager,
            container=self.identity_panel
        )
        self.first_name_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((120, current_y), (panel_width - 140, 35)),
            manager=self.ui_manager,
            container=self.identity_panel,
            object_id='#first_name_entry'
        )
        current_y += 45

        # Cognome
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, current_y), (100, 30)),
            text="Cognome:",
            manager=self.ui_manager,
            container=self.identity_panel
        )
        self.last_name_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((120, current_y), (panel_width - 140, 35)),
            manager=self.ui_manager,
            container=self.identity_panel,
            object_id='#last_name_entry'
        )
        current_y += 45

        # Genere
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, current_y), (100, 30)),
            text="Genere:",
            manager=self.ui_manager,
            container=self.identity_panel
        )
        button_width = (panel_width - 140 - 10) // 2 # Due bottoni affiancati
        self.gender_male_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((120, current_y), (button_width, 35)),
            text="Maschile",
            manager=self.ui_manager,
            container=self.identity_panel,
            object_id='#gender_male_button'
        )
        self.gender_female_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((120 + button_width + 10, current_y), (button_width, 35)),
            text="Femminile",
            manager=self.ui_manager,
            container=self.identity_panel,
            object_id='#gender_female_button'
        )
        current_y += 45
        
        # Bottone "Accetta e Inizia" (Placeholder, da posizionare meglio globalmente)
        self.accept_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((panel_left, SCREEN_HEIGHT - 100), (panel_width, 50)),
            text="✅ Accetta e Inizia",
            manager=self.ui_manager,
            object_id="#accept_button"
        )


    def process_event(self, event):
        # Gestisci gli eventi della UI
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.gender_male_button:
                self.character_data["gender"] = "Male"
                print(f"Genere selezionato: {self.character_data['gender']}")
                # Qui aggiorneresti l'anteprima del personaggio
            elif event.ui_element == self.gender_female_button:
                self.character_data["gender"] = "Female"
                print(f"Genere selezionato: {self.character_data['gender']}")
                # Qui aggiorneresti l'anteprima del personaggio
            elif event.ui_element == self.accept_button:
                self._finalize_character()

        if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
            if event.ui_element == self.first_name_entry:
                self.character_data["first_name"] = event.text
                print(f"Nome inserito: {self.character_data['first_name']}")
            elif event.ui_element == self.last_name_entry:
                self.character_data["last_name"] = event.text
                print(f"Cognome inserito: {self.character_data['last_name']}")
                
        self.ui_manager.process_events(event)


    def _finalize_character(self):
        # Raccogli tutti i dati da self.character_data
        first_name = self.character_data.get("first_name", "SenzaNome")
        last_name = self.character_data.get("last_name", "SenzaCognome")
        gender = self.character_data.get("gender")
        # ... raccogli altri dati dalle sezioni successive
        
        print(f"Finalizzazione personaggio: {first_name} {last_name}, Genere: {gender}")

        # Esempio di creazione (la tua logica potrebbe essere più complessa):
        # new_char = self.character_manager.create_new_playable_character(
        #     first_name=first_name,
        #     last_name=last_name,
        #     gender=gender,
        #     # ... altri parametri come aspirazione, tratti, ecc.
        # )
        # if new_char:
        #     print(f"Personaggio {new_char.full_name} creato con ID: {new_char.id}")
        #     self.is_running = False # Termina questa schermata
        # else:
        #     print("Errore nella creazione del personaggio.")
        #     # Magari mostrare un messaggio di errore all'utente
        self.is_running = False # Per ora, esce semplicemente


    def update(self, time_delta):
        self.ui_manager.update(time_delta)

    def draw(self):
        # Disegna l'area di anteprima (placeholder)
        pygame.draw.rect(self.screen_surface, pygame.Color('black'), self.character_preview_area, 2)
        self.screen_surface.blit(self.character_preview_image, (self.character_preview_area.left + 10, self.character_preview_area.top + 10))
        
        # La UI Manager disegna i suoi elementi
        self.ui_manager.draw_ui(self.screen_surface)

    def run(self):
        """Metodo principale per eseguire il loop di questa schermata."""
        clock = pygame.time.Clock()
        self.is_running = True

        while self.is_running:
            time_delta = clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                    # Qui dovresti gestire l'uscita generale dal gioco o tornare al menu principale
                
                self.process_event(event)

            self.update(time_delta)
            
            self.screen_surface.fill(pygame.Color("cornflowerblue")) # Sfondo temporaneo
            self.draw()
            
            pygame.display.flip()
        
        # Restituisci i dati del personaggio o un segnale per procedere
        # return self.character_data # o l'oggetto Character creato