# test_pygame_gui.py
import pygame
import pygame_gui

pygame.init()
screen = pygame.display.set_mode((800, 600))
manager = pygame_gui.UIManager((800, 600))

try:
    panel = pygame_gui.elements.UIPanel(
        relative_rect=pygame.Rect(10, 10, 200, 200),
        layer_starting_height=0, # Test con questo
        manager=manager
    )
    print("UIPanel creato con successo usando 'layer_starting_height'")
except TypeError as e_layer:
    print(f"Errore con 'layer_starting_height': {e_layer}")
    try:
        panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(10, 10, 200, 200),
            starting_layer_height=0, # Test con questo
            manager=manager
        )
        print("UIPanel creato con successo usando 'starting_layer_height'")
    except TypeError as e_starting:
        print(f"Errore anche con 'starting_layer_height': {e_starting}")

pygame.quit()