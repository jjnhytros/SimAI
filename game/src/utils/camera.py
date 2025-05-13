# simai/game/src/utils/camera.py (o simai/game/src/camera.py)
import pygame

try:
    # Tentativo di importare config dal package 'game'
    from game import config
except ImportError:
    print("ERRORE CRITICO (Camera): Impossibile importare 'game.config'.")
    import sys
    sys.exit("Uscita a causa di fallimento import config in Camera.")

class Camera:
    """
    Gestisce la visuale (camera) sul mondo di gioco.
    Determina quale porzione del mondo è visibile sullo schermo.
    """
    def __init__(self, screen_width, screen_height, world_pixel_width, world_pixel_height):
        """
        Inizializza la Camera.

        Args:
            screen_width (int): Larghezza dello schermo/finestra di gioco in pixel.
            screen_height (int): Altezza dello schermo/finestra di gioco in pixel.
            world_pixel_width (int): Larghezza totale del mondo di gioco in pixel.
            world_pixel_height (int): Altezza totale del mondo di gioco in pixel.
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.world_pixel_width = world_pixel_width
        self.world_pixel_height = world_pixel_height
        
        # Il camera_rect rappresenta la porzione del MONDO attualmente visibile.
        # Le sue coordinate (topleft) sono in coordinate del MONDO.
        # Le sue dimensioni (width, height) sono quelle dello schermo.
        self.camera_rect = pygame.Rect(0, 0, self.screen_width, self.screen_height)
        
        self.target_entity = None # Opzionale: per far seguire la camera a un'entità

        print(f"Camera inizializzata: Schermo {self.screen_width}x{self.screen_height}, Mondo {self.world_pixel_width}x{self.world_pixel_height}")

    def set_target(self, entity):
        """
        Imposta un'entità che la camera deve seguire.
        L'entità deve avere attributi 'x' e 'y' (coordinate del mondo).
        """
        self.target_entity = entity

    def update(self):
        """
        Aggiorna la posizione della camera.
        Se un target è impostato, la camera cercherà di centrarlo.
        Altrimenti, la camera può essere mossa manualmente (non implementato qui, ma in main.py).
        """
        if self.target_entity:
            # Centra la camera sul target, mantenendo le coordinate in termini di mondo
            target_world_x = self.target_entity.x
            target_world_y = self.target_entity.y
            
            # Calcola la posizione in alto a sinistra della camera per centrare il target
            new_cam_x = target_world_x - self.screen_width / 2
            new_cam_y = target_world_y - self.screen_height / 2
            
            self.camera_rect.topleft = (new_cam_x, new_cam_y)
        
        # Assicura che la camera non esca dai bordi del mondo
        self.camera_rect.left = max(0, self.camera_rect.left)
        self.camera_rect.top = max(0, self.camera_rect.top)
        self.camera_rect.right = min(self.world_pixel_width, self.camera_rect.right)
        self.camera_rect.bottom = min(self.world_pixel_height, self.camera_rect.bottom)

        # Se il mondo è più piccolo dello schermo in una dimensione, centra la camera in quella dimensione
        if self.world_pixel_width < self.screen_width:
            self.camera_rect.left = (self.world_pixel_width - self.screen_width) // 2
        if self.world_pixel_height < self.screen_height:
            self.camera_rect.top = (self.world_pixel_height - self.screen_height) // 2


    def apply_to_rect(self, world_rect):
        """
        Applica la trasformazione della camera a un pygame.Rect dato in coordinate del mondo.
        Restituisce un nuovo Rect in coordinate dello schermo.

        Args:
            world_rect (pygame.Rect): Il rettangolo nelle coordinate del mondo.

        Returns:
            pygame.Rect: Il rettangolo trasformato in coordinate dello schermo.
        """
        screen_x = world_rect.left - self.camera_rect.left
        screen_y = world_rect.top - self.camera_rect.top
        return pygame.Rect(screen_x, screen_y, world_rect.width, world_rect.height)

    def apply_to_point(self, world_x, world_y):
        """
        Applica la trasformazione della camera a un punto dato in coordinate del mondo.
        Restituisce le coordinate del punto sullo schermo.

        Args:
            world_x (float): Coordinata X del punto nel mondo.
            world_y (float): Coordinata Y del punto nel mondo.

        Returns:
            tuple[float, float]: Coordinate (screen_x, screen_y) del punto sullo schermo.
        """
        screen_x = world_x - self.camera_rect.left
        screen_y = world_y - self.camera_rect.top
        return screen_x, screen_y

    def get_world_coordinates_from_screen(self, screen_x, screen_y):
        """
        Converte le coordinate dello schermo in coordinate del mondo.
        Utile per il input del mouse.

        Args:
            screen_x (int): Coordinata X sullo schermo.
            screen_y (int): Coordinata Y sullo schermo.

        Returns:
            tuple[int, int]: Coordinate (world_x, world_y) nel mondo.
        """
        world_x = screen_x + self.camera_rect.left
        world_y = screen_y + self.camera_rect.top
        return world_x, world_y

if __name__ == '__main__':
    # Esempio di utilizzo della Camera
    pygame.init()
    
    # Assicurati che config.py sia accessibile e abbia questi valori per il test
    config.SCREEN_WIDTH = 800
    config.SCREEN_HEIGHT = 600
    config.WORLD_TILE_WIDTH = 50  # Mondo di 50x40 tiles
    config.WORLD_TILE_HEIGHT = 40
    config.TILE_SIZE = 32
    config.CAMERA_SPEED = 300 # Per il test di movimento manuale

    screen_test = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption("Test Camera")

    # Calcola le dimensioni del mondo in pixel
    world_px_w = config.WORLD_TILE_WIDTH * config.TILE_SIZE
    world_px_h = config.WORLD_TILE_HEIGHT * config.TILE_SIZE

    game_camera = Camera(config.SCREEN_WIDTH, config.SCREEN_HEIGHT, world_px_w, world_px_h)

    # Oggetto di test da seguire (simula un personaggio)
    class TestEntity:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.rect = pygame.Rect(x - 10, y - 10, 20, 20) # Rect in coordinate del mondo
            self.color = (255, 0, 0)
        
        def update_position(self, dx, dy, world_w, world_h):
            self.x += dx
            self.y += dy
            # Limita l'entità ai bordi del mondo
            self.x = max(10, min(self.x, world_w - 10))
            self.y = max(10, min(self.y, world_h - 10))
            self.rect.center = (self.x, self.y)

    player_entity = TestEntity(world_px_w / 2, world_px_h / 2)
    game_camera.set_target(player_entity) # La camera seguirà questa entità

    running_test = True
    clock_test = pygame.time.Clock()

    print("\n--- Inizio Test Camera ---")
    print(f"Camera Rect iniziale (coordinate mondo): {game_camera.camera_rect}")
    print(f"Posizione iniziale entità (mondo): ({player_entity.x}, {player_entity.y})")

    while running_test:
        dt = clock_test.tick(config.FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running_test = False
        
        keys = pygame.key.get_pressed()
        player_dx, player_dy = 0, 0
        player_speed = 150 * dt # pixel al secondo
        if keys[pygame.K_a]: player_dx -= player_speed
        if keys[pygame.K_d]: player_dx += player_speed
        if keys[pygame.K_w]: player_dy -= player_speed
        if keys[pygame.K_s]: player_dy += player_speed
        
        player_entity.update_position(player_dx, player_dy, world_px_w, world_px_h)
        game_camera.update() # Aggiorna la camera per seguire il target

        screen_test.fill((50, 50, 50)) # Sfondo per il test

        # Disegna un "mondo" fittizio (griglia di linee) per vedere lo scrolling
        # Le linee sono disegnate in coordinate del mondo, poi trasformate dalla camera
        line_color = (80, 80, 80)
        for x_line in range(0, world_px_w, config.TILE_SIZE * 2):
            start_screen_pos = game_camera.apply_to_point(x_line, 0)
            end_screen_pos = game_camera.apply_to_point(x_line, world_px_h)
            pygame.draw.line(screen_test, line_color, start_screen_pos, end_screen_pos, 1)
        for y_line in range(0, world_px_h, config.TILE_SIZE * 2):
            start_screen_pos = game_camera.apply_to_point(0, y_line)
            end_screen_pos = game_camera.apply_to_point(world_px_w, y_line)
            pygame.draw.line(screen_test, line_color, start_screen_pos, end_screen_pos, 1)

        # Disegna l'entità usando le coordinate trasformate dalla camera
        entity_screen_rect = game_camera.apply_to_rect(player_entity.rect)
        pygame.draw.rect(screen_test, player_entity.color, entity_screen_rect)
        
        # Stampa info debug
        font_debug = pygame.font.SysFont("arial", 18)
        cam_text = f"Camera (World): TL({game_camera.camera_rect.left:.0f}, {game_camera.camera_rect.top:.0f}) BR({game_camera.camera_rect.right:.0f}, {game_camera.camera_rect.bottom:.0f})"
        ent_text = f"Entity (World): ({player_entity.x:.0f}, {player_entity.y:.0f})"
        ent_screen_text = f"Entity (Screen): ({entity_screen_rect.centerx:.0f}, {entity_screen_rect.centery:.0f})"
        
        screen_test.blit(font_debug.render(cam_text, True, (255,255,255)), (10,10))
        screen_test.blit(font_debug.render(ent_text, True, (255,255,255)), (10,30))
        screen_test.blit(font_debug.render(ent_screen_text, True, (255,255,255)), (10,50))

        pygame.display.flip()

    pygame.quit()
    print("--- Fine Test Camera ---")

