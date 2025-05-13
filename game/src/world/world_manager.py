# simai/game/src/world/world_manager.py
import pygame
import sys # Per sys.exit in caso di errore critico

try:
    # Tentativo di importare config dal package 'game'
    # Questo si aspetta che tu stia eseguendo il gioco dalla directory 'simai'
    # con un comando come 'python -m game.main'
    from game import config
except ImportError:
    print("ERRORE CRITICO (WorldManager): Impossibile importare 'game.config'.")
    print("Assicurati che il gioco sia eseguito dalla directory radice 'simai' e che 'game/config.py' esista.")
    sys.exit("Uscita a causa di fallimento import config in WorldManager.")

class WorldManager:
    """
    Gestisce la mappa del mondo di gioco, le sue dimensioni,
    i dati dei tile e le conversioni di coordinate.
    """
    def __init__(self):
        """
        Inizializza il WorldManager utilizzando le costanti da config.py.
        """
        self.world_tile_width = getattr(config, 'WORLD_TILE_WIDTH', 100)
        self.world_tile_height = getattr(config, 'WORLD_TILE_HEIGHT', 80)
        self.tile_size = getattr(config, 'TILE_SIZE', 32)
        
        self.world_pixel_width = self.world_tile_width * self.tile_size
        self.world_pixel_height = self.world_tile_height * self.tile_size

        # La mappa del mondo. Sarà una lista di liste (matrice) di ID di tile.
        self.map_data = []
        self._load_map_from_config() # Carica la mappa all'inizializzazione
        
        print(f"WorldManager inizializzato: Mondo {self.world_tile_width}x{self.world_tile_height} tiles, Tile Size: {self.tile_size}")
        print(f"Dimensioni mondo in pixel: {self.world_pixel_width}x{self.world_pixel_height}")

    def _load_map_from_config(self):
        """
        Carica i dati della mappa dalla costante TEMP_WORLD_MAP_DATA in config.py.
        """
        map_data_source = getattr(config, 'TEMP_WORLD_MAP_DATA', [])
        
        if not isinstance(map_data_source, list) or \
           not all(isinstance(row, list) for row in map_data_source) or \
           not map_data_source:
            print("ERRORE (WorldManager._load_map_from_config): config.TEMP_WORLD_MAP_DATA non è una lista di liste valida o è vuota.")
            # Crea una mappa vuota di default se i dati non sono validi
            self.map_data = [[getattr(config, 'DEFAULT_VOID_TILE_ID', -1) for _ in range(self.world_tile_width)] for _ in range(self.world_tile_height)]
            return

        # Verifica base delle dimensioni
        map_height_from_source = len(map_data_source)
        map_width_from_source = len(map_data_source[0]) if map_height_from_source > 0 else 0

        if map_height_from_source != self.world_tile_height or \
           map_width_from_source != self.world_tile_width:
            print(f"ATTENZIONE (WorldManager._load_map_from_config): Le dimensioni di TEMP_WORLD_MAP_DATA ({map_height_from_source}x{map_width_from_source}) "
                  f"non corrispondono alle dimensioni del mondo definite in config ({self.world_tile_height}x{self.world_tile_width}).")
            # Qui potresti decidere di troncare/riempire o sollevare un errore.
            # Per ora, la usiamo così com'è, ma questo potrebbe causare problemi se le dimensioni non corrispondono.
            # Per maggiore robustezza, si potrebbe forzare la mappa alle dimensioni definite:
            new_map_data = [[getattr(config, 'DEFAULT_VOID_TILE_ID', -1) for _ in range(self.world_tile_width)] for _ in range(self.world_tile_height)]
            for r in range(min(self.world_tile_height, map_height_from_source)):
                for c in range(min(self.world_tile_width, map_width_from_source)):
                    new_map_data[r][c] = map_data_source[r][c]
            self.map_data = new_map_data
            print(f"Mappa adattata alle dimensioni del mondo: {self.world_tile_height}x{self.world_tile_width}")
        else:
            self.map_data = map_data_source
            print(f"Mappa caricata da config in WorldManager. Dimensioni: {len(self.map_data)}x{len(self.map_data[0]) if self.map_data else 0} tiles.")

    def get_tile_id(self, world_tile_x, world_tile_y):
        """
        Restituisce l'ID del tile alle coordinate specificate del mondo (in tile).

        Args:
            world_tile_x (int): Coordinata X del tile nel mondo.
            world_tile_y (int): Coordinata Y del tile nel mondo.

        Returns:
            int: L'ID del tile, o un ID di default (es. per "vuoto" o "fuori mappa") se le coordinate sono non valide.
        """
        if 0 <= world_tile_y < self.world_tile_height and 0 <= world_tile_x < self.world_tile_width:
            # Assicurati che map_data e le sue righe non siano vuote prima di accedere
            if self.map_data and self.map_data[world_tile_y]:
                 return self.map_data[world_tile_y][world_tile_x]
            else:
                # Questo caso non dovrebbe accadere se _load_map_from_config gestisce bene le mappe vuote/malformate
                print(f"ERRORE (get_tile_id): map_data o riga map_data[{world_tile_y}] è vuota/non valida.")
                return getattr(config, 'DEFAULT_VOID_TILE_ID', -1)
        else:
            # Commentato per ridurre lo spam di log durante il normale gioco ai bordi
            # print(f"ATTENZIONE (get_tile_id): Coordinate ({world_tile_x}, {world_tile_y}) fuori dai limiti della mappa ({self.world_tile_width}x{self.world_tile_height}).")
            return getattr(config, 'DEFAULT_VOID_TILE_ID', -1) 

    def is_obstacle(self, world_tile_x, world_tile_y):
        """
        Controlla se il tile alle coordinate specificate del mondo è un ostacolo.
        Utilizza OBSTACLE_TILE_IDS da config.py.

        Args:
            world_tile_x (int): Coordinata X del tile nel mondo.
            world_tile_y (int): Coordinata Y del tile nel mondo.

        Returns:
            bool: True se il tile è un ostacolo, False altrimenti.
        """
        tile_id = self.get_tile_id(world_tile_x, world_tile_y)
        
        obstacle_ids = getattr(config, 'OBSTACLE_TILE_IDS', []) 
        if tile_id in obstacle_ids:
            return True
        return False

    def world_pixel_to_tile_coordinates(self, world_pixel_x, world_pixel_y):
        """
        Converte coordinate pixel del mondo in coordinate tile del mondo.

        Args:
            world_pixel_x (float): Coordinata X in pixel nel mondo.
            world_pixel_y (float): Coordinata Y in pixel nel mondo.

        Returns:
            tuple[int, int]: Coordinate (tile_x, tile_y) nel mondo.
        """
        if self.tile_size == 0: 
            print("ERRORE (world_pixel_to_tile_coordinates): tile_size è 0.")
            return (0,0) 
        tile_x = int(world_pixel_x // self.tile_size)
        tile_y = int(world_pixel_y // self.tile_size)
        return tile_x, tile_y

    def tile_to_world_pixel_topleft(self, world_tile_x, world_tile_y):
        """
        Converte coordinate tile del mondo nell'angolo in alto a sinistra (in pixel) di quel tile nel mondo.

        Args:
            world_tile_x (int): Coordinata X del tile nel mondo.
            world_tile_y (int): Coordinata Y del tile nel mondo.

        Returns:
            tuple[int, int]: Coordinate (pixel_x, pixel_y) dell'angolo in alto a sinistra del tile.
        """
        pixel_x = world_tile_x * self.tile_size
        pixel_y = world_tile_y * self.tile_size
        return pixel_x, pixel_y
        
    def tile_to_world_pixel_center(self, world_tile_x, world_tile_y):
        """
        Converte coordinate tile del mondo nel centro (in pixel) di quel tile nel mondo.

        Args:
            world_tile_x (int): Coordinata X del tile nel mondo.
            world_tile_y (int): Coordinata Y del tile nel mondo.

        Returns:
            tuple[float, float]: Coordinate (pixel_x, pixel_y) del centro del tile nel mondo.
        """
        pixel_x = world_tile_x * self.tile_size + self.tile_size / 2.0
        pixel_y = world_tile_y * self.tile_size + self.tile_size / 2.0
        return pixel_x, pixel_y

    def get_world_rect_pixels(self):
        """Restituisce un pygame.Rect che rappresenta l'intera dimensione del mondo in pixel."""
        return pygame.Rect(0, 0, self.world_pixel_width, self.world_pixel_height)

    def draw_map_portion(self, surface_to_draw_on, camera_world_rect, tile_images_dict=None):
        """
        Disegna la porzione della mappa del mondo che è visibile attraverso la camera.

        Args:
            surface_to_draw_on (pygame.Surface): La superficie su cui disegnare (es. lo schermo).
            camera_world_rect (pygame.Rect): Il rettangolo della camera in coordinate del mondo.
            tile_images_dict (dict, optional): Un dizionario che mappa gli ID dei tile alle loro Surface pygame.
                                          Es: {0: erba_img, 1: muro_img}. Defaults to None.
        """
        if not self.map_data:
            # print("ATTENZIONE (WorldManager.draw_map_portion): Nessun dato mappa da disegnare.")
            return

        # Determina quali tile del mondo sono visibili attraverso la camera
        start_world_tile_x, start_world_tile_y = self.world_pixel_to_tile_coordinates(camera_world_rect.left, camera_world_rect.top)
        # Per l'ultimo tile, considera il bordo destro/inferiore della camera
        end_world_tile_x, end_world_tile_y = self.world_pixel_to_tile_coordinates(camera_world_rect.right -1 , camera_world_rect.bottom -1)

        # Limita il disegno ai tile effettivamente esistenti nella mappa
        start_world_tile_x = max(0, start_world_tile_x)
        start_world_tile_y = max(0, start_world_tile_y)
        end_world_tile_x = min(self.world_tile_width - 1, end_world_tile_x)
        end_world_tile_y = min(self.world_tile_height - 1, end_world_tile_y)

        for world_ty in range(start_world_tile_y, end_world_tile_y + 1):
            for world_tx in range(start_world_tile_x, end_world_tile_x + 1):
                tile_id = self.get_tile_id(world_tx, world_ty)
                
                # Calcola la posizione di disegno sullo schermo:
                # coordinate del tile nel mondo * dimensione tile - offset della camera
                screen_draw_x = world_tx * self.tile_size - camera_world_rect.left
                screen_draw_y = world_ty * self.tile_size - camera_world_rect.top

                if tile_images_dict and tile_id in tile_images_dict and tile_images_dict[tile_id] is not None:
                    surface_to_draw_on.blit(tile_images_dict[tile_id], (screen_draw_x, screen_draw_y))
                else:
                    # Fallback: disegna un colore di base se l'immagine non è disponibile
                    tile_color_map = getattr(config, 'TILE_COLORS', {})
                    default_color = getattr(config, 'DEFAULT_TILE_COLOR', (128, 128, 128))
                    color_to_draw = tile_color_map.get(tile_id, default_color)
                    pygame.draw.rect(surface_to_draw_on, color_to_draw, 
                                     (screen_draw_x, screen_draw_y, self.tile_size, self.tile_size))

    def draw_world_grid_on_surface(self, surface_to_draw_on, camera_world_rect):
        """
        Disegna una griglia di debug per la porzione visibile del mondo.

        Args:
            surface_to_draw_on (pygame.Surface): La superficie su cui disegnare.
            camera_world_rect (pygame.Rect): Il rettangolo della camera in coordinate del mondo.
        """
        start_world_tile_x, start_world_tile_y = self.world_pixel_to_tile_coordinates(camera_world_rect.left, camera_world_rect.top)
        end_world_tile_x, end_world_tile_y = self.world_pixel_to_tile_coordinates(camera_world_rect.right -1, camera_world_rect.bottom -1)

        start_world_tile_x = max(0, start_world_tile_x)
        start_world_tile_y = max(0, start_world_tile_y)
        end_world_tile_x = min(self.world_tile_width - 1, end_world_tile_x)
        end_world_tile_y = min(self.world_tile_height - 1, end_world_tile_y)
        
        grid_line_color = getattr(config, 'DEBUG_GRID_COLOR_WALKABLE', (60,60,60))

        for world_ty in range(start_world_tile_y, end_world_tile_y + 1):
            for world_tx in range(start_world_tile_x, end_world_tile_x + 1):
                screen_draw_x = world_tx * self.tile_size - camera_world_rect.left
                screen_draw_y = world_ty * self.tile_size - camera_world_rect.top
                
                tile_rect_on_screen = pygame.Rect(screen_draw_x, screen_draw_y, self.tile_size, self.tile_size)
                pygame.draw.rect(surface_to_draw_on, grid_line_color, tile_rect_on_screen, 1)


if __name__ == '__main__':
    # Esempio di utilizzo e test del WorldManager
    pygame.init()
    
    # Usa le dimensioni dello schermo da config per il test
    screen_width_test = getattr(config, 'SCREEN_WIDTH', 800)
    screen_height_test = getattr(config, 'SCREEN_HEIGHT', 600)
    
    screen_test = pygame.display.set_mode((screen_width_test, screen_height_test))
    pygame.display.set_caption("Test WorldManager Avanzato")

    # Crea un'istanza di WorldManager (ora non prende argomenti, legge da config)
    world_manager_instance = WorldManager()

    # La mappa è già caricata da config.TEMP_WORLD_MAP_DATA all'interno di __init__
    # world_manager_instance.load_map(config.TEMP_WORLD_MAP_DATA) # Non più necessario chiamarlo esplicitamente

    # Camera: Inizia in alto a sinistra del mondo
    camera_test_rect = pygame.Rect(0, 0, screen_width_test, screen_height_test)
    
    running_test = True
    clock_test = pygame.time.Clock()

    print("\n--- Inizio Test WorldManager Avanzato ---")
    print(f"Tile (0,0) ID: {world_manager_instance.get_tile_id(0,0)}, Ostacolo: {world_manager_instance.is_obstacle(0,0)}")
    print(f"Tile (11,11) ID (acqua): {world_manager_instance.get_tile_id(11,11)}, Ostacolo: {world_manager_instance.is_obstacle(11,11)}")
    print(f"Tile (21,31) ID (sabbia): {world_manager_instance.get_tile_id(21,31)}, Ostacolo: {world_manager_instance.is_obstacle(21,31)}")
    print(f"Tile (fuori mappa {config.WORLD_TILE_WIDTH + 5},{config.WORLD_TILE_HEIGHT + 5}) ID: {world_manager_instance.get_tile_id(config.WORLD_TILE_WIDTH + 5, config.WORLD_TILE_HEIGHT + 5)}, Ostacolo: {world_manager_instance.is_obstacle(config.WORLD_TILE_WIDTH + 5, config.WORLD_TILE_HEIGHT + 5)}")
    
    px, py = world_manager_instance.tile_to_world_pixel_center(1,1)
    print(f"Centro del tile (1,1) del mondo in pixel: ({px}, {py})")
    tx, ty = world_manager_instance.world_pixel_to_tile_coordinates(px, py)
    print(f"Pixel ({px}, {py}) riconvertiti a tile del mondo: ({tx}, {ty})")
    print("--------------------------------------")

    show_debug_grid = True

    while running_test:
        dt = clock_test.tick(getattr(config, 'FPS', 60)) / 1000.0 # Delta time in secondi

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running_test = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_g: # Toggle griglia di debug
                    show_debug_grid = not show_debug_grid

        # Movimento camera per test (usa config.CAMERA_SPEED)
        keys = pygame.key.get_pressed()
        cam_speed_val = getattr(config, 'CAMERA_SPEED', 300) * dt
        if keys[pygame.K_LEFT]: camera_test_rect.x -= cam_speed_val
        if keys[pygame.K_RIGHT]: camera_test_rect.x += cam_speed_val
        if keys[pygame.K_UP]: camera_test_rect.y -= cam_speed_val
        if keys[pygame.K_DOWN]: camera_test_rect.y += cam_speed_val
        
        # Limita il movimento della camera ai bordi del mondo
        camera_test_rect.left = max(0, camera_test_rect.left)
        camera_test_rect.top = max(0, camera_test_rect.top)
        camera_test_rect.right = min(world_manager_instance.world_pixel_width, camera_test_rect.right)
        camera_test_rect.bottom = min(world_manager_instance.world_pixel_height, camera_test_rect.bottom)

        screen_test.fill((30,30,30)) # Sfondo scuro per il test
        
        # Disegna la porzione di mappa visibile
        world_manager_instance.draw_map_portion(screen_test, camera_test_rect) 
        
        if show_debug_grid:
            world_manager_instance.draw_world_grid_on_surface(screen_test, camera_test_rect)

        pygame.display.flip()

    pygame.quit()
    print("--- Fine Test WorldManager Avanzato ---")
